#include "Car.h"

#include <iomanip>
#include <iostream>
#include <sstream>

Car::Car(const std::string& id, const std::string& model, double pricePerDay,
         int seats, bool automatic, bool available)
    : Vehicle(id, model, pricePerDay, available), seats_(seats), automatic_(automatic) {}

int Car::getSeats() const { return seats_; }
bool Car::isAutomatic() const { return automatic_; }
void Car::setSeats(int seats) { seats_ = seats; }
void Car::setAutomatic(bool automatic) { automatic_ = automatic; }

std::string Car::getType() const { return "Car"; }
double Car::calculateCharge(int days) const { return getPricePerDay() * days; }

void Car::displayDetails() const {
    std::cout << std::left << std::setw(8) << getId() << std::setw(28) << getModel()
              << std::setw(10) << getType() << std::setw(12) << std::fixed
              << std::setprecision(2) << getPricePerDay() << std::setw(12)
              << (isAvailable() ? "Available" : "Rented") << "Seats: " << seats_
              << ", " << (automatic_ ? "Automatic" : "Manual") << '\n';
}

std::string Car::serialize() const {
    std::ostringstream out;
    out << "Car|" << cleanField(getId()) << '|' << cleanField(getModel()) << '|'
        << std::fixed << std::setprecision(2) << getPricePerDay() << '|'
        << seats_ << '|' << (automatic_ ? 1 : 0) << '|' << (isAvailable() ? 1 : 0);
    return out.str();
}
