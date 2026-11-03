#include "Bike.h"

#include <iomanip>
#include <iostream>
#include <sstream>

Bike::Bike(const std::string& id, const std::string& model, double pricePerDay,
           int engineCC, bool helmetIncluded, bool available)
    : Vehicle(id, model, pricePerDay, available), engineCC_(engineCC),
      helmetIncluded_(helmetIncluded) {}

int Bike::getEngineCC() const { return engineCC_; }
bool Bike::isHelmetIncluded() const { return helmetIncluded_; }
void Bike::setEngineCC(int engineCC) { engineCC_ = engineCC; }
void Bike::setHelmetIncluded(bool helmetIncluded) { helmetIncluded_ = helmetIncluded; }

std::string Bike::getType() const { return "Bike"; }
double Bike::calculateCharge(int days) const { return getPricePerDay() * days; }

void Bike::displayDetails() const {
    std::cout << std::left << std::setw(8) << getId() << std::setw(28) << getModel()
              << std::setw(10) << getType() << std::setw(12) << std::fixed
              << std::setprecision(2) << getPricePerDay() << std::setw(12)
              << (isAvailable() ? "Available" : "Rented") << "Engine: " << engineCC_
              << "cc, " << (helmetIncluded_ ? "Helmet included" : "Helmet not included")
              << '\n';
}

std::string Bike::serialize() const {
    std::ostringstream out;
    out << "Bike|" << cleanField(getId()) << '|' << cleanField(getModel()) << '|'
        << std::fixed << std::setprecision(2) << getPricePerDay() << '|'
        << engineCC_ << '|' << (helmetIncluded_ ? 1 : 0) << '|'
        << (isAvailable() ? 1 : 0);
    return out.str();
}
