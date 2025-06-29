import json
import os
import database as db

users_file = "users.json"
patients_file = "patients.json"
appointments_file = "appointments.json"

def load_data(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            
            if filename == db.users_file:
                for user in data:
                    if 'user_id' not in user:
                        user['user_id'] = f"U{len(data)+1:04d}" 
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_data(data, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")
        raise
        
def initialize_data_files():
    for filename in [users_file, patients_file, appointments_file]:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                json.dump([], f)
  