import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database as db
from gui import GUI

class AppointmentAndSchedulingSystem:   
    def __init__(self, root, current_user):
        self.root = root
        self.root.title("Appointment and Scheduling System")
        self.current_user = current_user
        
        self.GUI = GUI(self.root)

        self.logout_callback = None
        self.return_to_dashboard_callback = None
        self.show_patient_records_callback = None
        self.show_user_management_callback = None
        
        db.initialize_data_files()
        self.users = db.load_data(db.users_file)
        self.patients = db.load_data(db.patients_file)
        self.appointments = db.load_data(db.appointments_file)
        
        self.root.configure(bg=GUI.bg_color)
        self.root.geometry('1000x600+350+200')

        self.nav_frame = tk.Frame(root, bg=GUI.bg_color)
        self.nav_frame.pack(fill='x', pady=(20, 15), padx=15)
        
        if current_user['role'] == 'Admin':
            tk.Button(self.nav_frame, text="Dashboard", command=self.return_to_dashboard, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            tk.Button(self.nav_frame, text="User Management", command=self.show_user_management, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            
        tk.Button(self.nav_frame, text="Patient Records", command=self.show_patient_records, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)

        tk.Button(self.nav_frame, text="Logout", command=self.logout, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='right')
        
        self.dashboard_content = tk.Frame(root, bg=GUI.bg_color)
        self.dashboard_content.pack(fill='both', expand=True)
        
        self.show_appointments()
        
    def show_user_management(self):
        if self.show_user_management_callback:
            self.show_user_management_callback()
        elif self.return_to_dashboard_callback:
            self.return_to_dashboard_callback()
            
    def show_patient_records(self):
        if self.show_patient_records_callback:
            self.show_patient_records_callback()
        elif self.return_to_dashboard_callback: 
            self.return_to_dashboard_callback()
            
    def return_to_dashboard(self):
        if self.return_to_dashboard_callback:
            self.return_to_dashboard_callback()
        
    def logout(self):
        if self.logout_callback:
            self.logout_callback()

    def show_appointments(self):
        for widget in self.dashboard_content.winfo_children():
            widget.destroy()
            
        tk.Label(self.dashboard_content, text="Appointment Management", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 5))
            
            #Options frame
        option_frame = tk.Frame(self.dashboard_content, bg=GUI.bg_color)
        option_frame.pack(fill='x', pady=(10, 5), padx=15)
            
        tk.Label(option_frame, text="Filter by:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color
).pack(side='left', padx=(0, 5))
        self.appt_filter = ttk.Combobox(option_frame, values=["All", "Today", "Upcoming", "Past", "Pending", "Confirmed", "Cancelled"], width=GUI.combo_width)
        self.appt_filter.pack(side='left', padx=5)
        self.appt_filter.current(0)
            
        tk.Button(option_frame, text="Apply Filter", command=self.filter_appointments, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            
        if self.current_user['role'] in ['Doctor', 'Nurse']:
            tk.Button(option_frame, text="Doctor Schedule", command=self.show_doctor_schedule, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
        
        #Treeview to display appointments
        tree_frame = tk.Frame(self.dashboard_content, padx=15, bg=GUI.bg_color)
        tree_frame.pack(fill='both', expand=True)
            
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
            
        columns = ('patient', 'doctor', 'date', 'time', 'reason', 'status')
        self.appt_tree = ttk.Treeview(tree_frame, columns=columns, yscrollcommand=scrollbar.set)
        self.appt_tree.pack(fill='both', expand=True)
            
        scrollbar.config(command=self.appt_tree.yview)
            
        #Configure columns
        self.appt_tree.heading('#0', text='Appt ID')
        self.appt_tree.column('#0', width=80)
            
        for col in columns:
            self.appt_tree.heading(col, text=col.capitalize())
            self.appt_tree.column(col, width=120)
                
        #Add appointments to treeview
        self.load_all_appointments()
            
        #Buttons
        btn_frame = tk.Frame(self.dashboard_content, bg=GUI.bg_color)
        btn_frame.pack(pady=(5, 15))

        tk.Button(btn_frame, text="View Details", command=self.view_appointment_details, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)

        if self.current_user['role'] in ['Admin', 'Nurse', 'Patient']:
            tk.Button(btn_frame, text="Book New Appointment", command=self.show_book_appointments, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Reschedule Appointment", command=self.show_reschedule_appointments, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
            tk.Button(btn_frame, text="Cancel Appointment", command=self.cancel_appointment, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)

            if self.current_user['role'] == 'Nurse':
                tk.Button(btn_frame, text="Update Status", command=self.show_update_appointment_status, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(side='left', padx=5)
                    
    def load_all_appointments(self):
        self.appt_tree.delete(*self.appt_tree.get_children())
    
        today = datetime.now().strftime("%Y-%m-%d")
        
        for appt in self.appointments:
            try:
                # Find patient user
                patient_user = None
                for user in self.users:
                    if 'patient_id' in user and user['patient_id'] == appt.get('patient_id'):
                        patient_user = user
                        break
                        
                if not patient_user:
                    continue
                    
                # Role-based filtering
                if self.current_user['role'] == 'Patient':
                    if 'patient_id' not in self.current_user or appt['patient_id'] != self.current_user.get('patient_id'):
                        continue
                elif self.current_user['role'] == 'Doctor':
                    if appt['doctor'] != self.current_user['name']:
                        continue
                        
                # Add to treeview
                self.appt_tree.insert('', 'end', text=appt['appt_id'],
                                    values=(patient_user.get('name', 'Unknown'), 
                                        appt.get('doctor', 'Unknown'), 
                                        appt.get('date', 'Unknown'), 
                                        appt.get('time', 'Unknown'), 
                                        appt.get('reason', 'Unknown'), 
                                        appt.get('status', 'Unknown')))
            except KeyError as e:
                print(f"Error loading appointment {appt.get('appt_id', 'Unknown')}: {e}")
                continue

    def filter_appointments(self):
        filter_by = self.appt_filter.get()
        self.appt_tree.delete(*self.appt_tree.get_children())
        
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now().strftime("%H:%M")
        
        for appt in self.appointments:
            try:
                # Find patient user
                patient_user = None
                for user in self.users:
                    if 'patient_id' in user and user['patient_id'] == appt.get('patient_id'):
                        patient_user = user
                        break
                
                if not patient_user:
                    continue
                    
                # Role-based filtering
                if self.current_user['role'] == 'Patient':
                    if 'patient_id' not in self.current_user or appt['patient_id'] != self.current_user.get('patient_id'):
                        continue
                elif self.current_user['role'] == 'Doctor':
                    if appt.get('doctor') != self.current_user.get('name'):
                        continue
                
                appt_datetime = datetime.strptime(f"{appt.get('date', '1970-01-01')} {appt.get('time', '00:00')}", "%Y-%m-%d %H:%M")
                current_datetime = datetime.now()
                
                if filter_by == "All":
                    pass
                elif filter_by == "Today" and appt.get('date') != today:
                    continue
                elif filter_by == "Upcoming" and appt_datetime <= current_datetime:
                    continue
                elif filter_by == "Past" and appt_datetime > current_datetime:
                    continue
                elif filter_by == "Pending" and appt.get('status') != "Pending":
                    continue
                elif filter_by == "Confirmed" and appt.get('status') != "Confirmed":
                    continue
                elif filter_by == "Cancelled" and appt.get('status') != "Cancelled":
                    continue
                
                self.appt_tree.insert('', 'end', text=appt.get('appt_id', 'Unknown'),
                                    values=(patient_user.get('name', 'Unknown'), 
                                        appt.get('doctor', 'Unknown'), 
                                        appt.get('date', 'Unknown'), 
                                        appt.get('time', 'Unknown'), 
                                        appt.get('reason', 'Unknown'), 
                                        appt.get('status', 'Unknown')))
            except Exception as e:
                print(f"Error filtering appointment: {e}")
                continue
            
    #Doctor's schedule
    def show_doctor_schedule(self):
        if self.current_user['role'] not in ['Doctor', 'Nurse']:
            return
        
        self.appt_filter.current(0) #Resets filter to "All"
        
        #Nurses can select a doctor
        if self.current_user['role'] == 'Nurse':
            doctors = [user['name'] for user in self.users if user['role'] == 'Doctor']
            
            self.doctor_selection = ttk.Combobox(self.dashboard_content, values=doctors)
            self.doctor_selection.pack(pady=5)
            self.doctor_selection.bind("<<ComboboxSelected>>", self.filter_by_doctor)
        else:
            self.filter_appointments()

    #Filters appointments based on selected doctor
    def filter_by_doctor(self, event=None):
        doctor_name = self.doctor_selection.get()
        self.appt_tree.delete(*self.appt_tree.get_children())
        
        for appt in self.appointments:
            try:
                if appt.get('doctor') != doctor_name:
                    continue
                    
                patient = next((p for p in self.patients if p.get('patient_id') == appt.get('patient_id')), None)
                if not patient:
                    continue
                    
                user = next((u for u in self.users if u.get('role') == 'Patient' and u.get('patient_id') == patient.get('patient_id')), None)
                if not user:
                    continue

                self.appt_tree.insert('', 'end', text=appt.get('appt_id', 'Unknown'),
                                    values=(user.get('name', 'Unknown'), 
                                        appt.get('doctor', 'Unknown'), 
                                        appt.get('date', 'Unknown'), 
                                        appt.get('time', 'Unknown'), 
                                        appt.get('reason', 'Unknown'), 
                                        appt.get('status', 'Unknown')))
            except Exception as e:
                print(f"Error filtering by doctor: {e}")
                continue
                
    def show_book_appointments(self):
        self.book_appt_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.book_appt_window.title("Book New Appointment")
        self.book_appt_window.geometry("450x500+600+225")

        form_frame = tk.Frame(self.book_appt_window, bg=GUI.bg_color)
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Book Appointment", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, columnspan=2, padx=5, pady=(5, 10))

        #Name
        tk.Label(form_frame, text="Patient's Full Name:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=0, padx=5, pady=5)
        self.appt_name = tk.Entry(form_frame, width=GUI.entry_width)
        self.appt_name.grid(row=1, column=1, padx=5, pady=5)

        #Doctor selection
        tk.Label(self.book_appt_window, text="Select Doctor:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        doctors = [user['name'] for user in db.load_data(db.users_file) if user['role'] == 'Doctor']
        self.appt_doctor = ttk.Combobox(self.book_appt_window, values=doctors, width=GUI.combo_width)
        self.appt_doctor.pack(pady=5)
        
        #Date selection
        tk.Label(self.book_appt_window, text="Date:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        self.appt_date = tk.Entry(self.book_appt_window, width=GUI.entry_width)
        self.appt_date.pack(pady=5)
        
        #Time selection
        tk.Label(self.book_appt_window, text="Time:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        self.appt_time = ttk.Combobox(self.book_appt_window,
                                    values=[f"{h:02d}:{m:02d}" for h in range(9, 17) for m in [0, 30]], width=GUI.combo_width)
        self.appt_time.pack(pady=5)
        
        #Reason
        tk.Label(self.book_appt_window, text="Reason:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        self.appt_reason = tk.Text(self.book_appt_window, height=5, width=GUI.textbox_width)
        self.appt_reason.pack(pady=5)
        
        #Submit button
        tk.Button(self.book_appt_window, text="Submit", command=self.book_appointment, font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(pady=10)
        
    def book_appointment(self):
        name = self.appt_name.get()
        doctor = self.appt_doctor.get()
        date = self.appt_date.get()
        time = self.appt_time.get()
        reason = self.appt_reason.get("1.0", tk.END).strip()
        
        #Validation
        if not all([name, doctor, date, time, reason]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        #Find the patient user
        patient_user = None
        for user in self.users:
            if user['name'] == name and user['role'] == 'Patient':
                patient_user = user
                break
                
        if not patient_user:
            messagebox.showerror("Error", "Patient not found!")
            return
        
        #Find the patient record
        patient = next((p for p in self.patients if p.get('patient_id') == patient_user.get('patient_id')), None)
        if not patient:
            messagebox.showerror("Error", "Patient record not found!")
            return
        
        #Check for time slot availability
        for appt in self.appointments:
            if (appt['doctor'] == doctor and 
                appt['date'] == date and 
                appt['time'] == time and 
                appt['status'] != 'Cancelled'):
                messagebox.showerror("Error", "This time slot is already booked!")
                return
        
        #Create new appointment
        new_appt = {
            "appt_id": f"A{len(self.appointments)+1:04d}",
            "patient_id": patient_user['patient_id'],
            "doctor": doctor,
            "date": date,
            "time": time,
            "reason": reason,
            "status": "Pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        #Add to appointments
        self.appointments.append(new_appt)
        db.save_data(self.appointments, db.appointments_file)
            
        #Add to patient's record
        if 'appointments' not in patient:
            patient['appointments'] = []
        patient['appointments'].append(new_appt['appt_id'])
        db.save_data(self.patients, db.patients_file)
        
        messagebox.showinfo("Success", "Appointment booked successfully!")
        self.book_appt_window.destroy()
        self.show_appointments()

    def show_reschedule_appointments(self):
        selected_item = self.appt_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment!")
            return
        
        item = self.appt_tree.item(selected_item)
        appt_id = item['text']
        doctor = item['text']
        
        self.resched_appt_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.resched_appt_window.title("Reschedule Appointment Date")
        self.resched_appt_window.geometry("450x275+625+325")
        
        tk.Label(self.resched_appt_window, text="Reschedule Appointment", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 10))

        #Date Selection
        tk.Label(self.resched_appt_window, text="Date:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        self.resched_appt_date = tk.Entry(self.resched_appt_window, width=GUI.entry_width)
        self.resched_appt_date.pack(pady=5)

        #Time selection
        tk.Label(self.resched_appt_window, text="Time:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        self.resched_appt_time = ttk.Combobox(self.resched_appt_window,
                                    values=[f"{h:02d}:{m:02d}" for h in range(9, 17) for m in [0, 30]], width=GUI.combo_width)
        self.resched_appt_time.pack(pady=5)
        
        tk.Button(self.resched_appt_window, text="Reschedule", command=lambda: self.reschedule_appointment(appt_id, doctor), font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(pady=10)

    def reschedule_appointment(self, appt_id, doctor):
        new_date = self.resched_appt_date.get()
        new_time = self.resched_appt_time.get()
        
        if not new_date:
            messagebox.showerror("Error", "Please set a date!")
            return
        elif not new_time:
            messagebox.showerror("Error", "Please set a time!")
            return
        if not new_date and not new_time:
            messagebox.showerror("Error", "Please set a time and date!")
            return
        
        for appt in self.appointments:
            if appt['doctor'] == doctor and appt['date'] == new_date and appt['time'] == new_time: 
                messagebox.showerror("Error", "This time slot is already booked!")
                return

        for idx, appt in enumerate(self.appointments):
            if appt['appt_id'] == appt_id:
                self.appointments[idx]['date'] = new_date
                self.appointments[idx]['time'] = new_time
                break

        db.save_data(self.appointments, db.appointments_file)
        messagebox.showinfo("Success", "Status updated successfully!")
        self.update_status_window.destroy()
        self.show_appointments() 

    def view_appointment_details(self):
        selected_item = self.appt_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment!")
            return
        
        try:
            item = self.appt_tree.item(selected_item)
            appt_id = item['text']
            
            appointment = next((a for a in self.appointments if a.get('appt_id') == appt_id), None)
            if not appointment:
                messagebox.showerror("Error", "Appointment not found!")
                return
                
            patient = next((p for p in self.patients if p.get('patient_id') == appointment.get('patient_id')), None)
            if not patient:
                messagebox.showerror("Error", "Patient record not found!")
                return
                
            user = next((u for u in self.users if u.get('role') == 'Patient' and u.get('patient_id') == patient.get('patient_id')), None)
            if not user:
                messagebox.showerror("Error", "User record not found!")
                return
            
            self.view_appt_window = tk.Toplevel(self.root, bg=GUI.bg_color)
            self.view_appt_window.title(f"Appointment Details - {appt_id}")
            self.view_appt_window.geometry("450x325+625+300")
            
            # Display appointment details with proper error handling
            tk.Label(self.view_appt_window, text=f"Appointment ID: {appointment.get('appt_id', 'Unknown')}", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(10, 5))
            
            details_frame = tk.Frame(self.view_appt_window, bg=GUI.bg_color)
            details_frame.pack(pady=(0, 10), padx=15, fill='x')
            
            # Use .get() with default values for all dictionary accesses
            tk.Label(details_frame, text="Patient:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=0, sticky='w', padx=(15, 0))
            tk.Label(details_frame, text=user.get('name', 'Unknown'), anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=0, column=1, sticky='w')
            
            tk.Label(details_frame, text="Doctor:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=0, sticky='w', padx=(15, 0))
            tk.Label(details_frame, text=appointment.get('doctor', 'Unknown'), anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=1, column=1, sticky='w')
            
            tk.Label(details_frame, text="Date:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=0, sticky='w', padx=(15, 0))
            tk.Label(details_frame, text=appointment.get('date', 'Unknown'), anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=2, column=1, sticky='w')
            
            tk.Label(details_frame, text="Time:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=0, sticky='w', padx=(15, 0))
            tk.Label(details_frame, text=appointment.get('time', 'Unknown'), anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=3, column=1, sticky='w')
            
            tk.Label(details_frame, text="Status:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=0, sticky='w', padx=(15, 0))
            tk.Label(details_frame, text=appointment.get('status', 'Unknown'), anchor='w', font=self.GUI.text_font, bg=GUI.bg_color, fg=GUI.label_color).grid(row=4, column=1, sticky='w')
            
            tk.Label(self.view_appt_window, text="Reason:", anchor='w', font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(10, 0))
            reason_text = tk.Text(self.view_appt_window, height=5, width=50, font=self.GUI.text_font, fg=GUI.label_color)
            reason_text.insert(tk.END, appointment.get('reason', 'No reason provided'))
            reason_text.config(state='disabled')
            reason_text.pack(pady=5, padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view appointment details: {str(e)}")
            print(f"Error viewing appointment details: {e}")
        
    def show_update_appointment_status(self):
        selected_item = self.appt_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment!")
            return
        
        item = self.appt_tree.item(selected_item)
        appt_id = item['text']
        
        self.update_status_window = tk.Toplevel(self.root, bg=GUI.bg_color)
        self.update_status_window.title("Update Appointment Status")
        self.update_status_window.geometry("350x275+650+350")
        
        tk.Label(self.update_status_window, text="Update Status", font=self.GUI.header1_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=(20, 0))

        tk.Label(self.update_status_window, text="Select new status:", font=self.GUI.header2_font, bg=GUI.bg_color, fg=GUI.label_color).pack(pady=5)
        
        self.new_status = ttk.Combobox(self.update_status_window,
                                    values=["Pending", "Confirmed", "Cancelled", "Completed"], width=GUI.combo_width)
        self.new_status.pack(pady=5)
        
        tk.Button(self.update_status_window, text="Update", command=lambda: self.update_appointment_status(appt_id), font=self.GUI.button_font, bg=GUI.button_color, fg=GUI.button_label_color).pack(pady=(10, 20))
        
    def update_appointment_status(self, appt_id):
        new_status = self.new_status.get()
        
        if not new_status:
            messagebox.showerror("Error", "Please select a status!")
            return
        
        for idx, appt in enumerate(self.appointments):
            if appt['appt_id'] == appt_id:
                self.appointments[idx]['status'] = new_status
                break
        
        db.save_data(self.appointments, db.appointments_file)
        messagebox.showinfo("Success", "Status updated successfully!")
        self.update_status_window.destroy()
        self.show_appointments()
        
    def cancel_appointment(self):
        selected_item = self.appt_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment!")
            return
        
        item = self.appt_tree.item(selected_item)
        appt_id = item['text']
        
        if not messagebox.askyesno("Confirm", "Cancel this appointment?"):
            return
        
        for idx, appt in enumerate(self.appointments):
            if appt['appt_id'] == appt_id:
                self.appointments[idx]['status'] = "Cancelled"
                break
            
        db.save_data(self.appointments, db.appointments_file)
        messagebox.showinfo("Success", "Appointment cancelled!")
        self.show_appointments()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = AppointmentAndSchedulingSystem(root)
    root.mainloop()