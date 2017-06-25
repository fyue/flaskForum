
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or \
    "my born day is 111111111"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SSL_DISABLE = True
    MAIL_SERVER = "smtp.qq.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    FLASKY_MAIL_SUBJECT_PREFIX = "[Flask forum]"
    FLASKY_MAIL_SENDER = "Flask Forum Admin<544648788@qq.com>"
    FLASKY_ADMIN = os.environ.get("FLASKY_ADMIN")
    FLASKY_POSTS_PER_PAGE = os.environ.get("FLASKY_POSTS_PER_PAGE") or 25
    FLASKY_FOLLOWERS_PER_PAGE = os.environ.get("FLASKY_FOLLOWERS_PER_PAGE") or 50
    FLASKY_COMMENTS_PER_PAGE = 30
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    
    @staticmethod
    def init_app(app):
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/test_db_new"
    
    
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/testing_db"
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
    "mysql://root:ryqbwzy@localhost:3306/product_db"
    
    @classmethod
    def  init_app(cls, app):
        Config.init_app(app)
        
        """send error to admin by email"""
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls,"MAIL_USERNAME", None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, "MAIL_USE_TLS",None):
                secure = ()
        mail_hander = SMTPHandler(
            mailhost = (cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr = cls.FLASKY_MAIL_SENDER,
            toaddrs = [cls.FLASKY_ADMIN],
            subject = cls.FLASKY_MAIL_SUBJECT_PREFIX + "Application Error",
            credentials = credentials,
            secure = secure)
        mail_hander.setLevel(logging.ERROR)
        app.logger.addHandler(mail_hander)
    
class AliyunConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        """handle proxy server headers"""
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        """log to stderr"""
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        """handle proxy server headers"""
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
        
        """log to syslog"""
        import logging
        from logging.handlers import SysLogHandler
        syslog_hander = SysLogHandler()
        syslog_hander.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_hander)
        
    
config = {
    "development": DevelopmentConfig,
    "testing" : TestingConfig,
    "production" : ProductionConfig,
    "default" : DevelopmentConfig,
    "aliyun" : AliyunConfig,
    "unix": UnixConfig
}
