#ifndef RIDE_EASE_DATA_STORE_H
#define RIDE_EASE_DATA_STORE_H

#include "Customer.h"
#include "Rental.h"
#include "Vehicle.h"

#include <string>
#include <vector>

class DataStore {
private:
    std::string dataDirectory_;
    std::vector<VehiclePtr> vehicles_;
    std::vector<Customer> customers_;
    std::vector<Rental> rentals_;

    void ensureDataFiles();
    void reconcileAvailability();

public:
    explicit DataStore(const std::string& dataDirectory = "data");
    ~DataStore() = default;

    void load();
    bool saveAll() const;

    std::vector<VehiclePtr>& getVehicles();
    const std::vector<VehiclePtr>& getVehicles() const;
    std::vector<Customer>& getCustomers();
    const std::vector<Customer>& getCustomers() const;
    std::vector<Rental>& getRentals();
    const std::vector<Rental>& getRentals() const;

    VehiclePtr findVehicle(const std::string& id) const;
    Customer* findCustomer(const std::string& username);
    const Customer* findCustomer(const std::string& username) const;
    Rental* findRental(const std::string& rentalId);
    bool customerExists(const std::string& username) const;
    std::string nextRentalId() const;
};

#endif
