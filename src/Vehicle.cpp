#include "Vehicle.h"

#include <algorithm>

Vehicle::Vehicle(const std::string& id, const std::string& model,
                 double pricePerDay, bool available)
    : id_(id), model_(model), pricePerDay_(pricePerDay), available_(available) {}

const std::string& Vehicle::getId() const { return id_; }
const std::string& Vehicle::getModel() const { return model_; }
double Vehicle::getPricePerDay() const { return pricePerDay_; }
bool Vehicle::isAvailable() const { return available_; }

void Vehicle::setModel(const std::string& model) { model_ = model; }
void Vehicle::setPricePerDay(double pricePerDay) { pricePerDay_ = pricePerDay; }
void Vehicle::setAvailable(bool available) { available_ = available; }

std::string Vehicle::cleanField(const std::string& value) {
    std::string clean = value;
    std::replace(clean.begin(), clean.end(), '|', '/');
    return clean;
}
