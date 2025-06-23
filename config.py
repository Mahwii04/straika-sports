import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)  # Proper None handling
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['the.opeyemimichael@gmail.com']
    
    # Pagination
    POSTS_PER_PAGE = 10
    COMMENTS_PER_PAGE = 10
    
    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Analytics
    ANALYTICS_ENABLED = True

    # RapidAPI Football Data Configuration
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY') or 'your-rapidapi-key'
    RAPIDAPI_HOST = os.environ.get('RAPIDAPI_HOST') or 'api-football-v1.p.rapidapi.com'
    RAPIDAPI_BASE_URL = os.environ.get('RAPIDAPI_BASE_URL') or 'https://api-football-v1.p.rapidapi.com/v3'
    # Cache settings to minimize API calls
    CACHE_TTL = 3600  # 1 hour cache for static data like leagues, teams
    PREDICTION_CACHE_TTL = 10800  # 3 hours for prediction-relevant data
    
    # Site settings
    # Site-specific settings can be loaded in init_app

    @staticmethod
    def init_app(app):
        # Load settings from database into app config
        try:
            from app.models import SiteSettings
            app.config.update({
                'SITE_NAME': SiteSettings.get('SITE_NAME', app.config.get('SITE_NAME', 'Sports Blog')),
                'SITE_DESCRIPTION': SiteSettings.get('SITE_DESCRIPTION', app.config.get('SITE_DESCRIPTION', '')),
                'POSTS_PER_PAGE': int(SiteSettings.get('POSTS_PER_PAGE', app.config.get('POSTS_PER_PAGE', 10))),
                'CONTACT_EMAIL': SiteSettings.get('CONTACT_EMAIL', app.config.get('CONTACT_EMAIL', '')),
                'SITE_LOGO': SiteSettings.get('SITE_LOGO')
            })
        except Exception:
            # If SiteSettings or app is not ready, skip updating config
            pass


    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app-dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Email errors to administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr='no-reply@' + cls.MAIL_SERVER,
            toaddrs=cls.ADMINS,
            subject='Sports Blog Failure',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

