from flask import current_app

def get_user_by_id(user_id):
    supabase = current_app.supabase
    response = supabase.table('users').select('*').eq('user_id', user_id).execute()
    return response.data[0] if response.data else None

def get_pending_users():
    supabase = current_app.supabase
    response = supabase.table('users').select('*').eq('approval_status', 'pending').execute()
    return response.data

def approve_user(user_id):
    supabase = current_app.supabase
    supabase.table('users').update({'approval_status': 'approved'}).eq('user_id', user_id).execute()

def check_in_user(user_id):
    supabase = current_app.supabase
    supabase.table('users').update({'check_in_status': 'checked_in'}).eq('user_id', user_id).execute()

def get_admin_by_email(email):
    supabase = current_app.supabase
    response = supabase.table('admins').select('*').eq('email', email).execute()
    return response.data[0] if response.data else None