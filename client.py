import random
from datetime import datetime

import customtkinter as ctk


class SmartMeterUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance and theme
        self.title("Smart Meter Interface")
        self.geometry("600x300")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

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


# Main app with mock data
if __name__ == "__main__":
    app = SmartMeterUI()

    # Simulate server status message
    app.after(2000, lambda: app.update_connection_status("connected"))
    app.after(8000, lambda: app.update_connection_status("error"))

    # Simulate main display data
    app.after(3000, lambda: app.update_main_display("£6.84", "54.63 kWh")),

    # Simulate notice message
    app.after(
        5000,
        lambda: app.update_notice_message(
            "Alert: Possible electricity grid problem detected."
        ),
    )

    app.mainloop()
