import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from datetime import datetime
from gui import GUI

def get_next_patient_id(patients_list):
    if not patients_list:
        return "P0001"
    
    max_id = 0
    for patient in patients_list:
        pid = patient.get('patient_id', 'P0000')
        if pid and pid.startswith('P'):
            try:
                num = int(pid[1:])
                if num > max_id:
                    max_id = num
            except ValueError:
                continue
    
    return f"P{max_id + 1:04d}"

class PatientRecordManagement:
    def __init__(self, root, current_user):
        self.root = root
        self.root.title("Patient Record Management System")
        self.current_user = current_user

        self.GUI = GUI(self.root)

        self.logout_callback = None
        self.return_to_dashboard_callback = None
        self.show_user_management_callback = None
        self.show_appointments_callback = None

        self.root.configure(bg=GUI.bg_color)
        self.root.geometry('1000x600+350+200')
        
        db.initialize_data_files()
        self.users = db.load_data(db.users_file)
        self.patients = db.load_data(db.patients_file)
        self.appointments = db.load_data(db.appointments_file)

        self.nav_frame = tk.Frame(root, bg=GUI.bg_color)
        self.nav_frame.pack(fill='x', pady=(20, 15), padx=15)
        
        if current_user['role'] == 'Admin':
            tk.Button(self.nav_frame, text="Dashboard", command=self.return_to_dashboard, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            tk.Button(self.nav_frame, text="User Management", command=self.show_user_management, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            
        tk.Button(self.nav_frame, text="Appointments", command=self.show_appointments, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        
        tk.Button(self.nav_frame, text="Logout", command=self.logout, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right')
        
        self.dashboard_content = tk.Frame(root, bg=GUI.bg_color)
        self.dashboard_content.pack(fill='both', expand=True)
        
        self.show_patients()
        
    def refresh_data(self):
        self.users = db.load_data(db.users_file)
        self.patients = db.load_data(db.patients_file)
        self.appointments = db.load_data(db.appointments_file)
        
    def show_user_management(self):
        if self.show_user_management_callback:
            self.show_user_management_callback()
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

    def show_patients(self):
        for widget in self.dashboard_content.winfo_children():
            widget.destroy()

        tk.Label(self.dashboard_content, text="Patient Record Management", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 5))

        # Treeview for displaying patient records
        tree_frame = tk.Frame(self.dashboard_content)
        tree_frame.pack(fill="both", expand=True, pady=(10, 15), padx=15)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("name", "age", "gender", "email", "contact_no", "appointments")
        self.record_tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=scrollbar.set)
        self.record_tree.pack(fill="both", expand=True)

        scrollbar.config(command=self.record_tree.yview)

        # Configure Treeview columns
        self.record_tree.heading("#0", text="Patient ID")
        self.record_tree.column("#0", width=50)
        for col in columns:
            self.record_tree.heading(col, text=col.capitalize())
            self.record_tree.column(col, width=120)

        self.load_all_patients()

        # Add role-based buttons for interaction
        button_frame = tk.Frame(self.dashboard_content, bg=GUI.bg_color)
        button_frame.pack(pady=(5, 15))

        tk.Button(button_frame, text="View Details", command=self.view_patient_details, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side="left", padx=5)
        
        if self.current_user['role'] in ['Admin', 'Doctor', 'Nurse']:
            tk.Button(button_frame, text="Create New Record", command=self.create_patient_record, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            tk.Button(button_frame, text="Edit Record", command=self.edit_patient_record, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side="left", padx=5)

    def load_all_patients(self):
        self.record_tree.delete(*self.record_tree.get_children())

        if self.current_user['role'] == 'Patient':
            patient_id = self.current_user.get('patient_id')
            if not patient_id:
                return
            
            patient = next((p for p in self.patients if p["patient_id"] == patient_id), None)
            user = next((u for u in self.users if u["role"] == 'Patient' and u.get('patient_id') == patient_id), None)
            
            if user and patient:
                appt_ids = ", ".join(patient.get("appointments", ["No Appointments"]))
                self.record_tree.insert("", "end", text=patient["patient_id"],
                                        values=(user["name"], user["age"], user["gender"], user["email"], user["contact_no"], appt_ids))
        else:
            for patient in self.patients:
                user = next((u for u in self.users if u.get('patient_id') == patient['patient_id'] and u['role'] == 'Patient'), None)
                if user:
                    appt_ids = ", ".join(patient.get("appointments", ["No Appointments"]))
                    self.record_tree.insert("", "end", text=patient["patient_id"],
                                            values=(user["name"], user["age"], user["gender"], user["email"], user["contact_no"], appt_ids))
                    
    def create_patient_record(self):
        self.refresh_data() #Ensure we have latest data
        
        self.record_form_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.record_form_window.title("Create New Patient Record")
        self.record_form_window.geometry("425x525+625+225")
        
        fields = [
            ("Name:", "name"),
            ("Age:", "age"),
            ("Gender:", "gender"),
            ("Email:", "email"),
            ("Contact Number:", "contact_no"),
            ("Medical History:", "medical_history"),
            ("Allergies:", "allergies"),
            ("Current Medications:", "current_medications")
        ]
        
        self.entry_vars = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            tk.Label(self.record_form_window, text="New Patient Record", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=0, padx=5, pady=(20, 5), columnspan=2)

            tk.Label(self.record_form_window, text=label_text, font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=i+1, column=0, padx=(20, 5), pady=5, sticky='w')
            
            if field_name in ['medical_history', 'allergies', 'current_medications']:
                entry = tk.Text(self.record_form_window, height=4, width=GUI.textbox_width)
                entry.grid(row=i+1, column=1, padx=(5, 10), pady=5, sticky='w')
            else:
                entry = tk.Entry(self.record_form_window, width=GUI.entry_width)
                entry.grid(row=i+1, column=1, padx=(5, 10), pady=5, sticky='w')
                
            self.entry_vars[field_name] = entry
            
        button_frame = tk.Frame(self.record_form_window, bg=GUI.bg_color)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=(10, 5))
        
        tk.Button(button_frame, text="Save", command=self.save_new_patient, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=self.record_form_window.destroy, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        
    def save_new_patient(self):
        try:
            patient_data = {}
            user_data = {
                'role': 'Patient',
                'password': 'default_password'
            }
            
            for field_name, widget in self.entry_vars.items():
                if isinstance(widget, tk.Text):
                    value = widget.get("1.0", tk.END).strip()
                else:
                    value = widget.get().strip()
                    
                if field_name in ['name', 'age', 'gender', 'email', 'contact_no']:
                    user_data[field_name] = value
                else:
                    patient_data[field_name] = value
                    
            if not all(user_data.get(field) for field in ['name', 'age', 'gender', 'email']):
                messagebox.showerror("Error", "Please fill in all required fields!")
                return
                
            try:
                user_data['age'] = int(user_data['age'])
            except ValueError:
                messagebox.showerror("Error", "Age must be a number!")
                return
            
            print("\nDEBUG: Current patient IDs in system:")
            for p in self.patients:
                print(p['patient_id'])
                
            #Get the next patient ID
            new_patient_id = get_next_patient_id(self.patients)
            print(f"DEBUG: Generated new patient ID: {new_patient_id}")
            
            patient_record = {
                'patient_id': new_patient_id,
                'appointments': [],
                'medical_history': patient_data.get('medical_history', ''),
                'allergies': patient_data.get('allergies', ''),
                'current_medications': patient_data.get('current_medications', ''),
                'doctor_notes': '',
                'prescriptions': []
            }
            
            user_record = {
                'user_id': f"U{len(self.users)+1:04d}",
                'patient_id': new_patient_id,
                'username': user_data['email'],
                'password': (user_data.get('password', 'default_password')),
                'name': user_data['name'],
                'role': 'Patient',
                'age': user_data['age'],
                'gender': user_data['gender'],
                'email': user_data['email'],
                'contact_no': user_data.get('contact_no', ''),
                'security_question': 'What is your favorite color?', 
                'security_answer': 'blue' 
            }
            
            print("DEBUG: New patient record to be added:")
            print(patient_record)
            print("DEBUG: New user record to be added:")
            print(user_record)
            
            #Add to data
            self.patients.append(patient_record)
            self.users.append(user_record)
            
            #Save data
            db.save_data(self.patients, db.patients_file)
            db.save_data(self.users, db.users_file)
            
            print("DEBUG: Data saved. Reloading to verify...")
            test_patients = db.load_data(db.patients_file)
            print(f"DEBUG: Now {len(test_patients)} patients in system")
            
            messagebox.showinfo("Success", f"Patient record created successfully!\nPatient ID: {new_patient_id}")
            self.record_form_window.destroy()
            self.load_all_patients()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save patient record: {str(e)}")
            print(f"ERROR DETAILS: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def edit_patient_record(self):
        selected_item = self.record_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient record to edit.")
            return
        
        item = self.record_tree.item(selected_item)
        patient_id = item['text']
        
        patient = next((p for p in self.patients if p["patient_id"] == patient_id), None)
        user = next((u for u in self.users if u.get('patient_id') == patient_id and u['role'] == 'Patient'), None)
        
        if not patient or not user:
            messagebox.showerror("Error", "Patient record not found!")
            return
        
        self.edit_form_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.edit_form_window.title(f"Edit Patient Record - {patient_id}")
        self.edit_form_window.geometry("425x675+625+175")

        fields = [
            ("Name:", "name", user.get('name', '')),
            ("Age:", "age", user.get('age', '')),
            ("Gender:", "gender", user.get('gender', '')),
            ("Email:", "email", user.get('email', '')),
            ("Contact Number:", "contact_no", user.get('contact_no', '')),
            ("Medical History:", "medical_history", patient.get('medical_history', '')),
            ("Allergies:", "allergies", patient.get('allergies', '')),
            ("Current Medications:", "current_medications", patient.get('current_medications', ''))
        ]
        
        self.edit_entry_vars = {}
        
        for i, (label_text, field_name, default_value) in enumerate(fields):
            tk.Label(self.edit_form_window, text=f"Patient Record - {patient_id}", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, columnspan=2, padx=5, pady=(25, 5))

            tk.Label(self.edit_form_window, text=label_text, font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=i+1, column=0, padx=(25, 5), pady=5, sticky='w')
            
            if field_name in ['medical_history', 'allergies', 'current_medications']:
                entry = tk.Text(self.edit_form_window, height=4, width=GUI.textbox_width)
                entry.insert(tk.END, default_value)
                entry.grid(row=i+1, column=1, pady=5, sticky='w')
            else:
                entry = tk.Entry(self.edit_form_window, width=30)
                entry.insert(0, default_value)
                entry.grid(row=i+1, column=1, pady=5, sticky='w')
                
            self.edit_entry_vars[field_name] = entry
            
        if self.current_user['role'] in ['Admin', 'Doctor']:
            tk.Label(self.edit_form_window, text="Doctor's Notes:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=len(fields)+1, column=0, padx=(25, 5), pady=5, sticky='W')
            doctors_notes = tk.Text(self.edit_form_window, height=4, width=GUI.textbox_width)
            doctors_notes.insert(tk.END, patient.get('doctor_notes', ''))
            doctors_notes.grid(row=len(fields)+1, column=1, padx=(5, 0), pady=5, sticky='w')
            self.edit_entry_vars['doctors_notes'] = doctors_notes
            
            tk.Label(self.edit_form_window, text="Prescriptions:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=len(fields)+2, column=0, padx=(15, 5), pady=5, sticky='w')
            prescriptions = tk.Text(self.edit_form_window, height=4, width=GUI.textbox_width)
            prescriptions.insert(tk.END, patient.get('prescriptions', ''))
            prescriptions.grid(row=len(fields)+2, column=1, padx=(5, 0), pady=5, sticky='w')
            self.edit_entry_vars['prescriptions'] = prescriptions
            
        button_frame = tk.Frame(self.edit_form_window, bg=GUI.bg_color)
        button_frame.grid(row=len(fields)+3, column=0, columnspan=2, pady=(5, 10))
            
        tk.Button(button_frame, text="Save Changes", command=lambda: self.save_edited_patient(patient_id), font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=self.edit_form_window.destroy, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            
    def save_edited_patient(self, patient_id):
        try:
            patient = next((p for p in self.patients if p["patient_id"] == patient_id), None)
            user = next((u for u in self.users if u.get('patient_id') == patient_id and u['role'] == 'Patient'), None)
            
            if not patient or not user:
                messagebox.showerror("Error", "Patient record not found!")
                return
            
            for field_name in ['name', 'age', 'gender', 'email', 'contact_no']:
                if field_name in self.edit_entry_vars:
                    user[field_name] = self.edit_entry_vars[field_name].get().strip()
                    
            for field_name in ['medical_history', 'allergies', 'current_medications', 'doctor_notes', 'prescriptions']:
                if field_name in self.edit_entry_vars:
                    if field_name in ['doctor_notes', 'prescriptions'] and self.current_user['role'] not in ['Admin', 'Doctor']:
                        continue
                    
                    if isinstance(self.edit_entry_vars[field_name], tk.Text):
                        patient[field_name] = self.edit_entry_vars[field_name].get("1.0", tk.END).strip()
                    else:
                        patient[field_name] = self.edit_entry_vars[field_name].get().strip()
            
            # Debug prints
            print("Saving updated patient data:", patient)
            print("Saving updated user data:", user)
            
            db.save_data(self.patients, db.patients_file)
            db.save_data(self.users, db.users_file)
            
            messagebox.showinfo("Success", "Patient record updated successfully!")
            self.edit_form_window.destroy()
            self.load_all_patients()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update patient record: {str(e)}")
            print("Error:", e)
            import traceback
            traceback.print_exc()

    def view_patient_details(self):
        selected_item = self.record_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a patient record.")
            return

        item = self.record_tree.item(selected_item)
        patient_id = item['text']  # Use patient_id
        patient = next((p for p in self.patients if p["patient_id"] == patient_id), None)
        user = next((u for u in self.users if u["role"] == 'Patient' and u['patient_id'] == patient_id), None)

        if not user and not patient:
            messagebox.showerror("Error", "Patient not found!")
            return

        if patient:
            self.details_window = tk.Toplevel(self.root, bg=GUI.bg_color)
            self.details_window.title(f"Patient Details - {patient_id}")
            self.details_window.geometry("450x350+575+300")

            details_frame = tk.Frame(self.details_window, bg=GUI.bg_color)
            details_frame.pack(padx=20, fill='x')

            tk.Label(details_frame, text=f"Patient Details - {patient_id}", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, columnspan=2, pady=(15, 5), padx=5)

            tk.Label(details_frame, text="Patient ID:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=patient['patient_id'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=1, sticky='w')

            tk.Label(details_frame, text="Name:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=user['name'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=1, sticky='w')

            tk.Label(details_frame, text="Age:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=user['age'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=1, sticky='w')

            tk.Label(details_frame, text="Gender:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=user['gender'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=1, sticky='w')

            tk.Label(details_frame, text="Email:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=5, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=user['email'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=5, column=1, sticky='w')

            tk.Label(details_frame, text="Contact Number:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=6, column=0, sticky='w', padx=(20, 5))
            tk.Label(details_frame, text=user['contact_no'], font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=6, column=1, sticky='w')

            tk.Label(self.details_window, text="Appointments:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(10, 0))
            appt_text = tk.Text(self.details_window, height=5, width=50)
            appt_text.insert(tk.END, patient['appointments'])
            appt_text.config(state='disabled')
            appt_text.pack(pady=5, padx=10)
        else:
            messagebox.showerror("Error", "Patient details not found.")

    def logout(self):
        if self.logout_callback:
            self.logout_callback()
        
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
if __name__ == "__main__":
    root = tk.Tk()
    app = PatientRecordManagement(root)
    root.mainloop()