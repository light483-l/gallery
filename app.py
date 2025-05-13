from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['BASE_IMAGES'] = ['base_images/mars1.jpg', 'base_images/mars2.jpg']  # Обязательные базовые изображения
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['IMAGE_SIZE'] = (800, 600)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize(app.config['IMAGE_SIZE'])
        img.save(image_path)
        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    base_images = []
    for img_path in app.config['BASE_IMAGES']:
        full_path = os.path.join('static', img_path)
        if os.path.exists(full_path):
            base_images.append(img_path)
        else:
            print(f"Warning: Base image not found - {full_path}")

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Допустимые форматы: JPG, PNG, GIF')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(save_path)
            if not process_image(save_path):
                os.remove(save_path)
                flash('Ошибка обработки изображения')
            return redirect(url_for('gallery'))
        except:
            flash('Ошибка при загрузке файла')

    images = base_images.copy()

    upload_dir = app.config['UPLOAD_FOLDER']
    if os.path.exists(upload_dir):
        for filename in os.listdir(upload_dir):
            if allowed_file(filename):
                images.append(f'uploads/{filename}')

    return render_template('gallery.html', images=images)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)