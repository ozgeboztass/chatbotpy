from flask import Flask # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_login import LoginManager # type: ignore
from flask_tailwind import Tailwind # type: ignore
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os

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
    
    # Create database
    with app.app_context():
        db.create_all()
    
    return app 