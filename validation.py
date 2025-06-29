import hashlib as hash
import database as db

def hash_password(password):
    return hash.sha256(password.encode()).hexdigest()

def check_admin():
    users = db.load_data(db.users_file)
    for user in users:
        if user.get('role') == 'Admin':
            return True
    return False