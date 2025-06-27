from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import db, mail
from flask_mail import Message
from app.models import User, Post, HeroSlide, Prediction, Subscriber, PageView, SiteSettings
from app.forms import LoginForm, RegistrationForm, PostForm, HeroSlideForm, PredictionForm, NewsletterForm, UserForm, SiteSettingsForm, PasswordForm
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, desc, distinct
import os
from werkzeug.utils import secure_filename
from app.models import Post, HeroSlide 
from app.forms import PostForm, ProfileForm, ChangePasswordForm, SiteSettingsForm, HeroSlideForm, NewsletterForm, DeleteForm
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta



# Main Blueprint
main = Blueprint('main', __name__)


@main.route('/run-migrations')
@login_required
def run_migrations():
    """Endpoint to run database migrations."""
    if not current_user.is_admin():
        flash('You do not have permission to run migrations.', 'danger')
        return redirect(url_for('main.index'))
    

    from flask_migrate import upgrade
    upgrade()
    return "Migrations applied!"



@main.route('/')
def index():
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.created_at.desc()).limit(5).all()
    
    # Ensure each slide has a valid link
    for slide in hero_slides:
        if not slide.link:
            # Only try to get post by category if category exists
            if slide.category:
                latest_post = Post.query.filter_by(category=slide.category.lower())\
                                      .order_by(Post.created_at.desc())\
                                      .first()
                slide.link = url_for('blog.post', slug=latest_post.slug) if latest_post else url_for('main.index')
            else:
                slide.link = url_for('main.index')
                
    latest_posts = Post.query.order_by(Post.created_at.desc()).limit(4).all()
    football_posts = Post.query.filter_by(category='football').order_by(Post.created_at.desc()).limit(3).all()
    tennis_posts = Post.query.filter_by(category='tennis').order_by(Post.created_at.desc()).limit(3).all()
    basketball_posts = Post.query.filter_by(category='basketball').order_by(Post.created_at.desc()).limit(3).all()
    esports_posts = Post.query.filter_by(category='esports').order_by(Post.created_at.desc()).limit(3).all()
    
    return render_template('blog/index.html', 
                         hero_slides=hero_slides,
                         predictions=predictions,
                         latest_posts=latest_posts,
                         football_posts=football_posts,
                         tennis_posts=tennis_posts,
                         basketball_posts=basketball_posts,
                         esports_posts=esports_posts)


@main.app_errorhandler(404)
def page_not_found(e):
    # Render a custom 404 error page
    return render_template('404.html'), 404




@main.route('/about')
def about():
    return render_template('blog/about.html')


# Auth Blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on user role
        if hasattr(current_user, 'role'):
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif current_user.role == 'writer':
                return redirect(url_for('writer.dashboard'))
        # Default fallback
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        # Check user role before login
        if hasattr(user, 'role'):
            login_user(user, remember=form.remember.data)
            if user.role == 'admin':
                next_page = request.args.get('next') or url_for('admin.dashboard')
            elif user.role == 'writer':
                next_page = request.args.get('next') or url_for('writer.dashboard')
            else:
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('User role not defined.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/onboard', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

# Admin Blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Basic analytics data
    stats = {
        'total_posts': Post.query.count(),
        'total_users': User.query.count(),
        'new_users': User.query.filter(
            User.last_seen >= datetime.utcnow() - timedelta(days=7)
        ).count(),
        'popular_posts': Post.query.order_by(Post.views.desc()).limit(5).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)


@admin.route('/hero-slides', methods=['GET', 'POST'])
@login_required
def hero_slides():
    # Get all current hero slides
    form = HeroSlideForm()
    hero_slides = HeroSlide.query.order_by(HeroSlide.created_at.desc()).all()
    
    # Get posts that aren't already hero slides
    current_post_ids = [slide.post_id for slide in hero_slides]
    available_posts = Post.query.filter(~Post.id.in_(current_post_ids)).all()
    
    return render_template('admin/hero_slides.html',
                         form=form,
                         hero_slides=hero_slides,
                         available_posts=available_posts)

@admin.route('/add-hero-slide', methods=['POST'])
@login_required
def add_hero_slide():
    post_id = request.form.get('post_id')
    is_active = request.form.get('is_active', 'off') == 'on'
    
    if not post_id:
        flash('Please select a post', 'danger')
        return redirect(url_for('admin.hero_slides'))
    
    post = Post.query.get_or_404(post_id)
    
    # Create new hero slide
    slide = HeroSlide(
        post_id=post.id,
        title=post.title,
        description=post.excerpt,
        image_url=post.featured_image,
        is_active=is_active
    )
    
    db.session.add(slide)
    db.session.commit()
    
    flash('Post added to hero slides successfully!', 'success')
    return redirect(url_for('admin.hero_slides'))

@admin.route('/toggle-hero-slide/<int:slide_id>', methods=['POST'])
@login_required
def toggle_hero_slide(slide_id):
    slide = HeroSlide.query.get_or_404(slide_id)
    slide.is_active = not slide.is_active
    db.session.commit()
    
    flash('Hero slide status updated', 'success')
    return redirect(url_for('admin.hero_slides'))

@admin.route('/delete-hero-slide/<int:slide_id>', methods=['POST'])
@login_required
def delete_hero_slide(slide_id):
    slide = HeroSlide.query.get_or_404(slide_id)
    db.session.delete(slide)
    db.session.commit()
    
    flash('Hero slide removed successfully', 'success')
    return redirect(url_for('admin.hero_slides'))




@admin.route('/posts')
@login_required
def posts():
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    delete_form = DeleteForm()
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    author = request.args.get('author')
    status = request.args.get('status')
    
    # Start with base query
    query = Post.query
    
    # Apply filters if they exist
    if category:
        query = query.filter_by(category=category)
    if author:
        query = query.filter_by(author_id=author)
    if status:
        query = query.filter_by(status=status)
    
    # Order and paginate
    query = query.order_by(Post.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    
    # Get all users for author filter dropdown
    users = User.query.all()
    
    return render_template('admin/posts.html',
                         posts=pagination.items,
                         pagination=pagination,
                         current_page=page,
                         prev_page=pagination.prev_num,
                         next_page=pagination.next_num,
                         users=users,
                         form=delete_form)


@admin.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    
    # Print form errors for debugging
    if form.errors:
        print("Form errors:", form.errors)
    
    if form.validate_on_submit():
        try:
            # Handle featured image URL
            featured_image = form.featured_image.data if form.featured_image.data else None
            
            # Get content from TinyMCE (ensure it's properly saved)
            content = form.content.data
            
            # Calculate reading time
            content_text = content.replace('\n', ' ').replace('\r', '')
            word_count = len(content_text.split())
            reading_time = max(1, round(word_count / 200))
            
            # Create the post
            post = Post(
                title=form.title.data,
                slug=form.slug.data,
                content=content,
                excerpt=form.excerpt.data,
                category=form.category.data,
                featured_image=featured_image,
                user_id=current_user.id,
                reading_time=reading_time,
                created_at=datetime.utcnow()
            )
            
            db.session.add(post)
            db.session.commit()
            
            flash('Your post has been successfully published!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Display form errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'danger')
    
    return render_template('admin/create_post.html', form=form)

@admin.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        # Update post logic
        pass
    
    return render_template('admin/edit_post.html', form=form, post=post)

@admin.route('/delete-post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted', 'success')
    return redirect(url_for('admin.posts'))

@admin.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    
    # Start with base query
    query = User.query
    
    # Apply role filter if specified
    if role:
        query = query.filter_by(role=role)
    
    # Order and paginate (using a default per_page value of 10)
    pagination = query.order_by(User.last_seen.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination,
                         current_page=page,
                         prev_page=pagination.prev_num,
                         next_page=pagination.next_num,
                         total_pages=pagination.pages)


@admin.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Update basic info
            user.username = form.username.data
            user.email = form.email.data
            user.role = form.role.data
            user.phone = form.phone.data
            user.about = form.about.data
            
            # Update password if provided
            if form.new_password.data:
                user.set_password(form.new_password.data)
                flash('Password has been updated', 'success')
            
            db.session.commit()
            flash('User information has been updated', 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            flash('Error updating user. Please try again.', 'danger')
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to access this page', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('admin.users'))
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        flash('An error occurred while deleting the user.', 'danger')
    return redirect(url_for('admin.users'))


@admin.route('/newsletter', methods=['GET', 'POST'])
@login_required
def newsletter():
    form = NewsletterForm()
    
    # Pagination for subscribers
    page = request.args.get('page', 1, type=int)
    subscribers = Subscriber.query.order_by(desc(Subscriber.subscribed_at)).paginate(
        page=page, per_page=10, error_out=False)
    
    if form.validate_on_submit():
        try:
            # Get all subscribers
            recipients = [sub.email for sub in Subscriber.query.all()]
            
            # Send email
            msg = Message(
                subject=form.subject.data,
                recipients=recipients,
                body=form.message.data,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            mail.send(msg)
            
            flash('Newsletter sent successfully!', 'success')
            return redirect(url_for('admin.newsletter'))
        except Exception as e:
            flash(f'Error sending newsletter: {str(e)}', 'danger')
    
    return render_template('admin/newsletter.html', 
                         form=form,
                         subscribers=subscribers.items,
                         pagination=subscribers,
                         total_pages=subscribers.pages)  # <-- Add this line

@main.route('/add_subscriber', methods=['POST'])
def add_subscriber():
    
    email = request.form.get('email')
    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('admin.newsletter'))
    
    # Check if subscriber already exists
    existing_subscriber = Subscriber.query.filter_by(email=email).first()
    if existing_subscriber:
        flash('Subscriber already exists', 'warning')
        return redirect(url_for('admin.newsletter'))
    
    try:
        new_subscriber = Subscriber(email=email)
        db.session.add(new_subscriber)
        db.session.commit()
        flash('Subscriber added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding subscriber: {str(e)}")
        flash('Error adding subscriber. Please try again.', 'danger')
    
    return redirect(url_for('main.index'))

@admin.route('/delete_subscriber/<int:subscriber_id>', methods=['POST'])
@login_required
def delete_subscriber(subscriber_id):
    subscriber = Subscriber.query.get_or_404(subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash('Subscriber removed successfully', 'success')
    return redirect(url_for('admin.newsletter'))


@admin.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin():
        flash('Administrator access required', 'danger')
        return redirect(url_for('main.index'))
    
    # Initialize all forms
    profile_form = ProfileForm(obj=current_user)
    password_form = PasswordForm()
    site_form = SiteSettingsForm()

    # Handle profile avatar
    if profile_form.validate_on_submit():
        try:
            # Handle avatar upload
            if profile_form.avatar.data:
                filename = secure_filename(profile_form.avatar.data.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                profile_form.avatar.data.save(filepath)
                current_user.avatar = filename
            
            # Update user profile
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            current_user.phone = profile_form.phone.data
            current_user.about = profile_form.about.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {str(e)}")
            flash('Error updating profile. Please try again.', 'danger')
    
    
    # Handle GET request - load current settings
    if request.method == 'GET':
        # Load site settings with defaults
        site_form.site_name.data = SiteSettings.get('SITE_NAME', 'My Sports Blog')  # Default value
        site_form.site_description.data = SiteSettings.get('SITE_DESCRIPTION', 'A sports blog')  # Default value
        site_form.posts_per_page.data = SiteSettings.get('POSTS_PER_PAGE', 10)  # Default value
        site_form.contact_email.data = SiteSettings.get('CONTACT_EMAIL', '')
        site_form.logo.data = SiteSettings.get('SITE_LOGO')
    
    # Handle POST request - update settings
    if request.form.get('form_type') == 'site_settings' and site_form.validate_on_submit():
        try:
            # Handle logo upload
            logo_filename = SiteSettings.get('SITE_LOGO')  # Keep existing if no new upload
            if site_form.logo.data:
                filename = secure_filename(site_form.logo.data.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                site_form.logo.data.save(filepath)
                logo_filename = filename
            
            # Save all settings to database
            SiteSettings.set('SITE_NAME', site_form.site_name.data)
            SiteSettings.set('SITE_DESCRIPTION', site_form.site_description.data)
            SiteSettings.set('POSTS_PER_PAGE', str(site_form.posts_per_page.data))
            SiteSettings.set('CONTACT_EMAIL', site_form.contact_email.data)
            if logo_filename:
                SiteSettings.set('SITE_LOGO', logo_filename)
            
            flash('Site settings updated successfully!', 'success')
            return redirect(url_for('admin.settings'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings: {str(e)}")
            flash('Error updating site settings. Please try again.', 'danger')
    
    # Get current logo for display
    site_settings = {
        'logo': SiteSettings.get('SITE_LOGO')
    }
    
    return render_template('admin/settings.html',
                         profile_form=profile_form,
                         password_form=password_form,
                         site_form=site_form,
                         site_settings=site_settings)


@admin.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if not current_user.is_admin():
        flash('Administrator access required', 'danger')
        return redirect(url_for('main.index'))

    form = ProfileForm()
    if form.validate_on_submit():
        try:
            # Handle avatar upload
            if form.avatar.data:
                filename = secure_filename(form.avatar.data.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                form.avatar.data.save(filepath)
                current_user.avatar = filename

            # Update user profile
            current_user.username = form.username.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data
            current_user.about = form.about.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {str(e)}")
            flash('Error updating profile. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('admin.settings'))


@admin.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if not current_user.is_admin():
        flash('Administrator access required', 'danger')
        return redirect(url_for('main.index'))

    form = PasswordForm()
    if form.validate_on_submit():
        try:
            # Verify current password
            if not current_user.check_password(form.current_password.data):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('admin.settings'))
            
            # Set new password
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password changed successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error changing password: {str(e)}")
            flash('Error changing password. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('admin.settings'))









# Writer Blueprint
writer = Blueprint('writer', __name__, url_prefix='/writer')

@writer.route('/')
@login_required
def dashboard():
    # Get basic stats
    total_posts = current_user.posts.count()
    total_views = db.session.query(func.sum(Post.views)).filter(Post.user_id == current_user.id).scalar() or 0
    avg_reading_time = db.session.query(func.avg(Post.reading_time)).filter(Post.user_id == current_user.id).scalar() or 0
    
    # Calculate engagement score (example formula)
    engagement_score = min(100, (total_views / max(1, total_posts)) + (avg_reading_time * 2))
    
    # Get recent posts
    recent_posts = current_user.posts.order_by(Post.created_at.desc()).limit(5).all()
    
    # Prepare chart data
    last_30_days = datetime.utcnow() - timedelta(days=30)
    daily_views = db.session.query(
        func.date(Post.created_at).label('date'),
        func.sum(Post.views).label('views')
    ).filter(Post.user_id == current_user.id, Post.created_at >= last_30_days)\
     .group_by(func.date(Post.created_at))\
     .order_by(func.date(Post.created_at)).all()
    
    post_views_data = {
        'labels': [date.strftime('%b %d') for date, _ in daily_views],
        'values': [views for _, views in daily_views]
    }
    
    performance_data = {
        'titles': [post.title[:20] + '...' for post in recent_posts],
        'views': [post.views for post in recent_posts],
        'read_times': [post.reading_time for post in recent_posts]
    }
    
    return render_template(
        'writer/dashboard.html',
        total_views=total_views,
        avg_reading_time=avg_reading_time,
        engagement_score=int(engagement_score),
        recent_posts=recent_posts,
        post_views_data=post_views_data,
        performance_data=performance_data
    )



@writer.route('/posts')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.posts.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    posts = pagination.items
    total_pages = pagination.pages  # <-- Add this line
    return render_template('writer/posts.html', posts=posts, pagination=pagination, total_pages=total_pages)

@writer.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload
            featured_image_filename = form.featured_image.data if form.featured_image.data else None

            # Calculate reading time (200 words per minute)
            content_text = form.content.data.replace('\n', ' ').replace('\r', '')
            word_count = len(content_text.split())
            reading_time = max(1, round(word_count / 200))
            
            # Calculate SEO score
            seo_score = calculate_seo_score(form.title.data, form.content.data)
            
            # Create the post
            post = Post(
                title=form.title.data,
                slug=form.slug.data,
                content=form.content.data,
                excerpt=form.excerpt.data,
                category=form.category.data,
                featured_image=featured_image_filename,
                user_id=current_user.id,
                reading_time=reading_time,
                seo_score=seo_score,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(post)
            db.session.commit()
            
            flash('Your post has been successfully published!', 'success')
            return redirect(url_for('writer.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash('An error occurred while creating your post. Please try again.', 'danger')
    
    # If form didn't validate or GET request
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return render_template('writer/create_post.html', form=form)


@writer.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm(obj=post)
    if form.validate_on_submit():
        # Update post fields
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.category = form.category.data
        post.featured_image = form.featured_image.data
        post.updated_at = datetime.utcnow()
        
        # Recalculate metrics
        word_count = len(form.content.data.split())
        post.reading_time = max(1, round(word_count / 200))
        post.seo_score = calculate_seo_score(form.title.data, form.content.data)
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('writer.posts'))
    
    return render_template('writer/edit_post.html', form=form, post=post)

@writer.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('writer.posts'))

@writer.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.about = profile_form.about.data
        current_user.phone = profile_form.phone.data

        if profile_form.avatar.data:
            filename = secure_filename(profile_form.avatar.data.filename)
            avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            profile_form.avatar.data.save(avatar_path)
            current_user.avatar = filename

        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('writer.settings'))

    return render_template('writer/settings.html', profile_form=profile_form, password_form=password_form)

@writer.route('/change_password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('writer.settings'))
        if form.new_password.data == form.current_password.data:
            flash('New password must be different from the current password.', 'warning')
            return redirect(url_for('writer.settings'))
        current_user.password = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('writer.settings'))
    # If form is not valid, re-render settings with errors
    profile_form = ProfileForm(obj=current_user)
    return render_template('writer/settings.html', profile_form=profile_form, password_form=form)


def calculate_seo_score(title, content):
    """Calculate a basic SEO score (A-F) based on content analysis"""
    score = 0
    
    # Title length check (50-60 chars optimal)
    title_len = len(title)
    if 50 <= title_len <= 60:
        score += 25
    elif 40 <= title_len < 50 or 60 < title_len <= 70:
        score += 15
    else:
        score += 5
    
    # Content length check (minimum 300 words)
    word_count = len(content.split())
    if word_count >= 1000:
        score += 25
    elif word_count >= 600:
        score += 20
    elif word_count >= 300:
        score += 15
    else:
        score += 5
    
    # Heading check (at least H2 headings)
    headings = content.count('<h2') + content.count('<h1') + content.count('<h3')
    if headings >= 3:
        score += 25
    elif headings >= 1:
        score += 15
    else:
        score += 5
    
    # Image check
    images = content.count('<img')
    if images >= 1:
        score += 15
    else:
        score += 5
    
    # Link check
    links = content.count('<a href')
    if links >= 1:
        score += 10
    else:
        score += 0
    
    # Determine letter grade
    if score >= 90: return 'A'
    elif score >= 80: return 'B'
    elif score >= 70: return 'C'
    elif score >= 60: return 'D'
    else: return 'F'

# Blog Blueprint
blog = Blueprint('blog', __name__)

@blog.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('blog/post.html', post=post)

@blog.route('/category/<category>')
def category(category):
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(category=category).order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items
    total_pages = pagination.pages
    return render_template('blog/category.html', posts=posts, category=category, pagination=pagination, total_pages=total_pages)

@blog.route('/latest')
def latest():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('blog/latest.html', posts=posts)

@blog.route('/predictions')
def predictions():
    predictions = Prediction.query.filter_by(is_active=True).filter(Prediction.date >= datetime.now(timezone.utc)).order_by(Prediction.date.asc()).all()
    return render_template('blog/predictions.html', predictions=predictions)