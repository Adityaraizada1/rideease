#include "RideEaseApp.h"

#include "Bike.h"
#include "Car.h"

#include <algorithm>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>

namespace {

struct EndOfInputException : public std::exception {
    const char* what() const noexcept override { return "End of input stream reached."; }
};

std::string readLine(const std::string& prompt) {
    std::string value;
    std::cout << prompt;
    if (!std::getline(std::cin, value)) {
        if (std::cin.eof()) {
            throw EndOfInputException();
        }
    }
    if (!value.empty() && value.back() == '\r') {
        value.pop_back();
    }
    return value;
}

std::string readNonEmpty(const std::string& prompt) {
    while (true) {
        const std::string value = readLine(prompt);
        if (value.empty()) {
            std::cout << "Input cannot be empty. Please try again.\n";
        } else if (value.find('|') != std::string::npos) {
            std::cout << "The character '|' is not allowed. Please try again.\n";
        } else {
            return value;
        }
    }
}

int readInt(const std::string& prompt, int minimum, int maximum) {
    while (true) {
        const std::string value = readLine(prompt);
        try {
            size_t position = 0;
            const int result = std::stoi(value, &position);
            if (position == value.size() && result >= minimum && result <= maximum) return result;
        } catch (const std::exception&) {
        }
        std::cout << "Please enter a whole number from " << minimum << " to " << maximum << ".\n";
    }
}

double readPrice(const std::string& prompt) {
    while (true) {
        const std::string value = readLine(prompt);
        try {
            size_t position = 0;
            const double result = std::stod(value, &position);
            if (position == value.size() && result > 0.0 && result <= 1000000.0) return result;
        } catch (const std::exception&) {
        }
        std::cout << "Please enter a positive price.\n";
    }
}

bool readYesNo(const std::string& prompt) {
    while (true) {
        const std::string answer = readLine(prompt + " (y/n): ");
        if (answer == "y" || answer == "Y") return true;
        if (answer == "n" || answer == "N") return false;
        std::cout << "Please enter y or n.\n";
    }
}

std::string today() {
    const auto now = std::chrono::system_clock::now();
    const std::time_t time = std::chrono::system_clock::to_time_t(now);
    std::tm localTime{};
#if defined(_WIN32)
    localtime_s(&localTime, &time);
#else
    localtime_r(&time, &localTime);
#endif
    std::ostringstream date;
    date << std::put_time(&localTime, "%Y-%m-%d");
    return date.str();
}

void printHeading(const std::string& title) {
    std::cout << "\n========== " << title << " ==========\n";
}

} // namespace

RideEaseApp::RideEaseApp() : store_("data"), admin_("admin", "admin123") {
    store_.load();
}

void RideEaseApp::showWelcome() const {
    std::cout << "\n==============================================\n"
              << "              RIDE EASE\n"
              << "       Vehicle Rental Management System\n"
              << "==============================================\n";
}

void RideEaseApp::run() {
    showWelcome();
    try {
        while (true) {
            printHeading("MAIN MENU");
            std::cout << "1. Customer registration\n"
                      << "2. Customer login\n"
                      << "3. Admin login\n"
                      << "4. Exit\n";
            const int choice = readInt("Enter choice: ", 1, 4);
            if (choice == 1) customerRegistration();
            else if (choice == 2) customerLogin();
            else if (choice == 3) adminLogin();
            else {
                store_.saveAll();
                std::cout << "Thank you for using RideEase. Goodbye!\n";
                return;
            }
        }
    } catch (const EndOfInputException&) {
        store_.saveAll();
        std::cout << "\nInput stream closed. Saved data and exited RideEase.\n";
    }
}

void RideEaseApp::customerRegistration() {
    printHeading("CUSTOMER REGISTRATION");
    const std::string username = readNonEmpty("Choose username: ");
    if (store_.customerExists(username)) {
        std::cout << "That username is already registered.\n";
        return;
    }
    const std::string password = readNonEmpty("Choose password: ");
    if (password.size() < 4) {
        std::cout << "Password must contain at least 4 characters.\n";
        return;
    }
    const std::string name = readNonEmpty("Full name: ");
    const std::string phone = readNonEmpty("Phone number: ");
    const std::string email = readNonEmpty("Email address: ");
    store_.getCustomers().emplace_back(username, password, name, phone, email);
    if (store_.saveAll()) std::cout << "Registration successful. You can now log in.\n";
    else std::cout << "Registration could not be saved.\n";
}

void RideEaseApp::customerLogin() {
    printHeading("CUSTOMER LOGIN");
    const std::string username = readNonEmpty("Username: ");
    Customer* customer = store_.findCustomer(username);
    if (!customer) {
        std::cout << "Incorrect username or password.\n";
        return;
    }
    const std::string password = readNonEmpty("Password: ");
    if (!customer->verifyPassword(password)) {
        std::cout << "Incorrect username or password.\n";
        return;
    }
    std::cout << "Login successful. Welcome, " << customer->getName() << "!\n";
    customerMenu(*customer);
}

void RideEaseApp::adminLogin() {
    printHeading("ADMIN LOGIN");
    const std::string username = readNonEmpty("Username: ");
    const std::string password = readNonEmpty("Password: ");
    if (username != admin_.getUsername() || !admin_.verifyPassword(password)) {
        std::cout << "Incorrect admin login details.\n";
        return;
    }
    std::cout << "Admin login successful.\n";
    adminMenu();
}

void RideEaseApp::customerMenu(Customer& customer) {
    while (true) {
        printHeading("CUSTOMER MENU");
        std::cout << "1. View available vehicles\n"
                  << "2. Rent a vehicle\n"
                  << "3. Return a vehicle\n"
                  << "4. View rental history\n"
                  << "5. View my details\n"
                  << "6. Logout\n";
        const int choice = readInt("Enter choice: ", 1, 6);
        if (choice == 1) displayVehicles();
        else if (choice == 2) rentVehicle(customer);
        else if (choice == 3) returnVehicle(customer);
        else if (choice == 4) showCustomerHistory(customer);
        else if (choice == 5) {
            printHeading("MY DETAILS");
            customer.displayDetails();
        } else return;
    }
}

void RideEaseApp::displayVehicles() const {
    printHeading("VEHICLE LIST");
    if (store_.getVehicles().empty()) {
        std::cout << "No vehicles are currently registered.\n";
        return;
    }
    std::cout << std::left << std::setw(8) << "ID" << std::setw(28) << "Model"
              << std::setw(10) << "Type" << std::setw(12) << "Price/day"
              << std::setw(12) << "Status" << "Specifications\n";
    std::cout << std::string(96, '-') << '\n';
    for (const auto& vehicle : store_.getVehicles()) vehicle->displayDetails();
}

void RideEaseApp::rentVehicle(Customer& customer) {
    displayVehicles();
    const std::string vehicleId = readNonEmpty("Enter vehicle ID to rent: ");
    const VehiclePtr vehicle = store_.findVehicle(vehicleId);
    if (!vehicle) {
        std::cout << "Vehicle ID not found.\n";
        return;
    }
    if (!vehicle->isAvailable()) {
        std::cout << "That vehicle is already rented. Please choose an available vehicle.\n";
        return;
    }
    const int days = readInt("Number of rental days (1-365): ", 1, 365);
    const double total = vehicle->calculateCharge(days);
    std::cout << "Estimated charge: Rs. " << std::fixed << std::setprecision(2) << total << '\n';
    if (!readYesNo("Confirm rental")) {
        std::cout << "Rental cancelled.\n";
        return;
    }

    store_.getRentals().emplace_back(store_.nextRentalId(), customer.getUsername(),
        vehicle->getId(), vehicle->getType(), vehicle->getModel(), days,
        vehicle->getPricePerDay(), total, today(), "", "ACTIVE");
    vehicle->setAvailable(false);
    if (!store_.saveAll()) {
        vehicle->setAvailable(true);
        store_.getRentals().pop_back();
        std::cout << "Could not save the rental. No changes were made.\n";
        return;
    }

    const Rental& rental = store_.getRentals().back();
    printHeading("RENTAL BILL");
    std::cout << "Rental ID   : " << rental.getRentalId() << '\n'
              << "Customer    : " << customer.getName() << '\n'
              << "Vehicle     : " << vehicle->getId() << " - " << vehicle->getModel() << '\n'
              << "Type        : " << vehicle->getType() << '\n'
              << "Days        : " << days << '\n'
              << "Price/day   : Rs. " << vehicle->getPricePerDay() << '\n'
              << "Total charge: Rs. " << total << '\n'
              << "Rent date   : " << today() << '\n'
              << "Status      : ACTIVE\n";
}

void RideEaseApp::returnVehicle(Customer& customer) {
    printHeading("RETURN VEHICLE");
    std::vector<Rental*> activeRentals;
    for (auto& rental : store_.getRentals()) {
        if (rental.belongsTo(customer.getUsername()) && rental.isActive()) {
            activeRentals.push_back(&rental);
            rental.displaySummary();
        }
    }
    if (activeRentals.empty()) {
        std::cout << "You have no active rentals.\n";
        return;
    }
    const std::string rentalId = readNonEmpty("Enter rental ID to return: ");
    Rental* rental = store_.findRental(rentalId);
    if (!rental || !rental->belongsTo(customer.getUsername()) || !rental->isActive()) {
        std::cout << "Active rental not found for this customer.\n";
        return;
    }
    const VehiclePtr vehicle = store_.findVehicle(rental->getVehicleId());
    rental->markReturned(today());
    if (vehicle) vehicle->setAvailable(true);
    if (store_.saveAll()) {
        std::cout << "Vehicle returned successfully. Final charge: Rs. "
                  << std::fixed << std::setprecision(2) << rental->getTotalCharge() << '\n';
    } else {
        std::cout << "Could not save the return operation.\n";
    }
}

void RideEaseApp::showCustomerHistory(const Customer& customer) const {
    printHeading("RENTAL HISTORY");
    bool found = false;
    for (const auto& rental : store_.getRentals()) {
        if (rental.belongsTo(customer.getUsername())) {
            rental.displaySummary();
            found = true;
        }
    }
    if (!found) std::cout << "No rental history found.\n";
}

void RideEaseApp::adminMenu() {
    while (true) {
        printHeading("ADMIN MENU");
        std::cout << "1. View all vehicles\n"
                  << "2. Add vehicle\n"
                  << "3. Update vehicle\n"
                  << "4. Remove vehicle\n"
                  << "5. View all rentals\n"
                  << "6. Logout\n";
        const int choice = readInt("Enter choice: ", 1, 6);
        if (choice == 1) displayVehicles();
        else if (choice == 2) addVehicle();
        else if (choice == 3) updateVehicle();
        else if (choice == 4) removeVehicle();
        else if (choice == 5) showAllRentals();
        else return;
    }
}

void RideEaseApp::addVehicle() {
    printHeading("ADD VEHICLE");
    const std::string id = readNonEmpty("Vehicle ID: ");
    if (store_.findVehicle(id)) {
        std::cout << "That vehicle ID already exists.\n";
        return;
    }
    const int type = readInt("Type (1 = Car, 2 = Bike): ", 1, 2);
    const std::string model = readNonEmpty("Model: ");
    const double price = readPrice("Rental price per day: Rs. ");
    VehiclePtr vehicle;
    if (type == 1) {
        const int seats = readInt("Number of seats (1-12): ", 1, 12);
        const bool automatic = readYesNo("Is it automatic");
        vehicle = std::make_shared<Car>(id, model, price, seats, automatic);
    } else {
        const int engineCC = readInt("Engine capacity in CC (1-3000): ", 1, 3000);
        const bool helmet = readYesNo("Is a helmet included");
        vehicle = std::make_shared<Bike>(id, model, price, engineCC, helmet);
    }
    store_.getVehicles().push_back(vehicle);
    if (store_.saveAll()) std::cout << "Vehicle added successfully.\n";
    else {
        store_.getVehicles().pop_back();
        std::cout << "Could not save the vehicle.\n";
    }
}

void RideEaseApp::updateVehicle() {
    printHeading("UPDATE VEHICLE");
    const std::string id = readNonEmpty("Vehicle ID to update: ");
    const VehiclePtr vehicle = store_.findVehicle(id);
    if (!vehicle) {
        std::cout << "Vehicle ID not found.\n";
        return;
    }
    const std::string oldModel = vehicle->getModel();
    const double oldPrice = vehicle->getPricePerDay();
    vehicle->setModel(readNonEmpty("New model: "));
    vehicle->setPricePerDay(readPrice("New rental price per day: Rs. "));
    if (auto car = std::dynamic_pointer_cast<Car>(vehicle)) {
        car->setSeats(readInt("New number of seats (1-12): ", 1, 12));
        car->setAutomatic(readYesNo("Is it automatic"));
    } else if (auto bike = std::dynamic_pointer_cast<Bike>(vehicle)) {
        bike->setEngineCC(readInt("New engine capacity in CC (1-3000): ", 1, 3000));
        bike->setHelmetIncluded(readYesNo("Is a helmet included"));
    }
    if (store_.saveAll()) std::cout << "Vehicle updated successfully.\n";
    else {
        vehicle->setModel(oldModel);
        vehicle->setPricePerDay(oldPrice);
        std::cout << "Could not save the update; model and price were restored.\n";
    }
}

void RideEaseApp::removeVehicle() {
    printHeading("REMOVE VEHICLE");
    const std::string id = readNonEmpty("Vehicle ID to remove: ");
    const auto& vehicles = store_.getVehicles();
    const auto iterator = std::find_if(vehicles.begin(), vehicles.end(),
        [&id](const VehiclePtr& vehicle) { return vehicle->getId() == id; });
    if (iterator == vehicles.end()) {
        std::cout << "Vehicle ID not found.\n";
        return;
    }
    if (!(*iterator)->isAvailable()) {
        std::cout << "A rented vehicle cannot be removed until it is returned.\n";
        return;
    }
    const VehiclePtr removed = *iterator;
    store_.getVehicles().erase(iterator);
    if (store_.saveAll()) std::cout << "Vehicle removed successfully.\n";
    else {
        store_.getVehicles().push_back(removed);
        std::cout << "Could not save the removal.\n";
    }
}

void RideEaseApp::showAllRentals() const {
    printHeading("ALL RENTALS");
    if (store_.getRentals().empty()) {
        std::cout << "No rental records found.\n";
        return;
    }
    for (const auto& rental : store_.getRentals()) rental.displaySummary();
}
