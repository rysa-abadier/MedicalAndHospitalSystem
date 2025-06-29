import tkinter as tk
from tkinter import ttk, messagebox, font
import validation as valid
import database as db

class UserAuthentication:
    def __init__(self, root):
        self.root = root
        self.root.title("User Authentication")

        self.bg_color = "#f0f4f8"
        self.label_color = "#1f2937"
        self.button_color = "#6B9BDB"
        self.button_label_color = "#ffffff"

        self.entry_width = 30
        self.combo_width = 27

        self.header1_font = font.Font(family="Courier New", size=14, weight="bold")
        self.header2_font = font.Font(family="Courier New", size=11)
        self.button_font = font.Font(family="Courier New", size=10, weight="bold")

        self.root.configure(bg=self.bg_color)

        db.initialize_data_files()
        self.users = db.load_data(db.users_file)
        self.patients = db.load_data(db.patients_file)
        
        self.dashboard_content = tk.Frame(root)
        self.dashboard_content.pack(fill='both', expand=True)

        #Current user will start logged out
        self.current_user = None
        
        self.show_login_screen()
        
        self.login_success_callback = None
    
    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("User Authentication")
        self.root.geometry('400x300+650+300')
        self.root.resizable(False, False)

        self.login_frame = tk.Frame(self.root, bg=self.bg_color)
        self.login_frame.pack(pady=(20, 15))

        tk.Label(self.login_frame, text="Health Center Management", 
                font=self.header1_font, bg=self.bg_color, fg=self.label_color).grid(row=0, column=0, padx=5, pady=20, columnspan=2)

        tk.Label(self.login_frame, text="Username:", 
                font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame, width=self.entry_width)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Password:", 
                font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=2, column=0, padx=5, pady=(5, 15))
        self.password_entry = tk.Entry(self.login_frame, width=self.entry_width, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=(5, 15))

        if valid.check_admin:
            tk.Button(self.login_frame, text="Login", command=self.login, 
                    font=self.button_font, bg=self.button_color, fg=self.button_label_color).grid(row=3, column=0, columnspan=2, pady=10)
        else:
            tk.Button(self.login_frame, text="Login", command=self.login, 
                    font=self.button_font, bg=self.button_color, fg=self.button_label_color).grid(row=3, column=0, pady=10)
            tk.Button(self.login_frame, text="Register Admin", command=self.show_register_admin, 
                    font=self.button_font, bg=self.button_color, fg=self.button_label_color).grid(row=3, column=1, pady=10)

        tk.Button(self.login_frame, text="Forgot Password", command=self.show_forgot_password, 
                font=self.button_font, bg=self.button_color, fg=self.button_label_color).grid(row=4, column=0, columnspan=2)
            
    def show_register_admin(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.title("Register Admin Account")
        self.root.geometry('500x525+650+200')
        
        form_frame = tk.Frame(self.root, bg=self.bg_color)
        form_frame.pack(pady=(20, 15))
        
        tk.Label(form_frame, text="Admin Registration", font=self.header1_font, bg=self.bg_color, fg=self.label_color).grid(row=0, column=0, padx=5, pady=20, columnspan=2)

        #Name
        tk.Label(form_frame, text="Full Name:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=1, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_name = tk.Entry(form_frame, width=self.entry_width)
        self.reg_name.grid(sticky='w', row=1, column=1, pady=5)
        
        #Username
        tk.Label(form_frame, text="Username:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=2, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_username = tk.Entry(form_frame, width=self.entry_width)
        self.reg_username.grid(sticky='w', row=2, column=1, pady=5)
        
        #Password
        tk.Label(form_frame, text="Password:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=3, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_password = tk.Entry(form_frame, width=self.entry_width, show="*")
        self.reg_password.grid(sticky='w', row=3, column=1, pady=5)
        
        #Confirm Password
        tk.Label(form_frame, text="Confirm Password:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=4, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_confirm = tk.Entry(form_frame, width=self.entry_width, show="*")
        self.reg_confirm.grid(sticky='w', row=4, column=1, pady=5)

        #Age
        tk.Label(form_frame, text="Age:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=5, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_age = tk.Entry(form_frame, width=self.entry_width)
        self.reg_age.grid(sticky='w', row=5, column=1, pady=5)

        #Gender
        tk.Label(form_frame, text="Gender:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=6, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_gender = tk.StringVar(value="None")
        self.reg_gender_frame = tk.Frame(form_frame, bg=self.bg_color)
        self.reg_gender_frame.grid(sticky='w', row=6, column=1, pady=5)
        tk.Radiobutton(self.reg_gender_frame, text="Male", variable=self.reg_gender, value="Male", font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(side="left",
        padx=5)
        tk.Radiobutton(self.reg_gender_frame, text="Female", variable=self.reg_gender,
        value="Female", font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(side="left", padx=5)

        #Email
        tk.Label(form_frame, text="Email:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=7, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_email = tk.Entry(form_frame, width=self.entry_width)
        self.reg_email.grid(sticky='w', row=7, column=1, pady=5)

        #Contact Number
        tk.Label(form_frame, text="Contact Number:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=8, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_contact_no = tk.Entry(form_frame, width=self.entry_width)
        self.reg_contact_no.grid(sticky='w', row=8, column=1, pady=5)

        #Security Questions
        tk.Label(form_frame, text="Security Questions:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=9, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_question = ttk.Combobox(form_frame, 
                                         values=["What's your mother's maiden name?",
                                                "What city were you born in?",
                                                "What was the name of your first pet?"], width=self.combo_width)
        self.reg_question.grid(sticky='w', row=9, column=1, pady=5)
        
        tk.Label(form_frame, text="Answer:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).grid(row=10, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_answer = tk.Entry(form_frame, width=self.entry_width)
        self.reg_answer.grid(sticky='w', row=10, column=1, pady=5)
        
        tk.Button(self.register_window, text="Register", command=self.register_admin, font=self.button_font, bg=self.button_color, fg=self.button_label_color).pack(pady=10)
        
    def register_admin(self):
        name = self.reg_name.get()
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        age = self.reg_age.get()
        gender = self.reg_gender.get()
        email = self.reg_email.get()
        contact_no = self.reg_contact_no.get()
        question = self.reg_question.get()
        answer = self.reg_answer.get()
        
        if not all([name, username, password, confirm, age, gender, email, contact_no, question, answer]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match!")
            return
        
        if any(user['username'] == username  and user['name'] == name for user in self.users):
            messagebox.showerror("Error", "Username already exists!")
            return
        
        new_admin = {
            "user_id": f"U{len(self.users)+1:04d}",
            "username": username,
            "password": valid.hash_password(password),
            "name": name,
            "role": "Admin",
            "age": age,
            "gender": gender,
            "email": email,
            "contact_no": contact_no,
            "security_question": question,
            "security_answer": answer
        }
        
        self.users.append(new_admin)
        db.save_data(self.users, db.users_file)
        
        messagebox.showinfo("Success", "Admin account created successfully!")
        self.register_window.destroy()
        self.show_login_screen()
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        user = next((u for u in self.users if u['username'] == username), None)
        
        if not user or user['password'] != valid.hash_password(password):
            messagebox.showerror("Error", "Invalid username or password!")
            return
        
        self.current_user = user
        
        if self.login_success_callback:
            self.login_success_callback()
        
    def show_forgot_password(self):
        self.forgot_window = tk.Toplevel(self.root)
        self.forgot_window.title("Password Recovery")
        self.forgot_window.geometry('400x300+650+300')
        # self.forgot_window.resizable(False, False)
        self.forgot_window.configure(bg=self.bg_color)
        
        tk.Label(self.forgot_window, text="Password Recovery", font=self.header1_font, bg=self.bg_color, fg=self.label_color).pack(pady=(25,5))
        
        tk.Label(self.forgot_window, text="Username:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(pady=5)
        self.recovery_username = tk.Entry(self.forgot_window, width=self.entry_width)
        self.recovery_username.pack(pady=5)
        
        tk.Button(self.forgot_window, text="Next", command=self.verify_user_for_recovery, font=self.button_font, bg=self.button_color, fg=self.button_label_color).pack(pady=10)
        
    def verify_user_for_recovery(self):
        username = self.recovery_username.get()
        
        if not username:
            messagebox.showerror("Error", "Please enter your username!")
            return
        
        user = next((u for u in self.users if u['username'] == username), None)
        
        if not user:
            messagebox.showerror("Error", "Username not found!")
            return
        
        for widget in self.forgot_window.winfo_children():
            widget.destroy()
            
        tk.Label(self.forgot_window, text="Security Question", font=self.header1_font, bg=self.bg_color, fg=self.label_color).pack(pady=(20, 15))
        tk.Label(self.forgot_window, text=user['security_question'], font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(pady=5)
        
        tk.Label(self.forgot_window, text="Answer:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(pady=5)
        self.recovery_answer = tk.Entry(self.forgot_window, width=self.entry_width)
        self.recovery_answer.pack(pady=5)
        
        tk.Label(self.forgot_window, text="New Password:", font=self.header2_font, bg=self.bg_color, fg=self.label_color).pack(pady=5)
        self.new_password = tk.Entry(self.forgot_window, show="*", width=self.entry_width)
        self.new_password.pack(pady=5)
        
        tk.Button(self.forgot_window, text="Reset Password", command=lambda: self.reset_password(user), font=self.button_font, bg=self.button_color, fg=self.button_label_color).pack(pady=10)
        
    def reset_password(self, user):
        answer = self.recovery_answer.get()
        new_password = self.new_password.get()
        
        if not answer or not new_password:
            messagebox.showerror("Error", "Please provide answer in both fields!")
            return
        
        if answer.lower() != user['security_answer'].lower():
            messagebox.showerror("Error", "Incorrect answer to security question!")
            return
        
        for u in self.users:
            if u['username'] == user['username']:
                u['password'] = valid.hash_password(new_password)
                break
            
        db.save_data(self.users, db.users_file)
        messagebox.showinfo("Success", "Password reset successfully!")
        self.forgot_window.destroy()

    def logout(self):
        self.current_user = None
        self.show_login_screen()
        
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
if __name__ == "__main__":
    root = tk.Tk()
    app = UserAuthentication(root)
    root.mainloop()