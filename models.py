from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Letter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    password = db.Column(db.String(100), nullable=False)  # 이 줄을 추가
