#include "DataStore.h"

#include "Bike.h"
#include "Car.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>

namespace {

std::vector<std::string> split(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream stream(line);
    std::string field;
    while (std::getline(stream, field, '|')) {
        if (!field.empty() && field.back() == '\r') {
            field.pop_back();
        }
        fields.push_back(field);
    }
    return fields;
}

bool toBool(const std::string& value) { return value == "1" || value == "true"; }

} // namespace

DataStore::DataStore(const std::string& dataDirectory) : dataDirectory_(dataDirectory) {
    ensureDataFiles();
}

void DataStore::ensureDataFiles() {
    std::filesystem::create_directories(dataDirectory_);
    const std::vector<std::pair<std::string, std::string>> files = {
        {"vehicles.txt", "Car|C101|Maruti Swift|1800.00|5|0|1\n"
                          "Car|C102|Hyundai i20|2200.00|5|1|1\n"
                          "Bike|B101|Honda Activa 6G|700.00|110|1|1\n"
                          "Bike|B102|Royal Enfield Classic 350|1200.00|350|0|1\n"},
        {"customers.txt", ""},
        {"rentals.txt", ""}};

    for (const auto& file : files) {
        const std::filesystem::path path = std::filesystem::path(dataDirectory_) / file.first;
        if (!std::filesystem::exists(path)) {
            std::ofstream output(path);
            output << file.second;
        }
    }
}

void DataStore::load() {
    vehicles_.clear();
    customers_.clear();
    rentals_.clear();

    std::ifstream vehicleFile(std::filesystem::path(dataDirectory_) / "vehicles.txt");
    std::string line;
    while (std::getline(vehicleFile, line)) {
        if (line.empty()) continue;
        const auto fields = split(line);
        try {
            if (fields.size() != 7) continue;
            const std::string& type = fields[0];
            const std::string& id = fields[1];
            const std::string& model = fields[2];
            const double price = std::stod(fields[3]);
            if (type == "Car") {
                vehicles_.push_back(std::make_shared<Car>(id, model, price,
                    std::stoi(fields[4]), toBool(fields[5]), toBool(fields[6])));
            } else if (type == "Bike") {
                vehicles_.push_back(std::make_shared<Bike>(id, model, price,
                    std::stoi(fields[4]), toBool(fields[5]), toBool(fields[6])));
            }
        } catch (const std::exception&) {
            // Ignore malformed records and keep the remaining data usable.
        }
    }

    std::ifstream customerFile(std::filesystem::path(dataDirectory_) / "customers.txt");
    while (std::getline(customerFile, line)) {
        if (line.empty()) continue;
        const auto fields = split(line);
        if (fields.size() == 5) {
            customers_.emplace_back(fields[0], fields[1], fields[2], fields[3], fields[4]);
        }
    }

    std::ifstream rentalFile(std::filesystem::path(dataDirectory_) / "rentals.txt");
    while (std::getline(rentalFile, line)) {
        if (line.empty()) continue;
        const auto fields = split(line);
        try {
            if (fields.size() != 11) continue;
            rentals_.emplace_back(fields[0], fields[1], fields[2], fields[3], fields[4],
                std::stoi(fields[5]), std::stod(fields[6]), std::stod(fields[7]),
                fields[8], fields[9], fields[10]);
        } catch (const std::exception&) {
            // Ignore malformed records and keep the remaining data usable.
        }
    }

    reconcileAvailability();
}

void DataStore::reconcileAvailability() {
    for (const auto& vehicle : vehicles_) {
        vehicle->setAvailable(true);
    }
    for (const auto& rental : rentals_) {
        if (rental.isActive()) {
            const auto vehicle = findVehicle(rental.getVehicleId());
            if (vehicle) vehicle->setAvailable(false);
        }
    }
}

bool DataStore::saveAll() const {
    std::ofstream vehicleFile(std::filesystem::path(dataDirectory_) / "vehicles.txt");
    std::ofstream customerFile(std::filesystem::path(dataDirectory_) / "customers.txt");
    std::ofstream rentalFile(std::filesystem::path(dataDirectory_) / "rentals.txt");
    if (!vehicleFile || !customerFile || !rentalFile) return false;

    for (const auto& vehicle : vehicles_) vehicleFile << vehicle->serialize() << '\n';
    for (const auto& customer : customers_) customerFile << customer.serialize() << '\n';
    for (const auto& rental : rentals_) rentalFile << rental.serialize() << '\n';
    return true;
}

std::vector<VehiclePtr>& DataStore::getVehicles() { return vehicles_; }
const std::vector<VehiclePtr>& DataStore::getVehicles() const { return vehicles_; }
std::vector<Customer>& DataStore::getCustomers() { return customers_; }
const std::vector<Customer>& DataStore::getCustomers() const { return customers_; }
std::vector<Rental>& DataStore::getRentals() { return rentals_; }
const std::vector<Rental>& DataStore::getRentals() const { return rentals_; }

VehiclePtr DataStore::findVehicle(const std::string& id) const {
    for (const auto& vehicle : vehicles_) {
        if (vehicle->getId() == id) return vehicle;
    }
    return nullptr;
}

Customer* DataStore::findCustomer(const std::string& username) {
    for (auto& customer : customers_) {
        if (customer.getUsername() == username) return &customer;
    }
    return nullptr;
}

const Customer* DataStore::findCustomer(const std::string& username) const {
    for (const auto& customer : customers_) {
        if (customer.getUsername() == username) return &customer;
    }
    return nullptr;
}

Rental* DataStore::findRental(const std::string& rentalId) {
    for (auto& rental : rentals_) {
        if (rental.getRentalId() == rentalId) return &rental;
    }
    return nullptr;
}

bool DataStore::customerExists(const std::string& username) const {
    return findCustomer(username) != nullptr;
}

std::string DataStore::nextRentalId() const {
    int nextNumber = 1;
    for (const auto& rental : rentals_) {
        const std::string prefix = "RENT-";
        if (rental.getRentalId().rfind(prefix, 0) == 0) {
            try {
                nextNumber = std::max(nextNumber, std::stoi(rental.getRentalId().substr(prefix.size())) + 1);
            } catch (const std::exception&) {
                // Keep the next valid number when an old record has a custom ID.
            }
        }
    }
    std::ostringstream id;
    id << "RENT-" << std::setw(3) << std::setfill('0') << nextNumber;
    return id.str();
}
