from extensions import db
from sqlalchemy.dialects.sqlite import DATETIME
from datetime import datetime

class ImageUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    temp_file_path = db.Column(db.String(255), nullable=False)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    caption = db.Column(db.Text, nullable=True)
    created_at = db.Column(DATETIME, default=datetime.utcnow)