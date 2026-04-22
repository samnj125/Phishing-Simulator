import os


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = os.environ.get('BASE_URL') or 'http://127.0.0.1:5000'
