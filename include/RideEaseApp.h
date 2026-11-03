#ifndef RIDE_EASE_APP_H
#define RIDE_EASE_APP_H

#include "Admin.h"
#include "DataStore.h"

#include <string>

class RideEaseApp {
private:
    DataStore store_;
    Admin admin_;

    void showWelcome() const;
    void customerRegistration();
    void customerLogin();
    void adminLogin();
    void customerMenu(Customer& customer);
    void adminMenu();

    void displayVehicles() const;
    void rentVehicle(Customer& customer);
    void returnVehicle(Customer& customer);
    void showCustomerHistory(const Customer& customer) const;
    void addVehicle();
    void updateVehicle();
    void removeVehicle();
    void showAllRentals() const;

public:
    RideEaseApp();
    ~RideEaseApp() = default;
    void run();
};

#endif
