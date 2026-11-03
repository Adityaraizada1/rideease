#ifndef RIDE_EASE_CAR_H
#define RIDE_EASE_CAR_H

#include "Vehicle.h"

class Car : public Vehicle {
private:
    int seats_;
    bool automatic_;

public:
    Car(const std::string& id, const std::string& model, double pricePerDay,
        int seats, bool automatic, bool available = true);
    ~Car() override = default;

    int getSeats() const;
    bool isAutomatic() const;
    void setSeats(int seats);
    void setAutomatic(bool automatic);

    std::string getType() const override;
    double calculateCharge(int days) const override;
    void displayDetails() const override;
    std::string serialize() const override;
};

#endif
