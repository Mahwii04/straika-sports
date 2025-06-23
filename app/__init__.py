from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import config
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes import main as main_routes
    from app.routes import auth as auth_routes
    from app.routes import admin as admin_routes
    from app.routes import writer as writer_routes
    from app.routes import blog as blog_routes

    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(writer_routes, url_prefix='/writer')
    app.register_blueprint(blog_routes)

    @app.context_processor
    def inject_analytics():
        from app.analytics import get_analytics_data
        return dict(analytics=get_analytics_data())

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    


    return app

