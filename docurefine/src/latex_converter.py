from transformers import T5ForConditionalGeneration, T5Tokenizer
import matplotlib.pyplot as plt
import io
from PIL import Image
import numpy as np
import subprocess
import logging

model = None
tokenizer = None

def load_model():
    global model, tokenizer
    if model is None or tokenizer is None:
        model = T5ForConditionalGeneration.from_pretrained("t5-base")
        tokenizer = T5Tokenizer.from_pretrained("t5-base")

def text_to_latex(text):
    """
    Convert plain text to LaTeX using a pre-trained model.
    
    :param text: Input text to convert
    :return: LaTeX representation of the input text
    """
    load_model()
    
    input_text = f"translate English to LaTeX: {text}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    
    outputs = model.generate(input_ids, max_length=512, num_return_sequences=1)
    latex_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return latex_output

def convert_layout_to_latex(merged_layout):
    """
    Convert merged layout information to LaTeX.
    
    :param merged_layout: Merged layout information from OCR and layout analysis
    :return: LaTeX representation of the document
    """
    latex_output = []
    
    for element in merged_layout:
        if element['type'] == 'Title':
            latex_output.append(f"\\section{{{element['text']}}}")
        elif element['type'] == 'Text':
            latex_output.append(text_to_latex(element['text']))
        elif element['type'] == 'List':
            latex_output.append("\\begin{itemize}")
            for item in element['text'].split('\n'):
                latex_output.append(f"\\item {text_to_latex(item)}")
            latex_output.append("\\end{itemize}")
        elif element['type'] == 'Figure':
            # Placeholder for figure handling
            latex_output.append("\\begin{figure}[h]\n\\centering\n\\includegraphics[width=0.8\\textwidth]{placeholder.png}\n\\caption{Figure caption}\n\\end{figure}")
    
    return '\n\n'.join(latex_output)

def render_latex(latex_code, output_path):
    with open('temp.tex', 'w') as f:
        f.write(latex_code)
    
    try:
        subprocess.run(['pdflatex', '-interaction=nonstopmode', 'temp.tex'], check=True)
        subprocess.run(['mv', 'temp.pdf', output_path], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"LaTeX rendering failed: {e}")
        raise
    finally:
        subprocess.run(['rm', 'temp.tex', 'temp.aux', 'temp.log'], check=False)

def latex_to_image(latex_content):
    """
    Convert LaTeX content to a numpy array image.
    
    :param latex_content: LaTeX content to render
    :return: Numpy array representing the rendered image
    """
    fig = plt.figure(figsize=(8.5, 11))  # Standard letter size
    plt.axis('off')
    plt.text(0.5, 0.5, f'${latex_content}$', size=12, ha='center', va='center', wrap=True)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    
    buf.seek(0)
    img = Image.open(buf)
    return np.array(img)