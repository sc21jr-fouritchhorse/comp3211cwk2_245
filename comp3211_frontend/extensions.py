from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

db = SQLAlchemy()
celery = Celery('tasks', broker='redis://localhost:6379/0')
celery.conf.result_backend = 'redis://localhost:6379/0'

session_factory = sessionmaker()
Session = scoped_session(session_factory)