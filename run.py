import os
from app import create_app, db
from app.models import User, Post, HeroSlide, Prediction, Subscriber
from flask_migrate import Migrate

# Create the Flask application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
        'HeroSlide': HeroSlide,
        'Prediction': Prediction,
        'Subscriber': Subscriber
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)