import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY').encode()
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT= 587
    MAIL_USE_TLS = True
    MAIL_USERNAME= os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
