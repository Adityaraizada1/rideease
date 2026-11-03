#ifndef RIDE_EASE_VEHICLE_H
#define RIDE_EASE_VEHICLE_H

#include <memory>
#include <string>

class Vehicle {
private:
    std::string id_;
    std::string model_;
    double pricePerDay_;
    bool available_;

protected:
    // Used by derived classes while rebuilding their CSV representation.
    static std::string cleanField(const std::string& value);

public:
    Vehicle(const std::string& id, const std::string& model,
            double pricePerDay, bool available = true);
    virtual ~Vehicle() = default;

    const std::string& getId() const;
    const std::string& getModel() const;
    double getPricePerDay() const;
    bool isAvailable() const;

    void setModel(const std::string& model);
    void setPricePerDay(double pricePerDay);
    void setAvailable(bool available);

    virtual std::string getType() const = 0;
    virtual double calculateCharge(int days) const = 0;
    virtual void displayDetails() const = 0;
    virtual std::string serialize() const = 0;
};

using VehiclePtr = std::shared_ptr<Vehicle>;

#endif
