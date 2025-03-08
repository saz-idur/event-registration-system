from flask import Flask
from flask_jwt_extended import JWTManager
from .routes.user import bp as user_bp
from .routes.qr_code import bp as qr_code_bp
from .routes.whatsapp import bp as whatsapp_bp
from .routes.auth import bp as auth_bp
from .utils.whatsapp import WhatsAppBot
import logging

# Configure logging with a file handler for persistence
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    # Initialize Supabase
    from supabase import create_client, Client
    try:
        supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
        app.supabase = supabase
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        raise

    # Initialize JWT
    jwt = JWTManager(app)

    # Initialize WhatsApp bot
    try:
        app.whatsapp_bot = WhatsAppBot()
        logger.info("WhatsApp bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize WhatsApp bot: {str(e)}")
        raise

    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(qr_code_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(auth_bp)

    @app.teardown_appcontext
    def shutdown_whatsapp_bot(exception=None):
        if hasattr(app, 'whatsapp_bot'):
            app.whatsapp_bot.close()
            logger.info("WhatsApp bot shutdown completed")

    return app