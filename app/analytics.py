# app/analytics.py

from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.models import PageView, Post, db

def get_analytics_data():
    # Basic counts
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    daily_views = PageView.query.filter(
        func.date(PageView.timestamp) == today
    ).count()
    
    weekly_views = PageView.query.filter(
        func.date(PageView.timestamp) >= week_ago
    ).count()
    
    monthly_views = PageView.query.filter(
        func.date(PageView.timestamp) >= month_ago
    ).count()
    
    # Popular posts
    popular_posts = Post.query.join(PageView).group_by(Post.id).order_by(
        func.count(PageView.id).desc()
    ).limit(5).all()
    
    # Traffic sources
    traffic_sources = db.session.query(
        func.substr(PageView.referrer, 1, 50).label('source'),
        func.count(PageView.id).label('count')
    ).group_by('source').order_by(func.count(PageView.id).desc()).limit(5).all()
    
    return {
        'daily_views': daily_views,
        'weekly_views': weekly_views,
        'monthly_views': monthly_views,
        'popular_posts': popular_posts,
        'traffic_sources': traffic_sources
    }

def get_detailed_analytics(days=30):
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Views by day
    views_by_day = db.session.query(
        func.date(PageView.timestamp).label('date'),
        func.count(PageView.id).label('count')
    ).filter(
        PageView.timestamp >= date_threshold
    ).group_by(
        func.date(PageView.timestamp)
    ).order_by(
        func.date(PageView.timestamp)
    ).all()
    
    # Views by post category
    views_by_category = db.session.query(
        Post.category,
        func.count(PageView.id).label('count')
    ).join(
        PageView
    ).filter(
        PageView.timestamp >= date_threshold
    ).group_by(
        Post.category
    ).all()
    
    return {
        'views_by_day': views_by_day,
        'views_by_category': views_by_category
    }
