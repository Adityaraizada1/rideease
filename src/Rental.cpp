#include "Rental.h"

#include <iomanip>
#include <iostream>
#include <sstream>

Rental::Rental(const std::string& rentalId, const std::string& customerUsername,
               const std::string& vehicleId, const std::string& vehicleType,
               const std::string& vehicleModel, int days, double pricePerDay,
               double totalCharge, const std::string& rentDate,
               const std::string& returnDate, const std::string& status)
    : rentalId_(rentalId), customerUsername_(customerUsername), vehicleId_(vehicleId),
      vehicleType_(vehicleType), vehicleModel_(vehicleModel), days_(days),
      pricePerDay_(pricePerDay), totalCharge_(totalCharge), rentDate_(rentDate),
      returnDate_(returnDate), status_(status) {}

const std::string& Rental::getRentalId() const { return rentalId_; }
const std::string& Rental::getCustomerUsername() const { return customerUsername_; }
const std::string& Rental::getVehicleId() const { return vehicleId_; }
const std::string& Rental::getStatus() const { return status_; }
double Rental::getTotalCharge() const { return totalCharge_; }
int Rental::getDays() const { return days_; }

void Rental::markReturned(const std::string& returnDate) {
    returnDate_ = returnDate;
    status_ = "RETURNED";
}

bool Rental::belongsTo(const std::string& username) const { return customerUsername_ == username; }
bool Rental::isActive() const { return status_ == "ACTIVE"; }

std::string Rental::serialize() const {
    std::ostringstream out;
    out << rentalId_ << '|' << customerUsername_ << '|' << vehicleId_ << '|'
        << vehicleType_ << '|' << vehicleModel_ << '|' << days_ << '|'
        << std::fixed << std::setprecision(2) << pricePerDay_ << '|'
        << totalCharge_ << '|' << rentDate_ << '|' << returnDate_ << '|'
        << status_;
    return out.str();
}

void Rental::displaySummary() const {
    std::cout << "Rental ID: " << rentalId_ << " | Vehicle: " << vehicleId_ << " ("
              << vehicleModel_ << ") | Days: " << days_ << " | Charge: Rs. "
              << std::fixed << std::setprecision(2) << totalCharge_ << " | Rented: "
              << rentDate_ << " | Status: " << status_;
    if (!returnDate_.empty()) {
        std::cout << " | Returned: " << returnDate_;
    }
    std::cout << '\n';
}
