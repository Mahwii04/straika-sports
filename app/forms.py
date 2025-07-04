from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, DateTimeField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    content = TextAreaField('Content')
    excerpt = TextAreaField('Excerpt', validators=[DataRequired(), Length(max=300)])
    category = SelectField('Category', choices=[
        ('football', 'Football'), 
        ('tennis', 'Tennis'), 
        ('basketball', 'Basketball'), 
        ('esports', 'Esports')
    ])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published')
    ], default='draft')
    featured_image = StringField('Featured Image URL')
    submit = SubmitField('Publish')

class HeroSlideForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])
    link = StringField('Link')
    category = SelectField('Category', choices=[
        ('', 'None'),
        ('football', 'Football'),
        ('tennis', 'Tennis'),
        ('basketball', 'Basketball'),
        ('esports', 'Esports')
    ])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class PredictionForm(FlaskForm):
    team1 = StringField('Team 1', validators=[DataRequired()])
    team2 = StringField('Team 2', validators=[DataRequired()])
    league = StringField('League', validators=[DataRequired()])
    prediction = StringField('Prediction', validators=[DataRequired()])
    odds = FloatField('Odds', validators=[DataRequired()])
    date = DateTimeField('Match Date', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class NewsletterForm(FlaskForm):
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(max=200)
    ])
    message = TextAreaField('Message', validators=[
        DataRequired()
    ])

    
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
    phone = StringField('Phone', validators=[Length(max=20)])
    about = TextAreaField('About', validators=[Length(max=500)])
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=64)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    role = SelectField('Role', choices=[
        ('writer', 'Writer'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    phone = StringField('Phone', validators=[
        Optional(),
        Length(max=20)
    ])
    about = TextAreaField('About', validators=[
        Optional(),
        Length(max=500)
    ])
    new_password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=6),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')

class DeleteForm(FlaskForm):
    pass

class SiteSettingsForm(FlaskForm):
    site_name = StringField('Site Name', 
                          validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description',
                                   validators=[Length(max=300)])
    posts_per_page = IntegerField('Posts Per Page',
                                validators=[NumberRange(min=1, max=100)])
    contact_email = StringField('Contact Email',
                              validators=[Email(), Length(max=120)])
    logo = FileField('Site Logo',
                        validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 
                                              'Images only!')])
    submit = SubmitField('Save Settings')
    
class PasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])

    def validate_current_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect')



class PredictionForm(FlaskForm):
    team1 = StringField('Home Team', validators=[DataRequired()])
    team2 = StringField('Away Team', validators=[DataRequired()])
    league = StringField('League', validators=[DataRequired()])
    date = DateField('Match Date', format='%Y-%m-%d', validators=[DataRequired()])
    prediction = SelectField('Prediction', choices=[
        ('1', 'Home Win (1)'),
        ('2', 'Away Win (2)'),
        ('1x', 'Home or Draw (1x)'),
        ('x2', 'Away or Draw (x2)'),
        ('12', 'Anybody Win (12)'),
        ('un0.5', 'Under 0.5 Goals'),
        ('ov1.5', 'Over 1.5 Goals'),
        ('un1.5', 'Under 1.5 Goals'),
        ('ov2.5', 'Over 2.5 Goals'),
        ('un2.5', 'Under 2.5 Goals'),
        ('Home ov0.5', 'Home Over 0.5 Goals'),
        ('Away ov0.5', 'Away Over 0.5 Goals'),
        ('Home ov1.5', 'Home Over 1.5 Goals'),
        ('Away ov1.5', 'Away Over 1.5 Goals'),
        ('GG', 'Both Teams to Score (GG)'),
        ('NG', 'Only One Team to Score (NG)')
    ], validators=[DataRequired()])
    confidence = FloatField('Confidence (0-1)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=1, message="Must be between 0 and 1")
    ])
    odds = FloatField('Odds', validators=[DataRequired(), NumberRange(min=1.01)])
    analysis = TextAreaField('Analysis', validators=[DataRequired()])
    is_featured = BooleanField('Featured Prediction')
    
    # Statistical fields
    team1_xg = FloatField('Home Team xG', validators=[DataRequired()])
    team2_xg = FloatField('Away Team xG', validators=[DataRequired()])
    team1_form = StringField('Home Team Form (e.g., WWDLW)', validators=[DataRequired()])
    team2_form = StringField('Away Team Form', validators=[DataRequired()])
    team1_missing_players = TextAreaField('Home Team Missing Players')
    team2_missing_players = TextAreaField('Away Team Missing Players')
    h2h_record = StringField('Head-to-Head (W-D-L e.g., 3-2-5)')
    tactical_notes = TextAreaField('Tactical Notes')