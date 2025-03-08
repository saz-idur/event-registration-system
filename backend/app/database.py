from flask import current_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_by_id(user_id):
    supabase = current_app.supabase
    try:
        response = supabase.table('users').select('*').eq('user_id', user_id).execute()
        user = response.data[0] if response.data else None
        logger.debug(f"User fetched: {user_id if user else 'Not found'}")
        return user
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {str(e)}")
        raise

def get_pending_users():
    supabase = current_app.supabase
    try:
        response = supabase.table('users').select('*').eq('approval_status', 'pending').execute()
        logger.debug(f"Fetched {len(response.data)} pending users")
        return response.data
    except Exception as e:
        logger.error(f"Error fetching pending users: {str(e)}")
        raise

def approve_user(user_id):
    supabase = current_app.supabase
    try:
        supabase.table('users').update({'approval_status': 'approved'}).eq('user_id', user_id).execute()
        logger.info(f"User {user_id} approved")
    except Exception as e:
        logger.error(f"Error approving user {user_id}: {str(e)}")
        raise

def check_in_user(user_id):
    supabase = current_app.supabase
    try:
        supabase.table('users').update({'check_in_status': 'checked_in'}).eq('user_id', user_id).execute()
        logger.info(f"User {user_id} checked in")
    except Exception as e:
        logger.error(f"Error checking in user {user_id}: {str(e)}")
        raise

def get_admin_by_email(email):
    supabase = current_app.supabase
    try:
        response = supabase.table('admins').select('*').eq('email', email).execute()
        admin = response.data[0] if response.data else None
        logger.debug(f"Admin fetched: {email if admin else 'Not found'}")
        return admin
    except Exception as e:
        logger.error(f"Error fetching admin by email {email}: {str(e)}")
        raise