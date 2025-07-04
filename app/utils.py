# app/utils.py

from flask import request
from sqlalchemy import func
from datetime import datetime
from app.models import Post, PageView, db

def track_view(post):
    # Don't track views from admin or preview pages
    if request.path.startswith('/admin') or request.path.startswith('/preview'):
        return
    
    # Update post view count
    post.views += 1
    
    # Check if this IP already viewed this post today
    today = datetime.utcnow().date()
    existing_view = PageView.query.filter(
        PageView.post_id == post.id,
        func.date(PageView.timestamp) == today,
        PageView.ip_address == request.remote_addr
    ).first()
    
    if not existing_view:
        post.views += 1
        
        view = PageView(
            post_id=post.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            referrer=request.referrer,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(view)
        db.session.commit()
