from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_login import LoginManager # type: ignore
from flask_tailwind import Tailwind # type: ignore
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback

# Load environment variables
load_dotenv()

# Create database and login manager objects
db = SQLAlchemy()
login_manager = LoginManager()
tailwind = Tailwind()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///quiz.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Security configurations
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 dakika
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 saat
    
    # Configure logging
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up file handler for logging
        file_handler = RotatingFileHandler('logs/quiz_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Apply handler to app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Quiz App startup')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    tailwind.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints
    from app.routes import main, auth, quiz
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(quiz.bp)
    
    # Before request hook for security
    @app.before_request
    def before_request():
        # HTTPS yönlendirmesi (production ortamında)
        if not app.debug and not app.testing and not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
    # After request hook for security headers
    @app.after_request
    def add_security_headers(response):
        # Security Headers
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' https://cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net;"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'404 Error: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        error_traceback = traceback.format_exc()
        app.logger.error(f'500 Error: {error_traceback}')
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f'400 Error: {request.url}')
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f'403 Error: {request.url}')
        return render_template('errors/403.html'), 403
    
    # Create database
    with app.app_context():
        db.create_all()
    
    return app 