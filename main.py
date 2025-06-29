import tkinter as tk
from tkinter import messagebox, font
from user_authentication import UserAuthentication
from user_management import UserManagementSystem
from appt_and_sched import AppointmentAndSchedulingSystem
from patient_records import PatientRecordManagement
from gui import GUI

class MainApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hospital Management System")
        self.current_user = None

        self.GUI = GUI(self.root)

        self.root.configure(bg=GUI.bg_color)

        self.show_login()
        
    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.auth_system = UserAuthentication(self.root)
        self.auth_system.login_success_callback = self.on_login_success
        
    def on_login_success(self):
        self.current_user = self.auth_system.current_user
        self.show_dashboard()
            
    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if self.current_user['role'] == "Admin":
            self.show_admin_dashboard()
        elif self.current_user['role'] in ['Doctor', 'Nurse', 'Patient']:
            self.show_staff_patient_dashboard()
        else:
            messagebox.showerror("Error", "Unknown user role")
            self.show_login()
            
    def show_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry('500x250+575+300')
        self.root.resizable(False, False)
            
        tk.Label(self.root, text=f"Welcome Admin: {self.current_user['name']}", 
                font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(30, 15))
        
        btn_frame = tk.Frame(self.root, bg=GUI.bg_color)
        btn_frame.pack(pady=(30, 15))
        
        if self.current_user['role'] in ['Admin']:
            tk.Button(btn_frame, text="User Management", 
                    command=lambda: self.show_system(UserManagementSystem),
                    bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
            
        tk.Button(btn_frame, text="Patient Records", 
                command=lambda: self.show_system(PatientRecordManagement),
                bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
        tk.Button(btn_frame, text="Appointments", 
                command=lambda: self.show_system(AppointmentAndSchedulingSystem),
                bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
        
        tk.Button(self.root, text="Logout", command=self.show_login,
                bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(pady=20)
        
    def show_staff_patient_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry('500x250+575+300')
        self.root.resizable(False, False)

        role = self.current_user['role']
        tk.Label(self.root, text=f"Welcome {role}: {self.current_user['name']}", 
                font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(30, 15))
        
        btn_frame = tk.Frame(self.root, bg=GUI.bg_color)
        btn_frame.pack(pady=(30, 15))
        
        if role in ['Doctor', 'Nurse']:
            tk.Button(btn_frame, text="Patient Records", 
                    command=lambda: self.show_system(PatientRecordManagement),
                    bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="Appointments", 
                command=lambda: self.show_system(AppointmentAndSchedulingSystem),
                bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
        
        if role == 'Patient':
            tk.Button(btn_frame, text="My Records", 
                    command=lambda: self.show_system(PatientRecordManagement),
                    bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(side='left', padx=10)
            
        tk.Button(self.root, text="Logout", command=self.show_login,
                bg=GUI.button_color, fg=GUI.button_label_color, font=self.GUI.button_font).pack(pady=20)
        
    def show_system(self, system_class):
        for widget in self.root.winfo_children():
            widget.destroy()
    
        system = system_class(self.root, self.current_user)
        
        system.logout_callback = self.show_login
        system.return_to_dashboard_callback = self.show_dashboard
        
        if isinstance(system, UserManagementSystem):
            system.show_patient_records_callback = lambda: self.show_system(PatientRecordManagement)
            system.show_appointments_callback = lambda: self.show_system(AppointmentAndSchedulingSystem)
        elif isinstance(system, PatientRecordManagement):
            system.show_user_management_callback = lambda: self.show_system(UserManagementSystem)
            system.show_appointments_callback = lambda: self.show_system(AppointmentAndSchedulingSystem)
        elif isinstance(system, AppointmentAndSchedulingSystem):
            system.show_user_management_callback = lambda: self.show_system(UserManagementSystem)
            system.show_patient_records_callback = lambda: self.show_system(PatientRecordManagement)
        
    def run(self):
        self.root.mainloop()
        
if __name__ == "__main__":
    app = MainApplication()
    app.run()