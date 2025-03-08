import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')  # For JWT

    def __init__(self):
        # Validate environment variables
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'SECRET_KEY']
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Configuration loaded successfully")