import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from steganography import encode_image, decode_image, encode_file, decode_file

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = './uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files or request.files['image'].filename == '':
        flash('No image file selected.')
        return redirect(request.url)

    file = request.files['image']
    action = request.form['action']

    if action == 'text':
        message = request.form['message']
        if not message:
            flash('No message provided.')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + filename + '.png')
        try:
            encode_image(filepath, message, output_image_path)
            flash('Message encoded successfully!')
            return send_from_directory(app.config['UPLOAD_FOLDER'], 'encoded_' + filename + '.png')
        except Exception as e:
            flash(f'Error encoding message: {e}')
            return redirect(request.url)

    elif action == 'file':
        if 'file' not in request.files or request.files['file'].filename == '':
            flash('No file selected for encoding.')
            return redirect(request.url)

        data_file = request.files['file']
        data_filename = secure_filename(data_file.filename)
        data_filepath = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        data_file.save(data_filepath)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + filename + '.png')
        try:
            encode_file(filepath, data_filepath, output_image_path)
            flash('File encoded successfully!')
            return send_from_directory(app.config['UPLOAD_FOLDER'], 'encoded_' + filename + '.png')
        except Exception as e:
            flash(f'Error encoding file: {e}')
            return redirect(request.url)

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files or request.files['image'].filename == '':
        flash('No image file selected for decoding.')
        return redirect(request.url)

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    action = request.form['action']

    if action == 'text':
        try:
            message = decode_image(filepath)
            if message:
                flash(f'Message found: {message}')
            else:
                flash('No hidden message found.')
        except Exception as e:
            flash(f'Error decoding message: {e}')
        return redirect(url_for('index'))

    elif action == 'file':
        output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decoded_file')
        try:
            decode_file(filepath, output_file_path)
            flash('File decoded successfully!')
            return send_from_directory(app.config['UPLOAD_FOLDER'], 'decoded_file')
        except Exception as e:
            flash(f'Error decoding file: {e}')
            return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
