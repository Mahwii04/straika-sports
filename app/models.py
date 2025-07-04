from datetime import datetime
from flask import url_for
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(512))  # Increased length for better security
    role = db.Column(db.String(20), default='writer')
    about = db.Column(db.Text)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError:
            return False

    def is_admin(self):
        return self.role == 'admin'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.String(300))
    category = db.Column(db.String(50))
    featured_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_post_user_id'))  
    views = db.Column(db.Integer, default=0)
    page_views = db.relationship(
        'PageView', 
        backref='post', 
        cascade='all, delete-orphan',
        passive_deletes=True
    )  # Relationship to track page views
    status = db.Column(db.String(20), default='draft')  # 'draft' or 'published'
    reading_time = db.Column(db.Integer)
    # SEO rating represented as a single character (e.g., A, B, C, etc.)
    seo_score = db.Column(db.String(1))

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)

class HeroSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', name='fk_heroslide_post_id')
    )
    post = db.relationship('Post', backref='hero_slide')  # Optional: for easy access
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    link = db.Column(db.String(200))
    category = db.Column(db.String(50))  # Category for the hero slide
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post = db.relationship('Post', backref='hero_slides')  # Optional: for easy access
    
    def __init__(self, **kwargs):
        super(HeroSlide, self).__init__(**kwargs)
        if not self.link:
            self.link = ''  # Set empty string instead of None

    def __repr__(self):
        return f'<HeroSlide {self.title}>'
    
    def get_post_url(self):
        if self.post:
            return url_for('blog.post', slug=self.post.slug)
        return url_for('main.index')  # Fallback to homepage
    
    def get_link(self):
        if self.link:
            return self.link
        
        # Fallback logic
        if hasattr(self, 'category') and self.category:
            latest_post = Post.query.filter_by(category=self.category.lower())\
                                  .order_by(Post.created_at.desc())\
                                  .first()
            return url_for('blog.post', slug=latest_post.slug) if latest_post else url_for('main.index')
        
        return url_for('main.index')
    

class League(db.Model):
    __tablename__ = 'leagues'
    id = db.Column(db.Integer, primary_key=True)
    rapidapi_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
    country = db.Column(db.String(100))
    logo = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime)
    predictions = db.relationship('Prediction', backref='league', lazy='dynamic')

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    rapidapi_id = db.Column(db.Integer, unique=True)
    name = db.Column(db.String(100))
    short_name = db.Column(db.String(50))
    logo = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime)

class Fixture(db.Model):
    __tablename__ = 'fixtures'
    id = db.Column(db.Integer, primary_key=True)
    rapidapi_id = db.Column(db.Integer, unique=True)
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    date = db.Column(db.DateTime)
    status = db.Column(db.String(50))  # Not Started, Finished, Postponed, etc.
    home_goals = db.Column(db.Integer)
    away_goals = db.Column(db.Integer)
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    predictions = db.relationship('Prediction', backref='fixture', lazy='dynamic')

class Prediction(db.Model):
    __tablename__ = 'predictions'
    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, db.ForeignKey('fixtures.id'))
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    prediction_type = db.Column(db.String(50))  # 1, 2, 1x, x2, 12, un0.5, ov1.5, etc.
    confidence = db.Column(db.Float)  # 0-1 scale
    is_active = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    reasoning = db.Column(db.Text)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_correct = db.Column(db.Boolean)
    checked_at = db.Column(db.DateTime)

    @property
    def prediction_name(self):
        prediction_names = {
            '1': 'Home Win',
            '2': 'Away Win',
            '1x': 'Home or Draw',
            'x2': 'Away or Draw',
            '12': 'Anybody Win',
            'un0.5': 'Under 0.5 Goals',
            'ov1.5': 'Over 1.5 Goals',
            'un1.5': 'Under 1.5 Goals',
            'ov2.5': 'Over 2.5 Goals',
            'un2.5': 'Under 2.5 Goals',
            'Home ov0.5': 'Home 1+ Goals',
            'Away ov0.5': 'Away 1+ Goals',
            'Home ov1.5': 'Home 2+ Goals',
            'Away ov1.5': 'Away 2+ Goals',
            'GG': 'Both Teams to Score',
            'NG': 'Only One Team Scores'
        }
        return prediction_names.get(self.prediction_type, self.prediction_type)

class PredictionAnalysis(db.Model):
    __tablename__ = 'prediction_analysis'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    total_predictions = db.Column(db.Integer)
    correct_predictions = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    featured_accuracy = db.Column(db.Float)
    analysis = db.Column(db.Text)


class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_url = db.Column(db.String(200))
    referrer = db.Column(db.String(200))
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(
        db.Integer,
        db.ForeignKey('post.id', name='fk_pageview_post_id', ondelete='CASCADE')
    )


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(setting_key, default=None):
        setting = SiteSettings.query.filter_by(setting_key=setting_key).first()
        if setting:
            return setting.setting_value if setting.setting_value is not None else None
    @staticmethod
    def set(setting_key, value, commit=True):
        setting = SiteSettings.query.filter_by(setting_key=setting_key).first()
        if setting:
            setting.setting_value = value
        else:
            setting = SiteSettings(setting_key=setting_key, setting_value=value)
            db.session.add(setting)
        if commit:
            db.session.commit()
        return setting
        db.session.commit()
        return setting
    
@login_manager.user_loader
def load_user(id):
    try:
        return User.query.get(int(id))
    except (ValueError, TypeError):
        return None
    return User.query.get(int(id))

