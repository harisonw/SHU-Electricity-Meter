import random
from datetime import datetime

import customtkinter as ctk


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success  # Callback when login is successful

        self.grid_columnconfigure(0, weight=1)  # Center the login elements
        self.grid_rowconfigure([0, 1, 2, 3], weight=1)

        # Client ID Label and Entry
        self.client_id_label = ctk.CTkLabel(self, text="Client ID:", font=("Arial", 14))
        self.client_id_label.grid(row=0, column=0, pady=(20, 5), padx=20, sticky="n")
        self.client_id_entry = ctk.CTkEntry(
            self, width=200, placeholder_text="Enter Client ID"
        )
        self.client_id_entry.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Password Label and Entry
        self.password_label = ctk.CTkLabel(self, text="Password:", font=("Arial", 14))
        self.password_label.grid(row=2, column=0, pady=(5, 5), padx=20, sticky="n")
        self.password_entry = ctk.CTkEntry(
            self, width=200, placeholder_text="Enter Password", show="*"
        )
        self.password_entry.grid(row=3, column=0, padx=20, pady=(0, 20))

        # Login Button
        self.login_button = ctk.CTkButton(
            self, text="Login", command=self.attempt_login
        )
        self.login_button.grid(row=4, column=0, pady=20)

    def attempt_login(self):
        client_id = self.client_id_entry.get()
        password = self.password_entry.get()

        # Dummy logic for client ID and password validation
        if client_id == "12345" and password == "password":
            self.on_login_success()  # Call the function to open the main UI
        else:
            self.show_error("Invalid Client ID or Password")

    def show_error(self, message):
        error_label = ctk.CTkLabel(
            self, text=message, font=("Arial", 12), text_color="red"
        )
        error_label.grid(row=5, column=0, pady=10)


class SmartMeterUI(ctk.CTkFrame):  # Now SmartMeterUI is a Frame, not a CTk window
    def __init__(self, master):
        super().__init__(master, fg_color="grey14")  # Set the frame background color

        # Configure Grid layout
        self.grid_columnconfigure(0, weight=1)  # Create a single column
        self.grid_rowconfigure(0, weight=1)  # Server Connection status section
        self.grid_rowconfigure(1, weight=3)  # Main display
        self.grid_rowconfigure(2, weight=1)  # Outage Notice section

        self.create_widgets()

    # Create UI components
    def create_widgets(self):
        self.create_connection_status()
        self.create_main_display()
        self.create_notice_section()
        self.update_time()

    def create_connection_status(self):
        self.connection_status_frame = ctk.CTkFrame(
            self, corner_radius=10, fg_color="grey17"
        )
        self.connection_status_frame.grid(
            row=0, column=0, padx=20, pady=10, sticky="nsew"
        )

        # Time label
        self.time_label = ctk.CTkLabel(
            self.connection_status_frame,
            text="11:11",
            font=("Arial", 12),
            text_color="white",
        )
        self.time_label.pack(side="top", anchor="ne", padx=10)

        # Connection status label
        self.connection_status_label = ctk.CTkLabel(
            self.connection_status_frame,
            text="Connecting to server...",
            font=("Arial", 14, "bold"),
            text_color="white",
        )
        self.connection_status_label.pack(pady=(0, 10))

    def create_main_display(self):
        self.middle_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="grey12")
        self.middle_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.amount_label = ctk.CTkLabel(
            self.middle_frame,
            text="£x.xx",
            font=("Arial", 36, "bold"),
            text_color="green",
        )
        self.amount_label.pack(pady=(20, 5))

        self.usage_label = ctk.CTkLabel(
            self.middle_frame,
            text="Used so far today: xx.xx kWh",
            font=("Arial", 16),
            text_color="white",
        )
        self.usage_label.pack(pady=(5, 0))

    def create_notice_section(self):
        self.notice_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="grey17")
        self.notice_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.notice_label = ctk.CTkLabel(
            self.notice_frame,
            text="No current notices",
            font=("Arial", 14, "bold"),
            text_color="white",
        )
        self.notice_label.pack(pady=10)

    def update_connection_status(self, status):
        if status == "connected":
            self.connection_status_label.configure(
                text="Connected to server", text_color="green"
            )
        if status == "error":
            self.connection_status_label.configure(
                text="Error: Failed to connect to server. Retrying...",
                text_color="gold",
            )

    def update_main_display(self, amount, usage):
        self.amount_label.configure(text=amount)
        self.usage_label.configure(text=f"Used so far today: {usage}")

    def update_notice_message(self, message):
        if message == "":
            message = "No current notices"
            self.notice_label.configure(text=message, text_color="grey")
        else:
            self.notice_label.configure(text=message, text_color="red")

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        self.time_label.configure(text=current_time)  # Update the time label
        self.after(1000, self.update_time)  # Update every second


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("600x300")
        self.title("Smart Meter Login")

        # Display login frame first
        self.login_frame = LoginFrame(self, self.open_main_ui)
        self.login_frame.pack(fill="both", expand=True)

    def open_main_ui(self):
        # Destroy the login frame
        self.login_frame.destroy()

        # Show the SmartMeterUI in the same window
        self.smart_meter_ui = SmartMeterUI(self)
        self.smart_meter_ui.pack(fill="both", expand=True)


# Main app with login and mock data
if __name__ == "__main__":
    app = MainApp()

    # Simulate server status message and other mock data after login
    def load_mock_data():
        app.smart_meter_ui.after(
            2000, lambda: app.smart_meter_ui.update_connection_status("connected")
        )
        app.smart_meter_ui.after(
            8000, lambda: app.smart_meter_ui.update_connection_status("error")
        )
        app.smart_meter_ui.after(
            3000, lambda: app.smart_meter_ui.update_main_display("£6.84", "54.63 kWh")
        )
        app.smart_meter_ui.after(
            5000,
            lambda: app.smart_meter_ui.update_notice_message(
                "Alert: Possible electricity grid problem detected."
            ),
        )

    # Load the mock data when the main UI opens
    app.bind("<Map>", lambda event: load_mock_data())

    app.mainloop()
