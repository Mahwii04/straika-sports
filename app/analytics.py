# app/analytics.py
from datetime import datetime, timedelta
from app.models import Post, PageView, User, db
from sqlalchemy import func, extract, and_

def get_analytics_data(days=30):
    # Calculate date ranges
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Website traffic data
    daily_views = db.session.query(
        func.date(PageView.timestamp).label('date'),
        func.count(PageView.id).label('views')
    ).filter(PageView.timestamp >= start_date)\
     .group_by(func.date(PageView.timestamp))\
     .order_by(func.date(PageView.timestamp)).all()
    
    # Traffic sources
    traffic_sources = db.session.query(
        func.substr(PageView.referrer, 1, 50).label('source'),
        func.count(PageView.id).label('count')
    ).filter(PageView.timestamp >= start_date)\
     .group_by('source')\
     .order_by(func.count(PageView.id).desc()).limit(5).all()
    
    # Popular posts
    popular_posts = Post.query.join(PageView)\
        .filter(PageView.timestamp >= start_date)\
        .group_by(Post.id)\
        .order_by(func.count(PageView.id).desc())\
        .limit(5).all()
    
    # User growth
    user_growth = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('new_users')
    ).filter(User.created_at >= start_date)\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at)).all()
    
    # Reading time distribution
    reading_times = db.session.query(
        func.floor(Post.reading_time/5)*5,  # Group by 5-minute intervals
        func.count(Post.id)
    ).group_by(func.floor(Post.reading_time/5))\
     .order_by(func.floor(Post.reading_time/5)).all()
    
    return {
        'daily_views': [{'date': str(date), 'views': views} for date, views in daily_views],
        'traffic_sources': [{'source': source, 'count': count} for source, count in traffic_sources],
        'popular_posts': popular_posts,
        'user_growth': [{'date': str(date), 'new_users': new_users} for date, new_users in user_growth],
        'reading_times': [{'minutes': minutes, 'count': count} for minutes, count in reading_times],
        'total_views': sum(view.views for view in daily_views),
        'unique_visitors': db.session.query(func.count(func.distinct(PageView.ip_address)))
                          .filter(PageView.timestamp >= start_date).scalar(),
        'avg_reading_time': db.session.query(func.avg(Post.reading_time)).scalar() or 0
    }