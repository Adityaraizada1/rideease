#ifndef RIDE_EASE_BIKE_H
#define RIDE_EASE_BIKE_H

#include "Vehicle.h"

class Bike : public Vehicle {
private:
    int engineCC_;
    bool helmetIncluded_;

public:
    Bike(const std::string& id, const std::string& model, double pricePerDay,
         int engineCC, bool helmetIncluded, bool available = true);
    ~Bike() override = default;

    int getEngineCC() const;
    bool isHelmetIncluded() const;
    void setEngineCC(int engineCC);
    void setHelmetIncluded(bool helmetIncluded);

    std::string getType() const override;
    double calculateCharge(int days) const override;
    void displayDetails() const override;
    std::string serialize() const override;
};

#endif
