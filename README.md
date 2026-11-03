# 🚗 RideEase — Vehicle Rental Management System

[![C++17](https://img.shields.io/badge/C%2B%2B-17-00599C?logo=c%2B%2B)](https://en.cppreference.com/w/cpp/17)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/Desktop%20GUI-CustomTkinter-2D8CFF)](https://github.com/TomSchimansky/CustomTkinter)
[![Web](https://img.shields.io/badge/Web%20Dashboard-TailwindCSS-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**RideEase** is a full-featured, object-oriented Vehicle Rental Management System engineered in **modern C++17** with companion **Native Desktop (CustomTkinter)** and **Web Browser (Tailwind CSS)** graphical user interfaces. It demonstrates practical Object-Oriented Programming (OOP) paradigms through a complete customer and admin rental workflow, automatic bill calculation, real-time fleet reconciliation, and persistent file storage.

---

## 🌟 System Highlights

- **Triple-Interface Architecture**: Use the menu-driven C++ terminal console, the native macOS/cross-platform desktop GUI, or the zero-dependency browser web dashboard.
- **Unified Data Synchronization**: All three interfaces share the exact same persistent text database in `data/`. Actions taken in one interface reflect immediately across all others.
- **Complete OOP Hierarchy**: Base `Vehicle` abstraction inherited by specialized `Car` and `Bike` classes utilizing runtime polymorphism.
- **Self-Healing Fleet State**: Automatic startup reconciliation prevents inconsistent inventory states by verifying active rentals against vehicle availability flags.
- **Built-in Billing Engine**: Generates real-time rental estimates, itemized invoices, and rental history tracking.
- **Role-Based Workflows**: Dedicated customer booking and admin fleet management portals with validation safeguards.

---

## 🏗️ Project Architecture & File Structure

```text
rideease/
├── include/                 # C++ Header declarations
│   ├── Vehicle.h            # Abstract base class
│   ├── Car.h                # Derived Car class (seats, transmission)
│   ├── Bike.h               # Derived Bike class (engine CC, helmet)
│   ├── Customer.h           # Customer account encapsulation
│   ├── Rental.h             # Rental contract & transaction model
│   ├── Admin.h              # Admin authentication model
│   ├── DataStore.h          # File persistence & reconciliation layer
│   └── RideEaseApp.h        # Interactive CLI controller
├── src/                     # C++ Implementations
│   ├── Vehicle.cpp
│   ├── Car.cpp
│   ├── Bike.cpp
│   ├── Customer.cpp
│   ├── Rental.cpp
│   ├── Admin.cpp
│   ├── DataStore.cpp
│   ├── RideEaseApp.cpp
│   └── main.cpp             # Application entry point
├── data/                    # Persistent pipe-separated text storage
│   ├── vehicles.txt         # Fleet inventory records
│   ├── customers.txt        # Customer credentials and profile data
│   └── rentals.txt          # Active and historical rental contracts
├── gui.py                   # Modern Native Desktop GUI (CustomTkinter)
├── web_gui.py               # Responsive Web Dashboard (Python HTTP Server)
├── run_gui.sh               # One-click launcher script
├── Makefile                 # Automated build system (C++17)
└── README.md                # System documentation & Viva guide
```

---

## 🚀 Quick Start Guide

### 1. Terminal Console (C++17)

Compile using the provided `Makefile`:

```bash
make clean && make
./rideease
```

Or compile directly with `g++` / `clang++`:

```bash
g++ -std=c++17 -Wall -Wextra -pedantic -Iinclude src/*.cpp -o rideease
./rideease
```

### 2. Native Desktop GUI (CustomTkinter)

Launch the modern desktop application with dark/light mode, visual vehicle cards, and duration sliders:

```bash
./run_gui.sh
# or
make gui
# or
python3 gui.py
```

### 3. Web Browser Dashboard

Launch the local web server (requires only standard Python 3, zero pip packages):

```bash
./run_gui.sh --web
# or
make web
# or
python3 web_gui.py 8080
```
Then visit **`http://localhost:8080`** in your browser.

---

## 🔑 Default Credentials

- **Admin Username**: `admin`
- **Admin Password**: `admin123`
- **Customer Registration**: New customers can be registered instantly from any interface (username, password >= 4 chars, full name, phone number, email).

---

## 💾 Persistence & Data Format

The system uses human-readable, pipe-delimited (`|`) text files for seamless persistence and data recovery:

### `data/vehicles.txt`
```text
Type|ID|Model|PricePerDay|Spec1|Spec2|IsAvailable
Car|C101|Maruti Swift|1800.00|5|0|1
Car|C102|Hyundai i20|2200.00|5|1|1
Bike|B101|Honda Activa 6G|700.00|110|1|1
Bike|B102|Royal Enfield Classic 350|1200.00|350|0|1
```
*For Cars: `Spec1` = Seats, `Spec2` = Automatic (1/0). For Bikes: `Spec1` = Engine CC, `Spec2` = Helmet Included (1/0).*

### `data/customers.txt`
```text
Username|Password|FullName|PhoneNumber|Email
riya|ride123|Riya Sharma|9876543210|riya@example.com
```

### `data/rentals.txt`
```text
RentalID|Username|VehicleID|Type|Model|Days|PricePerDay|TotalCharge|RentDate|ReturnDate|Status
RENT-001|riya|B101|Bike|Honda Activa 6G|3|700.00|2100.00|2026-10-30|2026-10-30|RETURNED
RENT-002|riya|C101|Car|Maruti Swift|2|1800.00|3600.00|2026-10-30||ACTIVE
```

> [!NOTE]
> **Availability Reconciliation**: At startup, `DataStore::reconcileAvailability()` scans active records in `rentals.txt`. Any vehicle with an active rental is automatically marked as unavailable, protecting the database against inconsistent states even if the process was terminated unexpectedly.

---

## 🎓 Object-Oriented Programming (OOP) Concepts for Viva

| OOP Concept | Implementation in RideEase |
| :--- | :--- |
| **Classes & Objects** | Real-world entities are modeled as classes (`Vehicle`, `Car`, `Bike`, `Customer`, `Rental`, `Admin`, `DataStore`, `RideEaseApp`) and instantiated at runtime. |
| **Encapsulation** | State attributes (`pricePerDay_`, `available_`, `password_`) are private. Access and state mutations occur strictly through controlled public methods (`verifyPassword()`, `markReturned()`). |
| **Inheritance** | `Car` and `Bike` inherit common rental attributes and behaviors publicly from base class `Vehicle`. |
| **Abstraction** | `Vehicle` defines pure virtual functions (`getType()`, `calculateCharge()`, `displayDetails()`, `serialize()`), enforcing an interface contract without exposing internal details. |
| **Runtime Polymorphism** | Vehicles are held via base class smart pointers (`std::shared_ptr<Vehicle>`). Calling `vehicle->displayDetails()` or `vehicle->calculateCharge(days)` dynamically executes the derived class implementation. |
| **Virtual Destructors** | `virtual ~Vehicle() = default;` guarantees safe resource destruction when deleting derived objects through base pointers. |
| **Exception & Stream Safety** | Safe stream parsers, input validation checks, and graceful EOF handling prevent hanging or infinite loops on input termination. |

---

## 🛡️ Business Rules & Safeguards

1. **Unique Vehicle Identifiers**: Duplicate vehicle IDs are rejected during fleet registration.
2. **Availability Enforcement**: Already rented vehicles cannot be rented again until returned.
3. **Admin Deletion Guard**: An admin cannot delete a vehicle from the fleet while it is currently on an active rental.
4. **Owner-Specific Returns**: Returns are accepted only for active rentals belonging to the authenticated customer.
5. **Input Sanitization**: Disallows the delimiter `|` in user input fields to prevent record corruption.
6. **Password Validation**: Requires a minimum of 4 characters for customer passwords.

---

## 📋 Step-by-Step Demo Walkthrough

When presenting or demoing the project, follow this recommended sequence:

1. **Launch the Interface**:
   - Run `./rideease` for terminal CLI or `./run_gui.sh` for the desktop window.
2. **Customer Registration & Login**:
   - Register a new customer (`demo_user`, password `pass123`, full name `Alex Morgan`).
   - Log in with the newly created account.
3. **Browse & Rent a Vehicle**:
   - View available vehicles (observe specs: transmission for cars, engine cc/helmet for bikes).
   - Select a vehicle (e.g., `C102` Hyundai i20), specify rental days (e.g., `3` days).
   - Confirm rental and inspect the generated **Itemized Rental Bill** (`RENT-001`).
4. **Verify Availability Update**:
   - View the fleet list again; notice `C102` status changed to **Rented**.
   - Attempt to rent `C102` again; observe that the system prevents double-booking.
5. **Return the Vehicle**:
   - Go to "Return a vehicle" or "My Rentals".
   - Return `RENT-001`; observe the final charge receipt and status updated to **RETURNED**.
   - Notice the vehicle is now automatically restored to **Available**.
6. **Admin Panel Fleet Management**:
   - Log in as admin (`admin` / `admin123`).
   - Add a new vehicle (Car or Bike).
   - Attempt to delete a rented vehicle vs available vehicle to demonstrate integrity constraints.
   - View all system-wide rental transactions and revenue.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
