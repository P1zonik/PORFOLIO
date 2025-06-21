from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import os, requests

from extensions import db   # ← берём db из отдельного файла

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# подключаем SQLAlchemy к приложению
db.init_app(app)

# импортируем модели ТОЛЬКО после init_app
with app.app_context():
    from models import Message, BlogPost   # теперь цикла нет
    db.create_all()                        # создаём таблицы, если нужно


# ────────────────────────── утилиты ──────────────────────────
def optimize_image(input_path, output_path,
                   max_size=(1920, 1080), quality=80):
    """Сжать картинку без заметной потери качества."""
    with Image.open(input_path) as img:
        img.thumbnail(max_size)
        img.save(output_path, optimize=True, quality=quality)


# ────────────────────────── маршруты ──────────────────────────
@app.route('/')
def index():
    design = os.listdir('static/portfolio/design')[:3]
    return render_template('index.html', design=design)



@app.route('/portfolio')
def portfolio():
    design = os.listdir('static/portfolio/design')
    photo  = os.listdir('static/portfolio/photo')
    return render_template('portfolio.html', design=design, photo=photo)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/reviews')
def reviews():
    return render_template('reviews.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # ─── CAPTCHA ───
        recaptcha_response = request.form.get('g-recaptcha-response')
        payload = {
            'secret': app.config['RECAPTCHA_SECRET_KEY'],
            'response': recaptcha_response
        }
        r = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=payload
        )
        result = r.json()
        if not result.get('success'):
            return render_template('contact.html', error='Ошибка CAPTCHA. Попробуйте ещё раз.')

        # ─── сохраняем сообщение ───
        message = Message(
            name=request.form['name'],
            email=request.form['email'],
            content=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        return render_template('contact.html', success=True)

    return render_template('contact.html')
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    category = request.form.get('category', 'design')

    if not file:
        return "Файл не найден", 400

    filename = secure_filename(file.filename)
    save_dir = os.path.join(app.config['UPLOAD_FOLDER'], category)
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, filename)
    file.save(save_path)

    # оптимизируем изображение
    optimized_path = os.path.join(save_dir, f'opt_{filename}')
    optimize_image(save_path, optimized_path)
    os.replace(optimized_path, save_path)

    return redirect(url_for('portfolio'))


@app.route('/api/portfolio')
def api_portfolio():
    files = {
        "design": os.listdir('static/portfolio/design'),
        "photo": os.listdir('static/portfolio/photo')
    }
    return jsonify(files)


if __name__ == '__main__':
    app.run(debug=True)
