let files = [];

function handleFiles(newFiles) {
    files = [...files, ...Array.from(newFiles)];
    updateFileList();
    updateStartButton();
}

function updateFileList() {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';
    files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span class="file-name">${file.name}</span>
            <span class="remove-file" onclick="removeFile(${index})">×</span>
        `;
        fileList.appendChild(fileItem);
    });
}

function removeFile(index) {
    files.splice(index, 1);
    updateFileList();
    updateStartButton();
}

function updateStartButton() {
    const startButton = document.getElementById('start-button');
    startButton.disabled = files.length === 0;
}

function uploadFiles() {
    const formData = new FormData();
    files.forEach(file => formData.append('files[]', file));

    const progressBar = document.getElementById('progress-bar');
    const progressBarContainer = document.getElementById('progress-bar-container');
    progressBarContainer.style.display = 'block';

    $.ajax({
        url: '/process',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        xhr: function() {
            const xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressBar.style.width = percent + '%';
                }
            }, false);
            return xhr;
        },
        success: function(data) {
            checkStatus(data.task_id);
        },
        error: function() {
            alert('An error occurred while processing the files.');
            progressBarContainer.style.display = 'none';
        }
    });
}

function checkStatus(taskId) {
    $.get('/status/' + taskId, function(data) {
        const progressBar = document.getElementById('progress-bar');
        if (data.state === 'SUCCESS') {
            progressBar.style.width = '100%';
            alert('Processing complete! You can now download the result.');
            window.location.href = '/download/' + taskId;
        } else if (data.state === 'FAILURE') {
            alert('An error occurred during processing.');
        } else {
            setTimeout(function() {
                checkStatus(taskId);
            }, 1000);
        }
    });
}

// Set up the drag and drop listeners
const dropArea = document.getElementById('drop-area');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    dropArea.classList.add('highlight');
}

function unhighlight(e) {
    dropArea.classList.remove('highlight');
}

dropArea.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const newFiles = dt.files;
    handleFiles(newFiles);
}

// Set up the file input listener
const fileElem = document.getElementById('fileElem');
fileElem.addEventListener('change', function() {
    handleFiles(this.files);
});

// Set up the drop area click listener
dropArea.addEventListener('click', function() {
    fileElem.click();
});

// Set up the start button listener
const startButton = document.getElementById('start-button');
startButton.addEventListener('click', uploadFiles);