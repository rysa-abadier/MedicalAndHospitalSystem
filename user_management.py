import tkinter as tk
from tkinter import ttk, messagebox
import database as db
import validation as valid
from gui import GUI

class UserManagementSystem:
    def __init__(self, root, current_user):
        self.root = root
        self.root.title("User Management System")
        self.current_user = current_user
        
        self.GUI = GUI(self.root)

        # Initialize callbacks first (set them to None)
        self.logout_callback = None
        self.return_to_dashboard_callback = None
        self.show_patient_records_callback = None 
        self.show_appointments_callback = None

        db.initialize_data_files()
        self.users = db.load_data(db.users_file)
        self.patients = db.load_data(db.patients_file)

        self.root.configure(bg=GUI.bg_color)
        self.root.geometry('1000x600+350+200')
        
        # Now create the UI elements
        self.nav_frame = tk.Frame(root, bg=GUI.bg_color)
        self.nav_frame.pack(fill='x', pady=(20, 15))

        tk.Button(self.nav_frame, text="Dashboard", command=self.return_to_dashboard, 
                font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=(15,5))
        tk.Button(self.nav_frame, text="Patient Records", command=self.show_patient_records, 
                font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        tk.Button(self.nav_frame, text="Appointments", command=self.show_appointments, 
                font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)

        tk.Button(self.nav_frame, text="Logout", command=self.logout, 
                font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right', padx=(5, 15))
        
        self.dashboard_content = tk.Frame(root, bg=GUI.bg_color)
        self.dashboard_content.pack(fill='both', expand=True)
        
        self.show_user_record()
        
    def show_patient_records(self):
        if self.show_patient_records_callback:
            self.show_patient_records_callback()
        elif self.return_to_dashboard_callback:
            self.return_to_dashboard_callback()
            
    def show_appointments(self):
        if self.show_appointments_callback:
            self.show_appointments_callback()
        elif self.return_to_dashboard_callback:
            self.return_to_dashboard_callback()
            
    def return_to_dashboard(self):
        if self.return_to_dashboard_callback:
            self.return_to_dashboard_callback()
    
    def show_user_record(self):
        for widget in self.dashboard_content.winfo_children():
            widget.destroy()

        tk.Label(self.dashboard_content, text="User Record", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=10)
        
        #Options frame
        option_frame = tk.Frame(self.dashboard_content, bg=GUI.bg_color)
        option_frame.pack(fill='x', pady=(10, 5), padx=15)
            
        tk.Label(option_frame, text="Filter by:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color
).pack(side='left', padx=(0, 5))
        self.user_filter = ttk.Combobox(option_frame, values=["All", "Admin", "Doctor", "Nurse", "Patient"], width=GUI.combo_width)
        self.user_filter.pack(side='left', padx=5)
        self.user_filter.current(0)
            
        tk.Button(option_frame, text="Apply Filter", command=self.filter_users, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)

        tk.Button(option_frame, text="Delete User", command=self.delete_user, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right', padx=5)
                
        tk.Button(option_frame, text="Update User", command=self.show_update_user, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right', padx=5)

        tk.Button(option_frame, text="View Details", command=self.view_user_details, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right', padx=5)
            
        tk.Button(option_frame, text="Register User", command=self.show_register_user, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right', padx=5)

        #Treeview to display users
        tree_frame = tk.Frame(self.dashboard_content)
        tree_frame.pack(fill='both', expand=True, pady=(10, 15), padx=15)
            
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
            
        columns = ('username', 'name', 'role', 'age', 'gender', 'email', 'contact_no')
        self.user_tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=scrollbar.set)
        self.user_tree.pack(fill='both', expand=True)
            
        scrollbar.config(command=self.user_tree.yview)
            
        #Configure columns
        self.user_tree.heading('#0', text='User ID')
        self.user_tree.column('#0', width=80)
            
        for col in columns:
            self.user_tree.heading(col, text=col.capitalize())
            self.user_tree.column(col, width=120)
                
        #Add users to treeview
        self.load_all_users()
                    
    def load_all_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        
        for user in self.users:
                
            if 'user_id' not in user:
                print(f"Warning: User missing user_id: {user}")
                continue
                    
            self.user_tree.insert('', 'end', 
                                text=user['user_id'],
                                values=(user.get('username', ''),
                                    user.get('name', ''),
                                    user.get('role', ''),
                                    user.get('age', ''),
                                    user.get('gender', ''),
                                    user.get('email', ''),
                                    user.get('contact_no', '')))

    def filter_users(self):
        filter_by = self.user_filter.get()
        self.user_tree.delete(*self.user_tree.get_children())
        
        for user in self.users:            
            if filter_by == "All":
                pass
            elif filter_by == "Admin" and user['role'] != "Admin":
                continue
            elif filter_by == "Doctor" and user['role'] != "Doctor":
                continue
            elif filter_by == "Nurse" and user['role'] != "Nurse":
                continue
            elif filter_by == "Patient" and user['role'] != "Patient":
                continue
            
            self.user_tree.insert('', 'end', text=user['user_id'],
                                values=(user['username'], user['name'], user['role'], user['age'], user['gender'], user['email'], user['contact_no']))

    def show_register_user(self):
        self.new_user_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.new_user_window.title("Register User")
        self.new_user_window.geometry("450x525+550+225")

        tk.Label(self.new_user_window, text="User Registration", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 5))
        
        form_frame = tk.Frame(self.new_user_window, bg=GUI.bg_color)
        form_frame.pack(pady=(5, 15))
        
        #Name
        tk.Label(form_frame, text="Full Name:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_name = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        #Username
        tk.Label(form_frame, text="Username:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_username = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_username.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        #Password
        tk.Label(form_frame, text="Password:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_password = tk.Entry(form_frame, show="*", width=GUI.entry_width)
        self.reg_password.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        #Confirm Password
        tk.Label(form_frame, text="Confirm Password:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_confirm = tk.Entry(form_frame, show="*", width=GUI.entry_width)
        self.reg_confirm.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        #Role
        tk.Label(form_frame, text="Role:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_role = ttk.Combobox(form_frame, 
                                         values=["Admin",
                                                "Doctor",
                                                "Nurse",
                                                "Patient"], width=GUI.combo_width)
        self.reg_role.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        #Age
        tk.Label(form_frame, text="Age:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=5, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_age = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_age.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        #Gender
        tk.Label(form_frame, text="Gender:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=6, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_gender = tk.StringVar(value="None")
        self.reg_gender_frame = tk.Frame(form_frame, bg=GUI.bg_color)
        self.reg_gender_frame.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        tk.Radiobutton(self.reg_gender_frame, text="Male", variable=self.reg_gender, value="Male", bg=GUI.bg_color).pack(side="left",
        padx=5)
        tk.Radiobutton(self.reg_gender_frame, text="Female", variable=self.reg_gender,
        value="Female", bg=GUI.bg_color).pack(side="left", padx=5)

        #Email
        tk.Label(form_frame, text="Email:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=7, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_email = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_email.grid(row=7, column=1, padx=5, pady=5, sticky='w')

        #Contact Number
        tk.Label(form_frame, text="Contact Number:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=8, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_contact_no = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_contact_no.grid(row=8, column=1, padx=5, pady=5, sticky='w')

        #Security Questions
        tk.Label(form_frame, text="Security Questions:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=9, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_question = ttk.Combobox(form_frame, 
                                         values=["What's your mother's maiden name?",
                                                "What city were you born in?",
                                                "What was the name of your first pet?"], width=GUI.combo_width)
        self.reg_question.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        
        tk.Label(form_frame, text="Answer:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=10, column=0, padx=(15, 5), pady=5, sticky='w')
        self.reg_answer = tk.Entry(form_frame, width=GUI.entry_width)
        self.reg_answer.grid(row=10, column=1, padx=5, pady=5, sticky='w')
        
        tk.Button(self.new_user_window, text="Register", command=self.register_user, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(pady=10)
        
    def register_user(self):
        name = self.reg_name.get()
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()
        role = self.reg_role.get()
        age = self.reg_age.get()
        gender = self.reg_gender.get()
        email = self.reg_email.get()
        contact_no = self.reg_contact_no.get()
        question = self.reg_question.get()
        answer = self.reg_answer.get()
        
        if not all([name, username, password, confirm, role, age, gender, email, contact_no, question, answer]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match!")
            return
        
        if any(user['username'] == username and user['name'] == name for user in self.users):
            messagebox.showerror("Error", "This user already has an account!")
            return
        
        new_user_id = f"U{len(self.users)+1:04d}"

        if role == 'Patient':
            new_user = {
                "user_id": new_user_id,
                "patient_id": f"P{len(self.patients)+1:04d}",
                "username": username,
                "password": valid.hash_password(password),
                "name": name,
                "role": 'Patient',
                "age": age,
                "gender": gender,
                "email": email,
                "contact_no": contact_no,
                "security_question": question,
                "security_answer": answer
            }
        else:
            new_user = {
                "user_id": new_user_id,
                "username": username,
                "password": valid.hash_password(password),
                "name": name,
                "role": role,
                "age": age,
                "gender": gender,
                "email": email,
                "contact_no": contact_no,
                "security_question": question,
                "security_answer": answer
            }

        self.users.append(new_user)
        db.save_data(self.users, db.users_file)

        messagebox.showinfo("Success", "User registered successfully!")
        self.new_user_window.destroy()
        self.show_user_record()

    def view_user_details(self):
        self.i = 0
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user!")
            return
        
        item = self.user_tree.item(selected_item)
        user_id = item['text']
        
        user = next((u for u in self.users if u['user_id'] == user_id), None)
        
        if not user:
            messagebox.showerror("Error", "User not found!")
            return
        
        self.view_user_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.view_user_window.title(f"User Details - {user_id}")
        self.view_user_window.geometry("525x350+500+225")
        
        #Display user details
        tk.Label(self.view_user_window, text=f"User ID: {user['user_id']}", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 5))
        
        details_frame = tk.Frame(self.view_user_window, bg=GUI.bg_color)
        details_frame.pack(pady=(5, 15), padx=10, fill='x')

        if user['role'] == 'Patient':
            tk.Label(details_frame, text="Patient ID:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=0, sticky='w', padx=(15, 5))
            tk.Label(details_frame, text=user['patient_id'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=1, sticky='w')
            self.i += 1
        
        tk.Label(details_frame, text="Name:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['name'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1
        
        tk.Label(details_frame, text="Username:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['username'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1
        
        tk.Label(details_frame, text="Password:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['password'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1
        
        tk.Label(details_frame, text="Role:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['role'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1

        tk.Label(details_frame, text="Age:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['age'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1

        tk.Label(details_frame, text="Gender:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['gender'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1

        tk.Label(details_frame, text="Email:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['email'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1

        tk.Label(details_frame, text="Contact Number:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['contact_no'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1
        
        tk.Label(details_frame, text="Security Question:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['security_question'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')
        self.i += 1

        tk.Label(details_frame, text="Security Answer:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=0, sticky='w', padx=(15, 5))
        tk.Label(details_frame, text=user['security_answer'], anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=self.i, column=1, sticky='w')

    def show_update_user(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user!")
            return
        
        item = self.user_tree.item(selected_item)
        user_id = item['text']
        
        user = next((u for u in self.users if u['user_id'] == user_id), None)
        
        if not user:
            messagebox.showerror("Error", "User not found!")
            return
        
        self.update_user_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.update_user_window.title(f"Update User Details- {user_id}")
        self.update_user_window.geometry("450x500+500+200")
        
        tk.Label(self.update_user_window, text=f"User ID: {user['user_id']}", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 5))

        form_frame = tk.Frame(self.update_user_window, bg=GUI.bg_color)
        form_frame.pack(pady=(5, 15))
        
        #Name
        tk.Label(form_frame, text="Full Name:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_name = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_name.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        #Username
        tk.Label(form_frame, text="Username:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_username = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_username.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        #Password
        tk.Label(form_frame, text="Password:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_password = tk.Entry(form_frame, show="*", width=GUI.entry_width)
        self.update_password.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        #Confirm Password
        tk.Label(form_frame, text="Confirm Password:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_confirm = tk.Entry(form_frame, show="*", width=GUI.entry_width)
        self.update_confirm.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        #Role
        tk.Label(form_frame, text="Role:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_role = ttk.Combobox(form_frame, 
                             values=["Admin", "Doctor", "Nurse", "Patient"], 
                             width=GUI.combo_width,
                             state="readonly")
        self.update_role.grid(row=4, column=1, padx=5, pady=5, sticky='w')

        #Age
        tk.Label(form_frame, text="Age:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=5, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_age = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_age.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        #Gender
        tk.Label(form_frame, text="Gender:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=6, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_gender = tk.StringVar(value="None")
        self.update_gender_frame = tk.Frame(form_frame, bg=GUI.bg_color)
        self.update_gender_frame.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        tk.Radiobutton(self.update_gender_frame, text="Male", variable=self.update_gender, value="Male", bg=GUI.bg_color).pack(side="left",
        padx=5)
        tk.Radiobutton(self.update_gender_frame, text="Female", variable=self.update_gender,
        value="Female", bg=GUI.bg_color).pack(side="left", padx=5)

        #Email
        tk.Label(form_frame, text="Email:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=7, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_email = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_email.grid(row=7, column=1, padx=5, pady=5, sticky='w')

        #Contact Number
        tk.Label(form_frame, text="Contact Number:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=8, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_contact_no = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_contact_no.grid(row=8, column=1, padx=5, pady=5, sticky='w')

        #Security Questions
        tk.Label(form_frame, text="Security Questions:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=9, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_question = ttk.Combobox(form_frame, 
                                         values=["What's your mother's maiden name?",
                                                "What city were you born in?",
                                                "What was the name of your first pet?"], width=GUI.combo_width)
        self.update_question.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        
        #Security Question Answer
        tk.Label(form_frame, text="Answer:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=10, column=0, padx=(15, 5), pady=5, sticky='w')
        self.update_answer = tk.Entry(form_frame, width=GUI.entry_width)
        self.update_answer.grid(row=10, column=1, padx=5, pady=5, sticky='w')
        
        #Pre-fill the form with current values
        self.update_name.insert(0, user['name'])
        self.update_username.insert(0, user['username'])
        self.update_role.set(user['role'])
        self.update_age.insert(0, str(user['age']))
        self.update_gender.set(user['gender'])
        self.update_email.insert(0, user['email'])
        self.update_contact_no.insert(0, user['contact_no'])
        self.update_question.set(user['security_question'])
        self.update_answer.insert(0, user['security_answer'])
        
        tk.Button(self.update_user_window, text="Update", command=lambda: self.update_user_details(user_id), font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(pady=10)
        
    def update_user_details(self, user_id):
        # Get all values from the form
        new_name = self.update_name.get()
        new_username = self.update_username.get()
        new_password = self.update_password.get()
        confirm = self.update_confirm.get()
        new_role = self.update_role.get()
        new_age = self.update_age.get()
        new_gender = self.update_gender.get()
        new_email = self.update_email.get()
        new_contact_no = self.update_contact_no.get()
        new_question = self.update_question.get()
        new_answer = self.update_answer.get()

        # Validate password if changed
        if new_password and new_password != confirm:
            messagebox.showerror("Error", "Passwords don't match!")
            return

        # Check for duplicate username
        for user in self.users:
            if user['user_id'] != user_id and user['username'] == new_username:
                messagebox.showerror("Error", "Username already exists!")
                return

        # Find and update the user
        for idx, user in enumerate(self.users):
            if user['user_id'] == user_id:
                # Only update fields that have new values
                if new_name:
                    self.users[idx]['name'] = new_name
                if new_username:
                    self.users[idx]['username'] = new_username
                if new_password:
                    self.users[idx]['password'] = valid.hash_password(new_password)
                if new_role:
                    self.users[idx]['role'] = new_role
                if new_age:
                    self.users[idx]['age'] = new_age
                if new_gender != "None":
                    self.users[idx]['gender'] = new_gender
                if new_email:
                    self.users[idx]['email'] = new_email
                if new_contact_no:
                    self.users[idx]['contact_no'] = new_contact_no
                if new_question:
                    self.users[idx]['security_question'] = new_question
                if new_answer:
                    self.users[idx]['security_answer'] = new_answer
                
                break

        db.save_data(self.users, db.users_file)
        messagebox.showinfo("Success", "Details updated successfully!")
        self.update_user_window.destroy()
        self.show_user_record()
     
    def delete_user(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a user!")
            return
        
        item = self.user_tree.item(selected_item)
        user_id = item['text']
        
        if not messagebox.askyesno("Confirm", "Delete this User?"):
            return
        
        self.users = [user for user in self.users if user['user_id'] != user_id]
            
        db.save_data(self.users, db.users_file)
        messagebox.showinfo("Success", "User deleted!")
        self.show_user_record()

    def logout(self):
        if self.logout_callback:
            self.logout_callback()
        
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
if __name__ == "__main__":
    root = tk.Tk()
    app = UserManagementSystem(root)
    root.mainloop()