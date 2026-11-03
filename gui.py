#!/usr/bin/env python3
"""
RideEase GUI — Modern Vehicle Rental Management System
Built with CustomTkinter for native macOS / cross-platform desktop UI.
Synchronized with data/vehicles.txt, data/customers.txt, and data/rentals.txt.
"""

import os
import sys
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Set styling
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------
# Data Persistence Layer (Matches DataStore.cpp)
# ---------------------------------------------------------
class Vehicle:
    def __init__(self, v_type, vid, model, price, spec1, spec2, available=True):
        self.type = v_type # "Car" or "Bike"
        self.id = vid
        self.model = model
        self.price = float(price)
        self.spec1 = int(spec1) # Car: seats; Bike: engineCC
        self.spec2 = bool(int(spec2)) if isinstance(spec2, (int, str)) and str(spec2).isdigit() else bool(spec2) # Car: automatic; Bike: helmetIncluded
        self.available = bool(int(available)) if isinstance(available, (int, str)) and str(available).isdigit() else bool(available)

    def calculate_charge(self, days):
        return self.price * days

    def serialize(self):
        s1 = self.spec1
        s2 = 1 if self.spec2 else 0
        av = 1 if self.available else 0
        clean_id = self.id.replace("|", "/")
        clean_model = self.model.replace("|", "/")
        return f"{self.type}|{clean_id}|{clean_model}|{self.price:.2f}|{s1}|{s2}|{av}"


class Customer:
    def __init__(self, username, password, name, phone, email):
        self.username = username
        self.password = password
        self.name = name
        self.phone = phone
        self.email = email

    def verify_password(self, password):
        return self.password == password

    def serialize(self):
        return f"{self.username}|{self.password}|{self.name}|{self.phone}|{self.email}"


class Rental:
    def __init__(self, rental_id, username, vehicle_id, v_type, model, days, price, total, rent_date, return_date, status):
        self.rental_id = rental_id
        self.username = username
        self.vehicle_id = vehicle_id
        self.vehicle_type = v_type
        self.vehicle_model = model
        self.days = int(days)
        self.price_per_day = float(price)
        self.total_charge = float(total)
        self.rent_date = rent_date
        self.return_date = return_date
        self.status = status # "ACTIVE" or "RETURNED"

    def is_active(self):
        return self.status == "ACTIVE"

    def mark_returned(self, ret_date):
        self.return_date = ret_date
        self.status = "RETURNED"

    def serialize(self):
        return f"{self.rental_id}|{self.username}|{self.vehicle_id}|{self.vehicle_type}|{self.vehicle_model}|{self.days}|{self.price_per_day:.2f}|{self.total_charge:.2f}|{self.rent_date}|{self.return_date}|{self.status}"


class DataStore:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.vehicles = []
        self.customers = []
        self.rentals = []
        self.ensure_files()
        self.load()

    def ensure_files(self):
        os.makedirs(self.data_dir, exist_ok=True)
        v_path = os.path.join(self.data_dir, "vehicles.txt")
        if not os.path.exists(v_path):
            with open(v_path, "w") as f:
                f.write(
                    "Car|C101|Maruti Swift|1800.00|5|0|1\n"
                    "Car|C102|Hyundai i20|2200.00|5|1|1\n"
                    "Bike|B101|Honda Activa 6G|700.00|110|1|1\n"
                    "Bike|B102|Royal Enfield Classic 350|1200.00|350|0|1\n"
                )
        c_path = os.path.join(self.data_dir, "customers.txt")
        if not os.path.exists(c_path):
            open(c_path, "a").close()
        r_path = os.path.join(self.data_dir, "rentals.txt")
        if not os.path.exists(r_path):
            open(r_path, "a").close()

    def load(self):
        self.vehicles = []
        self.customers = []
        self.rentals = []

        # Load vehicles
        v_path = os.path.join(self.data_dir, "vehicles.txt")
        if os.path.exists(v_path):
            with open(v_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    if len(parts) == 7:
                        try:
                            self.vehicles.append(Vehicle(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]))
                        except Exception:
                            pass

        # Load customers
        c_path = os.path.join(self.data_dir, "customers.txt")
        if os.path.exists(c_path):
            with open(c_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    if len(parts) == 5:
                        self.customers.append(Customer(parts[0], parts[1], parts[2], parts[3], parts[4]))

        # Load rentals
        r_path = os.path.join(self.data_dir, "rentals.txt")
        if os.path.exists(r_path):
            with open(r_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    if len(parts) == 11:
                        try:
                            self.rentals.append(Rental(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7], parts[8], parts[9], parts[10]))
                        except Exception:
                            pass

        self.reconcile_availability()

    def reconcile_availability(self):
        for v in self.vehicles:
            v.available = True
        for r in self.rentals:
            if r.is_active():
                v = self.find_vehicle(r.vehicle_id)
                if v:
                    v.available = False

    def save_all(self):
        try:
            with open(os.path.join(self.data_dir, "vehicles.txt"), "w") as f:
                for v in self.vehicles:
                    f.write(v.serialize() + "\n")
            with open(os.path.join(self.data_dir, "customers.txt"), "w") as f:
                for c in self.customers:
                    f.write(c.serialize() + "\n")
            with open(os.path.join(self.data_dir, "rentals.txt"), "w") as f:
                for r in self.rentals:
                    f.write(r.serialize() + "\n")
            return True
        except Exception as e:
            print("Error saving:", e)
            return False

    def find_vehicle(self, vid):
        for v in self.vehicles:
            if v.id == vid:
                return v
        return None

    def find_customer(self, username):
        for c in self.customers:
            if c.username == username:
                return c
        return None

    def find_rental(self, rental_id):
        for r in self.rentals:
            if r.rental_id == rental_id:
                return r
        return None

    def next_rental_id(self):
        next_num = 1
        prefix = "RENT-"
        for r in self.rentals:
            if r.rental_id.startswith(prefix):
                try:
                    num = int(r.rental_id[len(prefix):])
                    if num >= next_num:
                        next_num = num + 1
                except ValueError:
                    pass
        return f"RENT-{next_num:03d}"


# ---------------------------------------------------------
# Modern GUI Main Application
# ---------------------------------------------------------
class RideEaseGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RideEase — Vehicle Rental Management System")
        self.geometry("1100x720")
        self.minsize(980, 640)

        # State
        self.store = DataStore("data")
        self.current_user = None # None (guest), Customer object, or "ADMIN"
        self.admin_creds = ("admin", "admin123")
        self.filter_type = "All" # "All", "Car", "Bike"
        self.filter_avail = False

        self.setup_layout()
        self.show_browse_view()

    def setup_layout(self):
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ----------------- SIDEBAR -----------------
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🚗 RideEase",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 4), sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Rental Management System",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        # User Card
        self.user_card = ctk.CTkFrame(self.sidebar, corner_radius=10, fg_color=("gray85", "gray20"))
        self.user_card.grid(row=2, column=0, padx=15, pady=(0, 20), sticky="ew")

        self.user_role_label = ctk.CTkLabel(
            self.user_card,
            text="👤 Guest Mode",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.user_role_label.pack(padx=12, pady=(10, 2), anchor="w")

        self.user_info_label = ctk.CTkLabel(
            self.user_card,
            text="Log in to rent vehicles",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.user_info_label.pack(padx=12, pady=(0, 10), anchor="w")

        # Nav Buttons
        self.nav_browse_btn = ctk.CTkButton(
            self.sidebar,
            text="🚘  Browse Fleet",
            height=36,
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.show_browse_view
        )
        self.nav_browse_btn.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.nav_my_rentals_btn = ctk.CTkButton(
            self.sidebar,
            text="📋  My Rentals",
            height=36,
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.show_my_rentals_view
        )
        # Will be shown when customer logs in

        self.nav_profile_btn = ctk.CTkButton(
            self.sidebar,
            text="👤  My Profile",
            height=36,
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.show_profile_view
        )

        self.nav_admin_vehicles_btn = ctk.CTkButton(
            self.sidebar,
            text="⚙️  Manage Fleet",
            height=36,
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.show_admin_vehicles_view
        )

        self.nav_admin_rentals_btn = ctk.CTkButton(
            self.sidebar,
            text="📊  All Rentals",
            height=36,
            anchor="w",
            font=ctk.CTkFont(size=14),
            command=self.show_admin_rentals_view
        )

        self.nav_auth_btn = ctk.CTkButton(
            self.sidebar,
            text="🔐  Login / Register",
            height=36,
            anchor="w",
            fg_color=("dodgerblue3", "dodgerblue"),
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.show_auth_view
        )
        self.nav_auth_btn.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        # Sidebar Footer
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Appearance:", font=ctk.CTkFont(size=11), text_color="gray")
        self.theme_label.grid(row=10, column=0, padx=20, pady=(10, 0), sticky="w")

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=ctk.set_appearance_mode,
            height=28
        )
        self.theme_menu.grid(row=11, column=0, padx=15, pady=(4, 20), sticky="ew")

        # ----------------- MAIN VIEW CONTAINER -----------------
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def update_sidebar_state(self):
        # Reset nav buttons
        self.nav_my_rentals_btn.grid_forget()
        self.nav_profile_btn.grid_forget()
        self.nav_admin_vehicles_btn.grid_forget()
        self.nav_admin_rentals_btn.grid_forget()

        if self.current_user is None:
            self.user_role_label.configure(text="👤 Guest Mode")
            self.user_info_label.configure(text="Log in to rent vehicles")
            self.nav_auth_btn.configure(
                text="🔐  Login / Register",
                fg_color=("dodgerblue3", "dodgerblue"),
                command=self.show_auth_view
            )
            self.nav_auth_btn.grid(row=4, column=0, padx=15, pady=6, sticky="ew")
        elif self.current_user == "ADMIN":
            self.user_role_label.configure(text="🛡️ Administrator")
            self.user_info_label.configure(text="Full System Access")
            self.nav_admin_vehicles_btn.grid(row=4, column=0, padx=15, pady=6, sticky="ew")
            self.nav_admin_rentals_btn.grid(row=5, column=0, padx=15, pady=6, sticky="ew")
            self.nav_auth_btn.configure(
                text="🚪  Logout Admin",
                fg_color=("gray60", "gray35"),
                command=self.logout
            )
            self.nav_auth_btn.grid(row=6, column=0, padx=15, pady=6, sticky="ew")
        else: # Customer instance
            self.user_role_label.configure(text=f"👤 {self.current_user.name}")
            self.user_info_label.configure(text=f"@{self.current_user.username}")
            self.nav_my_rentals_btn.grid(row=4, column=0, padx=15, pady=6, sticky="ew")
            self.nav_profile_btn.grid(row=5, column=0, padx=15, pady=6, sticky="ew")
            self.nav_auth_btn.configure(
                text="🚪  Logout",
                fg_color=("gray60", "gray35"),
                command=self.logout
            )
            self.nav_auth_btn.grid(row=6, column=0, padx=15, pady=6, sticky="ew")

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def logout(self):
        self.current_user = None
        self.update_sidebar_state()
        self.show_browse_view()
        messagebox.showinfo("Logged Out", "You have been logged out successfully.")

    # ---------------------------------------------------------
    # View 1: Browse Fleet (Guest, Customer, Admin)
    # ---------------------------------------------------------
    def show_browse_view(self):
        self.clear_main_container()
        self.update_sidebar_state()

        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(
            header_frame,
            text="Explore Available Vehicles",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(side="left")

        # Filters
        filter_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 15))

        self.type_filter = ctk.CTkSegmentedButton(
            filter_frame,
            values=["All", "Cars Only", "Bikes Only"],
            command=self.on_filter_changed
        )
        self.type_filter.set("All")
        self.type_filter.pack(side="left", padx=(0, 15))

        self.avail_checkbox = ctk.CTkCheckBox(
            filter_frame,
            text="Available Only",
            command=self.on_filter_changed
        )
        self.avail_checkbox.pack(side="left", padx=10)

        # Vehicle List (Scrollable)
        self.vehicle_scroll = ctk.CTkScrollableFrame(self.main_container, corner_radius=10)
        self.vehicle_scroll.pack(fill="both", expand=True)

        self.render_vehicle_cards()

    def on_filter_changed(self, *args):
        self.render_vehicle_cards()

    def render_vehicle_cards(self):
        for widget in self.vehicle_scroll.winfo_children():
            widget.destroy()

        vtype = self.type_filter.get()
        avail_only = self.avail_checkbox.get()

        matching = []
        for v in self.store.vehicles:
            if vtype == "Cars Only" and v.type != "Car":
                continue
            if vtype == "Bikes Only" and v.type != "Bike":
                continue
            if avail_only and not v.available:
                continue
            matching.append(v)

        if not matching:
            no_card = ctk.CTkFrame(self.vehicle_scroll, corner_radius=10)
            no_card.pack(fill="x", pady=20, padx=10)
            lbl = ctk.CTkLabel(no_card, text="No vehicles match your filter criteria.", font=ctk.CTkFont(size=15))
            lbl.pack(pady=30)
            return

        for v in matching:
            card = ctk.CTkFrame(self.vehicle_scroll, corner_radius=12)
            card.pack(fill="x", pady=8, padx=5)

            # Left side: icon & details
            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=20, pady=15)

            # Title row
            title_row = ctk.CTkFrame(left, fg_color="transparent")
            title_row.pack(fill="x", anchor="w")

            type_icon = "🚗" if v.type == "Car" else "🏍️"
            model_lbl = ctk.CTkLabel(
                title_row,
                text=f"{type_icon}  {v.model}",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            model_lbl.pack(side="left")

            id_badge = ctk.CTkLabel(
                title_row,
                text=f"  {v.id}  ",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=("gray75", "gray30"),
                corner_radius=6
            )
            id_badge.pack(side="left", padx=12)

            # Specs row
            specs_text = ""
            if v.type == "Car":
                trans = "Automatic" if v.spec2 else "Manual"
                specs_text = f"• {v.spec1} Seats   • {trans} Transmission   • Type: Car"
            else:
                helmet = "Helmet included" if v.spec2 else "Helmet not included"
                specs_text = f"• {v.spec1} cc Engine   • {helmet}   • Type: Bike"

            specs_lbl = ctk.CTkLabel(
                left,
                text=specs_text,
                font=ctk.CTkFont(size=13),
                text_color="gray"
            )
            specs_lbl.pack(anchor="w", pady=(5, 0))

            # Right side: Price, status, and action button
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=20, pady=15)

            price_lbl = ctk.CTkLabel(
                right,
                text=f"Rs. {v.price:.2f} / day",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=("royalblue", "deepskyblue")
            )
            price_lbl.pack(anchor="e", pady=(0, 4))

            # Status pill
            if v.available:
                status_pill = ctk.CTkLabel(
                    right,
                    text="  ● Available  ",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="white",
                    fg_color="#107c41",
                    corner_radius=10
                )
                status_pill.pack(anchor="e", pady=(0, 10))

                # Button action
                if isinstance(self.current_user, Customer):
                    rent_btn = ctk.CTkButton(
                        right,
                        text="Rent Vehicle",
                        height=32,
                        fg_color="#107c41",
                        hover_color="#0e6837",
                        command=lambda veh=v: self.open_rent_dialog(veh)
                    )
                    rent_btn.pack(anchor="e")
                elif self.current_user == "ADMIN":
                    admin_tag = ctk.CTkLabel(right, text="Admin View", font=ctk.CTkFont(size=11), text_color="gray")
                    admin_tag.pack(anchor="e")
                else:
                    login_to_rent_btn = ctk.CTkButton(
                        right,
                        text="Log In to Rent",
                        height=32,
                        fg_color=("gray60", "gray40"),
                        command=self.show_auth_view
                    )
                    login_to_rent_btn.pack(anchor="e")
            else:
                status_pill = ctk.CTkLabel(
                    right,
                    text="  ● Currently Rented  ",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="white",
                    fg_color="#a80000",
                    corner_radius=10
                )
                status_pill.pack(anchor="e", pady=(0, 6))

    # ---------------------------------------------------------
    # Dialog: Rent Vehicle with Live Calculations
    # ---------------------------------------------------------
    def open_rent_dialog(self, vehicle):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Rent {vehicle.model} ({vehicle.id})")
        dialog.geometry("480x520")
        dialog.resizable(False, False)
        dialog.grab_set()

        # Dialog Header
        title = ctk.CTkLabel(
            dialog,
            text=f"Confirm Rental: {vehicle.model}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(25, 5))

        # Vehicle Specs Card
        card = ctk.CTkFrame(dialog, corner_radius=10)
        card.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(card, text=f"Vehicle ID: {vehicle.id}   |   Type: {vehicle.type}", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(12, 2))
        ctk.CTkLabel(card, text=f"Daily Rate: Rs. {vehicle.price:.2f} per day", text_color=("royalblue", "deepskyblue"), font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(0, 12))

        # Days Selection
        select_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        select_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(select_frame, text="Rental Duration (Days):", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        days_val_label = ctk.CTkLabel(select_frame, text="3 Days", font=ctk.CTkFont(size=16, weight="bold"))
        days_val_label.pack(anchor="w", pady=(4, 0))

        days_slider = ctk.CTkSlider(
            select_frame,
            from_=1,
            to=30,
            number_of_steps=29
        )
        days_slider.set(3)
        days_slider.pack(fill="x", pady=(5, 10))

        # Total Calculation Box
        calc_box = ctk.CTkFrame(dialog, fg_color=("gray85", "gray20"), corner_radius=10)
        calc_box.pack(fill="x", padx=30, pady=10)

        calc_row = ctk.CTkFrame(calc_box, fg_color="transparent")
        calc_row.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(calc_row, text="Total Estimated Charge:", font=ctk.CTkFont(size=14)).pack(side="left")
        total_label = ctk.CTkLabel(
            calc_row,
            text=f"Rs. {vehicle.price * 3:.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#107c41"
        )
        total_label.pack(side="right")

        def update_calc(val):
            days = int(round(val))
            days_val_label.configure(text=f"{days} Day{'s' if days > 1 else ''}")
            total = vehicle.price * days
            total_label.configure(text=f"Rs. {total:.2f}")

        days_slider.configure(command=update_calc)

        # Confirm Button
        def confirm_rental():
            days = int(round(days_slider.get()))
            total = vehicle.price * days
            today_str = datetime.date.today().isoformat()
            rental_id = self.store.next_rental_id()

            new_rental = Rental(
                rental_id,
                self.current_user.username,
                vehicle.id,
                vehicle.type,
                vehicle.model,
                days,
                vehicle.price,
                total,
                today_str,
                "",
                "ACTIVE"
            )
            self.store.rentals.append(new_rental)
            vehicle.available = False
            self.store.save_all()

            dialog.destroy()
            self.render_vehicle_cards()
            self.show_bill_modal(new_rental, self.current_user)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=20)

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            fg_color=("gray60", "gray40"),
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        confirm_btn = ctk.CTkButton(
            btn_row,
            text="Confirm & Rent",
            fg_color="#107c41",
            hover_color="#0e6837",
            command=confirm_rental
        )
        confirm_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))

    # ---------------------------------------------------------
    # Digital Bill / Receipt Modal
    # ---------------------------------------------------------
    def show_bill_modal(self, rental, customer):
        bill = ctk.CTkToplevel(self)
        bill.title("Rental Confirmation Receipt")
        bill.geometry("450x520")
        bill.resizable(False, False)
        bill.grab_set()

        ctk.CTkLabel(bill, text="🎉 Rental Confirmed!", font=ctk.CTkFont(size=22, weight="bold"), text_color="#107c41").pack(pady=(25, 4))
        ctk.CTkLabel(bill, text="Your vehicle is booked and ready.", font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(0, 15))

        receipt_frame = ctk.CTkFrame(bill, corner_radius=12)
        receipt_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        fields = [
            ("Rental ID", rental.rental_id),
            ("Customer Name", customer.name),
            ("Vehicle ID", rental.vehicle_id),
            ("Vehicle Model", rental.vehicle_model),
            ("Vehicle Type", rental.vehicle_type),
            ("Duration", f"{rental.days} days"),
            ("Daily Rate", f"Rs. {rental.price_per_day:.2f}"),
            ("Rent Date", rental.rent_date),
            ("Status", rental.status)
        ]

        for label, val in fields:
            row = ctk.CTkFrame(receipt_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=13)).pack(side="right")

        # Divider
        div = ctk.CTkFrame(receipt_frame, height=2, fg_color=("gray75", "gray30"))
        div.pack(fill="x", padx=15, pady=10)

        # Total
        tot_row = ctk.CTkFrame(receipt_frame, fg_color="transparent")
        tot_row.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(tot_row, text="Total Charge Paid", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        ctk.CTkLabel(tot_row, text=f"Rs. {rental.total_charge:.2f}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#107c41").pack(side="right")

        close_btn = ctk.CTkButton(bill, text="Close Receipt", command=bill.destroy)
        close_btn.pack(fill="x", padx=25, pady=(0, 20))

    # ---------------------------------------------------------
    # View 2: Customer My Rentals
    # ---------------------------------------------------------
    def show_my_rentals_view(self):
        self.clear_main_container()

        title = ctk.CTkLabel(
            self.main_container,
            text=f"My Rentals — {self.current_user.name}",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))

        my_rentals = [r for r in self.store.rentals if r.username == self.current_user.username]
        active_rentals = [r for r in my_rentals if r.is_active()]

        # Metrics bar
        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        for heading, count in [("Total Rentals", len(my_rentals)), ("Active Rentals", len(active_rentals)), ("Total Spent", f"Rs. {sum(r.total_charge for r in my_rentals):.2f}")]:
            box = ctk.CTkFrame(stats_frame, corner_radius=10)
            box.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(box, text=heading, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(12, 2))
            ctk.CTkLabel(box, text=str(count), font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 12))

        # Rentals List
        scroll = ctk.CTkScrollableFrame(self.main_container, corner_radius=10)
        scroll.pack(fill="both", expand=True)

        if not my_rentals:
            no_card = ctk.CTkFrame(scroll, corner_radius=10)
            no_card.pack(fill="x", pady=20, padx=10)
            lbl = ctk.CTkLabel(no_card, text="You have no rental history yet.", font=ctk.CTkFont(size=15))
            lbl.pack(pady=30)
            return

        for r in reversed(my_rentals):
            card = ctk.CTkFrame(scroll, corner_radius=10)
            card.pack(fill="x", pady=6, padx=5)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=20, pady=15)

            ctk.CTkLabel(left, text=f"{r.rental_id}  •  {r.vehicle_model} ({r.vehicle_id})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
            info = f"Days: {r.days}  |  Daily Rate: Rs. {r.price_per_day:.2f}  |  Rented on: {r.rent_date}"
            if r.return_date:
                info += f"  |  Returned on: {r.return_date}"
            ctk.CTkLabel(left, text=info, font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(3, 0))

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=20, pady=15)

            ctk.CTkLabel(right, text=f"Rs. {r.total_charge:.2f}", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="e")

            if r.is_active():
                ret_btn = ctk.CTkButton(
                    right,
                    text="Return Vehicle",
                    height=28,
                    fg_color="coral3",
                    hover_color="coral4",
                    command=lambda rent_obj=r: self.handle_return_vehicle(rent_obj)
                )
                ret_btn.pack(anchor="e", pady=(6, 0))
            else:
                ret_badge = ctk.CTkLabel(
                    right,
                    text="  RETURNED  ",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color=("gray70", "gray35"),
                    corner_radius=6
                )
                ret_badge.pack(anchor="e", pady=(6, 0))

    def handle_return_vehicle(self, rental):
        if not messagebox.askyesno("Confirm Return", f"Are you sure you want to return {rental.vehicle_model} ({rental.vehicle_id})?"):
            return

        today_str = datetime.date.today().isoformat()
        rental.mark_returned(today_str)
        veh = self.store.find_vehicle(rental.vehicle_id)
        if veh:
            veh.available = True
        self.store.save_all()

        messagebox.showinfo("Vehicle Returned", f"Vehicle {rental.vehicle_model} returned successfully.\nFinal charge: Rs. {rental.total_charge:.2f}")
        self.show_my_rentals_view()

    # ---------------------------------------------------------
    # View 3: Customer Profile
    # ---------------------------------------------------------
    def show_profile_view(self):
        self.clear_main_container()

        title = ctk.CTkLabel(self.main_container, text="My Profile", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(self.main_container, corner_radius=12)
        card.pack(fill="x", padx=10, pady=10)

        details = [
            ("Full Name", self.current_user.name),
            ("Username", self.current_user.username),
            ("Phone Number", self.current_user.phone),
            ("Email Address", self.current_user.email)
        ]

        for lbl, val in details:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=12)
            ctk.CTkLabel(row, text=lbl, font=ctk.CTkFont(size=14, weight="bold"), width=140, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=ctk.CTkFont(size=14)).pack(side="left")

    # ---------------------------------------------------------
    # View 4: Admin Fleet Management (Add, Edit, Remove)
    # ---------------------------------------------------------
    def show_admin_vehicles_view(self):
        self.clear_main_container()

        header = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(header, text="Fleet Management", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(side="left")

        add_btn = ctk.CTkButton(
            header,
            text="+ Add New Vehicle",
            fg_color="#107c41",
            hover_color="#0e6837",
            command=self.open_add_vehicle_dialog
        )
        add_btn.pack(side="right")

        scroll = ctk.CTkScrollableFrame(self.main_container, corner_radius=10)
        scroll.pack(fill="both", expand=True)

        for v in self.store.vehicles:
            card = ctk.CTkFrame(scroll, corner_radius=10)
            card.pack(fill="x", pady=6, padx=5)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=20, pady=12)

            t_icon = "🚗" if v.type == "Car" else "🏍️"
            ctk.CTkLabel(left, text=f"{t_icon}  {v.model}  ({v.id})", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")

            spec_desc = f"Seats: {v.spec1}, {'Automatic' if v.spec2 else 'Manual'}" if v.type == "Car" else f"{v.spec1}cc, {'Helmet' if v.spec2 else 'No Helmet'}"
            status_desc = "Available" if v.available else "Rented"
            ctk.CTkLabel(left, text=f"Type: {v.type}  |  Price: Rs. {v.price:.2f}/day  |  {spec_desc}  |  Status: {status_desc}", font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(2, 0))

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=20, pady=12)

            del_btn = ctk.CTkButton(
                right,
                text="Remove",
                width=80,
                height=30,
                fg_color="crimson",
                hover_color="darkred",
                command=lambda veh=v: self.handle_remove_vehicle(veh)
            )
            del_btn.pack(side="right", padx=(8, 0))

            edit_btn = ctk.CTkButton(
                right,
                text="Edit",
                width=80,
                height=30,
                command=lambda veh=v: self.open_edit_vehicle_dialog(veh)
            )
            edit_btn.pack(side="right")

    def handle_remove_vehicle(self, vehicle):
        if not vehicle.available:
            messagebox.showerror("Error", "A rented vehicle cannot be removed until it is returned.")
            return

        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove {vehicle.model} ({vehicle.id})?"):
            self.store.vehicles = [v for v in self.store.vehicles if v.id != vehicle.id]
            self.store.save_all()
            messagebox.showinfo("Success", "Vehicle removed successfully.")
            self.show_admin_vehicles_view()

    def open_add_vehicle_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Vehicle")
        dialog.geometry("450x540")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Add New Vehicle", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 15))

        f = ctk.CTkFrame(dialog, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=35)

        ctk.CTkLabel(f, text="Vehicle ID (e.g. C103, B103):").pack(anchor="w")
        id_entry = ctk.CTkEntry(f)
        id_entry.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(f, text="Vehicle Type:").pack(anchor="w")
        type_menu = ctk.CTkSegmentedButton(f, values=["Car", "Bike"])
        type_menu.set("Car")
        type_menu.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(f, text="Model Name:").pack(anchor="w")
        model_entry = ctk.CTkEntry(f)
        model_entry.pack(fill="x", pady=(2, 10))

        ctk.CTkLabel(f, text="Daily Rate (Rs.):").pack(anchor="w")
        price_entry = ctk.CTkEntry(f)
        price_entry.pack(fill="x", pady=(2, 10))

        # Dynamic specs
        spec1_lbl = ctk.CTkLabel(f, text="Number of Seats (1-12):")
        spec1_lbl.pack(anchor="w")
        spec1_entry = ctk.CTkEntry(f)
        spec1_entry.pack(fill="x", pady=(2, 10))
        spec1_entry.insert(0, "5")

        spec2_var = tk.BooleanVar(value=True)
        spec2_switch = ctk.CTkSwitch(f, text="Automatic Transmission", variable=spec2_var)
        spec2_switch.pack(anchor="w", pady=(2, 15))

        def on_type_toggle(val):
            if val == "Car":
                spec1_lbl.configure(text="Number of Seats (1-12):")
                spec1_entry.delete(0, tk.END)
                spec1_entry.insert(0, "5")
                spec2_switch.configure(text="Automatic Transmission")
            else:
                spec1_lbl.configure(text="Engine Capacity in CC (50-3000):")
                spec1_entry.delete(0, tk.END)
                spec1_entry.insert(0, "150")
                spec2_switch.configure(text="Helmet Included")

        type_menu.configure(command=on_type_toggle)

        def save_vehicle():
            vid = id_entry.get().strip()
            vtype = type_menu.get()
            model = model_entry.get().strip()
            price_str = price_entry.get().strip()
            spec1_str = spec1_entry.get().strip()

            if not vid or not model or not price_str or not spec1_str:
                messagebox.showerror("Validation Error", "All fields are required.")
                return
            if "|" in vid or "|" in model:
                messagebox.showerror("Validation Error", "Character '|' is not allowed.")
                return
            if self.store.find_vehicle(vid):
                messagebox.showerror("Validation Error", f"Vehicle ID '{vid}' already exists.")
                return

            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Daily rate must be a positive number.")
                return

            try:
                spec1 = int(spec1_str)
                if spec1 <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Specification value must be a positive whole number.")
                return

            new_v = Vehicle(vtype, vid, model, price, spec1, spec2_var.get(), True)
            self.store.vehicles.append(new_v)
            self.store.save_all()

            messagebox.showinfo("Success", f"{vtype} {model} added successfully.")
            dialog.destroy()
            self.show_admin_vehicles_view()

        save_btn = ctk.CTkButton(f, text="Add Vehicle", fg_color="#107c41", hover_color="#0e6837", command=save_vehicle)
        save_btn.pack(fill="x", pady=10)

    def open_edit_vehicle_dialog(self, vehicle):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit {vehicle.model} ({vehicle.id})")
        dialog.geometry("450x480")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=f"Edit Vehicle: {vehicle.id}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 15))

        f = ctk.CTkFrame(dialog, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=35)

        ctk.CTkLabel(f, text="Model Name:").pack(anchor="w")
        model_entry = ctk.CTkEntry(f)
        model_entry.pack(fill="x", pady=(2, 10))
        model_entry.insert(0, vehicle.model)

        ctk.CTkLabel(f, text="Daily Rate (Rs.):").pack(anchor="w")
        price_entry = ctk.CTkEntry(f)
        price_entry.pack(fill="x", pady=(2, 10))
        price_entry.insert(0, f"{vehicle.price:.2f}")

        spec1_title = "Number of Seats:" if vehicle.type == "Car" else "Engine Capacity (CC):"
        ctk.CTkLabel(f, text=spec1_title).pack(anchor="w")
        spec1_entry = ctk.CTkEntry(f)
        spec1_entry.pack(fill="x", pady=(2, 10))
        spec1_entry.insert(0, str(vehicle.spec1))

        spec2_title = "Automatic Transmission" if vehicle.type == "Car" else "Helmet Included"
        spec2_var = tk.BooleanVar(value=vehicle.spec2)
        spec2_switch = ctk.CTkSwitch(f, text=spec2_title, variable=spec2_var)
        spec2_switch.pack(anchor="w", pady=(2, 15))

        def save_edit():
            model = model_entry.get().strip()
            price_str = price_entry.get().strip()
            spec1_str = spec1_entry.get().strip()

            if not model or not price_str or not spec1_str:
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                price = float(price_str)
                spec1 = int(spec1_str)
                if price <= 0 or spec1 <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values entered.")
                return

            vehicle.model = model
            vehicle.price = price
            vehicle.spec1 = spec1
            vehicle.spec2 = spec2_var.get()
            self.store.save_all()

            messagebox.showinfo("Success", "Vehicle updated successfully.")
            dialog.destroy()
            self.show_admin_vehicles_view()

        save_btn = ctk.CTkButton(f, text="Save Changes", command=save_edit)
        save_btn.pack(fill="x", pady=10)

    # ---------------------------------------------------------
    # View 5: Admin All Rentals
    # ---------------------------------------------------------
    def show_admin_rentals_view(self):
        self.clear_main_container()

        title = ctk.CTkLabel(self.main_container, text="All System Rentals", font=ctk.CTkFont(size=26, weight="bold"))
        title.pack(anchor="w", pady=(0, 15))

        # Metrics bar
        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))

        active_cnt = sum(1 for r in self.store.rentals if r.is_active())
        tot_rev = sum(r.total_charge for r in self.store.rentals)

        for heading, val in [("Total Contracts", len(self.store.rentals)), ("Active Rentals", active_cnt), ("Total System Revenue", f"Rs. {tot_rev:.2f}")]:
            box = ctk.CTkFrame(stats_frame, corner_radius=10)
            box.pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(box, text=heading, font=ctk.CTkFont(size=12), text_color="gray").pack(pady=(10, 2))
            ctk.CTkLabel(box, text=str(val), font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(self.main_container, corner_radius=10)
        scroll.pack(fill="both", expand=True)

        if not self.store.rentals:
            no_card = ctk.CTkFrame(scroll, corner_radius=10)
            no_card.pack(fill="x", pady=20, padx=10)
            lbl = ctk.CTkLabel(no_card, text="No rental records found in the system.", font=ctk.CTkFont(size=15))
            lbl.pack(pady=30)
            return

        for r in reversed(self.store.rentals):
            card = ctk.CTkFrame(scroll, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=15, pady=10)

            ctk.CTkLabel(left, text=f"{r.rental_id}  |  Customer: @{r.username}  |  Vehicle: {r.vehicle_id} ({r.vehicle_model})", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            desc = f"Rent Date: {r.rent_date}  |  Duration: {r.days} days  |  Total: Rs. {r.total_charge:.2f}"
            if r.return_date:
                desc += f"  |  Returned: {r.return_date}"
            ctk.CTkLabel(left, text=desc, font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", pady=(2, 0))

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=15, pady=10)

            status_color = "#107c41" if r.is_active() else ("gray70", "gray40")
            pill = ctk.CTkLabel(
                right,
                text=f"  {r.status}  ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=status_color,
                corner_radius=6
            )
            pill.pack()

    # ---------------------------------------------------------
    # View 6: Authentication (Customer Login / Register & Admin)
    # ---------------------------------------------------------
    def show_auth_view(self):
        self.clear_main_container()

        tabview = ctk.CTkTabview(self.main_container, width=500)
        tabview.pack(pady=20)

        # Tab 1: Customer Login
        tab_cust_login = tabview.add("Customer Login")
        # Tab 2: Customer Registration
        tab_cust_reg = tabview.add("Customer Register")
        # Tab 3: Admin Login
        tab_admin = tabview.add("Admin Login")

        # --- Customer Login Setup ---
        ctk.CTkLabel(tab_cust_login, text="Welcome Back!", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 15))
        ctk.CTkLabel(tab_cust_login, text="Username:").pack(anchor="w", padx=40)
        login_user = ctk.CTkEntry(tab_cust_login, width=320)
        login_user.pack(pady=(2, 12))

        ctk.CTkLabel(tab_cust_login, text="Password:").pack(anchor="w", padx=40)
        login_pass = ctk.CTkEntry(tab_cust_login, width=320, show="•")
        login_pass.pack(pady=(2, 20))

        def do_customer_login():
            u = login_user.get().strip()
            p = login_pass.get().strip()
            cust = self.store.find_customer(u)
            if not cust or not cust.verify_password(p):
                messagebox.showerror("Login Failed", "Incorrect username or password.")
                return
            self.current_user = cust
            self.update_sidebar_state()
            self.show_browse_view()
            messagebox.showinfo("Welcome", f"Logged in successfully! Welcome, {cust.name}!")

        login_btn = ctk.CTkButton(tab_cust_login, text="Sign In", width=320, command=do_customer_login)
        login_btn.pack(pady=10)

        # --- Customer Registration Setup ---
        ctk.CTkLabel(tab_cust_reg, text="Create a Customer Account", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 10))

        ctk.CTkLabel(tab_cust_reg, text="Choose Username:").pack(anchor="w", padx=40)
        reg_user = ctk.CTkEntry(tab_cust_reg, width=320)
        reg_user.pack(pady=(2, 8))

        ctk.CTkLabel(tab_cust_reg, text="Choose Password (min 4 chars):").pack(anchor="w", padx=40)
        reg_pass = ctk.CTkEntry(tab_cust_reg, width=320, show="•")
        reg_pass.pack(pady=(2, 8))

        ctk.CTkLabel(tab_cust_reg, text="Full Name:").pack(anchor="w", padx=40)
        reg_name = ctk.CTkEntry(tab_cust_reg, width=320)
        reg_name.pack(pady=(2, 8))

        ctk.CTkLabel(tab_cust_reg, text="Phone Number:").pack(anchor="w", padx=40)
        reg_phone = ctk.CTkEntry(tab_cust_reg, width=320)
        reg_phone.pack(pady=(2, 8))

        ctk.CTkLabel(tab_cust_reg, text="Email Address:").pack(anchor="w", padx=40)
        reg_email = ctk.CTkEntry(tab_cust_reg, width=320)
        reg_email.pack(pady=(2, 15))

        def do_customer_reg():
            u = reg_user.get().strip()
            p = reg_pass.get().strip()
            n = reg_name.get().strip()
            ph = reg_phone.get().strip()
            em = reg_email.get().strip()

            if not u or not p or not n or not ph or not em:
                messagebox.showerror("Error", "All fields are required.")
                return
            if len(p) < 4:
                messagebox.showerror("Error", "Password must contain at least 4 characters.")
                return
            if any("|" in x for x in (u, p, n, ph, em)):
                messagebox.showerror("Error", "Character '|' is not allowed in input.")
                return
            if self.store.find_customer(u) or u.lower() == "admin":
                messagebox.showerror("Error", "That username is already registered.")
                return

            new_cust = Customer(u, p, n, ph, em)
            self.store.customers.append(new_cust)
            self.store.save_all()

            messagebox.showinfo("Registration Successful", "Account created successfully! You can now log in.")
            tabview.set("Customer Login")
            login_user.delete(0, tk.END)
            login_user.insert(0, u)
            login_pass.delete(0, tk.END)

        reg_btn = ctk.CTkButton(tab_cust_reg, text="Create Account", fg_color="#107c41", hover_color="#0e6837", width=320, command=do_customer_reg)
        reg_btn.pack(pady=10)

        # --- Admin Login Setup ---
        ctk.CTkLabel(tab_admin, text="Administrator Portal", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25, 15))

        ctk.CTkLabel(tab_admin, text="Admin Username:").pack(anchor="w", padx=40)
        admin_user = ctk.CTkEntry(tab_admin, width=320)
        admin_user.insert(0, "admin")
        admin_user.pack(pady=(2, 12))

        ctk.CTkLabel(tab_admin, text="Admin Password:").pack(anchor="w", padx=40)
        admin_pass = ctk.CTkEntry(tab_admin, width=320, show="•")
        admin_pass.pack(pady=(2, 20))

        def do_admin_login():
            u = admin_user.get().strip()
            p = admin_pass.get().strip()
            if u != self.admin_creds[0] or p != self.admin_creds[1]:
                messagebox.showerror("Access Denied", "Incorrect admin login details.")
                return
            self.current_user = "ADMIN"
            self.update_sidebar_state()
            self.show_admin_vehicles_view()
            messagebox.showinfo("Admin Authenticated", "Admin mode unlocked. Welcome!")

        admin_login_btn = ctk.CTkButton(tab_admin, text="Log In as Admin", fg_color="darkred", hover_color="#700000", width=320, command=do_admin_login)
        admin_login_btn.pack(pady=10)


if __name__ == "__main__":
    app = RideEaseGUI()
    app.mainloop()

