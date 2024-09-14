from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from celery_tasks import process_document, process_multiple_documents, process_file
from werkzeug.utils import secure_filename
from user_management import db, User
import os
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from logging.handlers import RotatingFileHandler
import bleach
from prometheus_client import Counter, Histogram
from prometheus_flask_exporter import PrometheusMetrics
from config.config import config

request_count = Counter('http_requests_total', 'Total HTTP Requests')
request_latency = Histogram('http_request_duration_seconds', 'HTTP Request Duration')

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'html'}

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/files')
@login_required
def list_files():
    user_files = os.listdir(os.path.join(app.config['OUTPUT_FOLDER'], str(current_user.id)))
    return render_template('files.html', files=user_files)

@app.route('/delete/<filename>')
@login_required
def delete_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], str(current_user.id), filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'File {filename} has been deleted.')
    else:
        flash(f'File {filename} not found.')
    return redirect(url_for('list_files'))

@app.route('/process', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
@request_count.count_exceptions()
@request_latency.time()
def process():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    processed_files = []
    for file in files:
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                sanitized_filename = bleach.clean(filename)
                user_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
                os.makedirs(user_upload_folder, exist_ok=True)
                file_path = os.path.join(user_upload_folder, sanitized_filename)
                file.save(file_path)
                
                user_output_folder = os.path.join(app.config['OUTPUT_FOLDER'], str(current_user.id))
                os.makedirs(user_output_folder, exist_ok=True)
                output_dir = os.path.join(user_output_folder, os.path.splitext(filename)[0])
                os.makedirs(output_dir, exist_ok=True)
                
                processed_files.append((file_path, output_dir))
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                return jsonify({'error': f'An error occurred while processing the file {filename}'}), 500
        else:
            return jsonify({'error': f'File type not allowed: {file.filename}'}), 400
    
    task = process_multiple_documents.delay(processed_files)
    return jsonify({'task_id': task.id}), 202

@app.route('/status/<task_id>')
@login_required
def status(task_id):
    task = process_multiple_documents.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.route('/download/<task_id>')
@login_required
def download(task_id):
    task = process_multiple_documents.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        # Assuming the last file in the list is the final merged PDF
        output_path = task.result[-1].get('output_pdf_path')
        if output_path and os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({'error': 'Output file not found'}), 404
    else:
        return jsonify({'error': 'Task not completed'}), 400

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        # Trigger Celery task for processing
        task = process_file.delay(file_path)
        return jsonify({'message': 'File uploaded successfully', 'task_id': task.id}), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/task/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    task = process_file.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    return jsonify(response)

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('Not found: %s', (request.path))
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Server Error: %s', (error))
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)