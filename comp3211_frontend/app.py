import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired
from extensions import db
from models import ImageUpload


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accessible_thumbnailer.db'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    class ImageUploadForm(FlaskForm):
        name = StringField('Name', validators=[DataRequired()])
        image = FileField('Image', validators=[DataRequired()])

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = ImageUploadForm()
        
        image_uploads = ImageUpload.query.all()
        
        if form.validate_on_submit():
            uploaded_file = form.image.data
            filename = secure_filename(uploaded_file.filename)
            temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(temp_file_path)
            
            image_upload = ImageUpload(
                name=form.name.data,
                temp_file_path=temp_file_path
            )
            db.session.add(image_upload)
            db.session.commit()
            
            from tasks import process_image_upload
            process_image_upload.delay(image_upload.id)
            
            return redirect('/')
        
        return render_template('index.html', form=form, image_uploads=image_uploads)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
