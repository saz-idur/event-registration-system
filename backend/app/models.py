# Since we're using Supabase directly, this file defines the schema as comments for reference
# No ORM like SQLAlchemy is used; Supabase handles schema via its dashboard or SQL

"""
Schema for 'users' table:
- user_id: UUID (primary key, default uuid_generate_v4())
- name: text (not null)
- email: text (unique, not null)
- phone_number: text (unique, not null)
- payment_proof: text (not null, URL to Supabase Storage)
- approval_status: text (default 'pending', options: 'pending', 'approved', 'rejected')
- check_in_status: text (default 'not_checked_in', options: 'not_checked_in', 'checked_in')
- qr_code_image_url: text (nullable, URL to Supabase Storage)

Schema for 'admins' table:
- admin_id: UUID (primary key, default uuid_generate_v4())
- email: text (unique, not null)
- password: text (not null)
"""