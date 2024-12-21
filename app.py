from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import Letter, db
import os
import logging
from flask_migrate import Migrate

app = Flask(__name__, static_folder='static')
app.config.from_object('config.Config')

db.init_app(app)

migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/letter_list')
def letter_list():
    letters = Letter.query.order_by(Letter.date.desc()).all()
    return render_template('letter_list.html', letters=letters)

@app.route('/write', methods=['GET', 'POST'])
def write_letter():
    if request.method == 'POST':
        name = request.form['name']
        content = request.form['content']
        password = request.form['password']  # 비밀번호 필드 추가
        image = request.files['image']

        if image and image.filename and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join('uploads', filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(full_path)
            logging.info(f"Image saved at: {full_path}")
            logging.info(f"Image path stored in database: {image_path}")
        else:
            image_path = None
            logging.info("No image uploaded or invalid file type")

        new_letter = Letter(name=name, content=content, image=image_path, password=password)
        db.session.add(new_letter)
        db.session.commit()

        flash('편지가 성공적으로 저장되었습니다!', 'success')
        return redirect(url_for('index'))

    return render_template('write_letter.html')

@app.route('/delete/<int:letter_id>', methods=['POST'])
def delete_letter(letter_id):
    letter = Letter.query.get(letter_id)
    if letter:
        password = request.form['password']  # 비밀번호 확인
        if password == letter.password:
            db.session.delete(letter)
            db.session.commit()
            flash('편지가 성공적으로 삭제되었습니다!', 'success')
        else:
            flash('비밀번호가 일치하지 않습니다.', 'error')
    else:
        flash('편지를 찾을 수 없습니다.', 'error')
    return redirect(url_for('letter_list'))

@app.route('/edit/<int:letter_id>', methods=['GET', 'POST'])
def edit_letter(letter_id):
    letter = Letter.query.get(letter_id)

    if request.method == 'POST':
        password = request.form['password']  # 비밀번호 확인
        if password == letter.password:
            letter.name = request.form['name']
            letter.content = request.form['content']

            if request.files.get('image'):
                image = request.files['image']
                if allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(full_path)
                    letter.image = filename

            db.session.commit()
            flash('편지가 성공적으로 편집되었습니다!', 'success')
        else:
            flash('비밀번호가 일치하지 않습니다.', 'error')
        return redirect(url_for('letter_list'))

    return render_template('edit_letter.html', letter=letter)

if __name__ == '__main__':
    app.run(debug=True)