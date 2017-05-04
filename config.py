
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or \
    "my born day is 111111111"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = "[Flask forum]"
    FLASKY_MAIL_SENDER = "Flask Forum Admin<544648788@qq.com>"
    FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/test_db"
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/testing_db"
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/product_db"
    
config = {
    "development": DevelopmentConfig,
    "testing" : TestingConfig,
    "production" : ProductionConfig,
 
    "default" : DevelopmentConfig
}
    
    
    
    
    
    
    
    
    
    
    
    
    
    