from flask import Flask, render_template, request, send_file, redirect, url_for
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def generate_key(image_shape, seed=None):
    if seed:
        np.random.seed(seed)
    return np.random.randint(0, 256, image_shape, dtype=np.uint8)

def convert_to_png(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    png_image_path = os.path.splitext(image_path)[0] + ".png"
    cv2.imwrite(png_image_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return png_image_path

def encode_image(image_path, key_path, output_path):
    png_image_path = convert_to_png(image_path)
    image = cv2.imread(png_image_path, cv2.IMREAD_UNCHANGED)
    key = generate_key(image.shape)
    encoded_image = cv2.bitwise_xor(image, key)
    cv2.imwrite(output_path, encoded_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    np.save(key_path, key)

def decode_image(encoded_image_path, key_path, output_path):
    encoded_image = cv2.imread(encoded_image_path, cv2.IMREAD_UNCHANGED)
    key = np.load(key_path)
    decoded_image = cv2.bitwise_xor(encoded_image, key)
    cv2.imwrite(output_path, decoded_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        image_file = request.files['image']
        if image_file:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
            image_file.save(image_path)
            
            key_path = os.path.join(app.config['UPLOAD_FOLDER'], 'key.npy')
            encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_image.png')
            
            encode_image(image_path, key_path, encoded_image_path)
            
            # Provide both encoded image and key files for download
            return render_template('encode.html', encoded_image_path=encoded_image_path, key_path=key_path)
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        encoded_image_file = request.files['encoded_image']
        key_file = request.files['key']
        if encoded_image_file and key_file:
            encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(encoded_image_file.filename))
            key_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(key_file.filename))
            decoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'decoded_image.png')
            
            encoded_image_file.save(encoded_image_path)
            key_file.save(key_path)
            
            decode_image(encoded_image_path, key_path, decoded_image_path)
            
            return send_file(decoded_image_path, as_attachment=True)
    return render_template('decode.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)
@app.route('/careers')
def careers():
    return render_template('careers.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/guide')
def guide():
    return render_template('guide.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/help')
def help():
    return render_template('help.html')



if __name__ == '__main__':
    app.run(debug=True)

