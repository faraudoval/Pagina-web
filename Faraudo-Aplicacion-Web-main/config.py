import os

SECRET_KEY = "GDtfDCFYjD" 
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+ os.path.abspath(os.getcwd()) +'/datos.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False