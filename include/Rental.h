#ifndef RIDE_EASE_RENTAL_H
#define RIDE_EASE_RENTAL_H

#include <string>

class Rental {
private:
    std::string rentalId_;
    std::string customerUsername_;
    std::string vehicleId_;
    std::string vehicleType_;
    std::string vehicleModel_;
    int days_;
    double pricePerDay_;
    double totalCharge_;
    std::string rentDate_;
    std::string returnDate_;
    std::string status_;

public:
    Rental() = default;
    Rental(const std::string& rentalId, const std::string& customerUsername,
           const std::string& vehicleId, const std::string& vehicleType,
           const std::string& vehicleModel, int days, double pricePerDay,
           double totalCharge, const std::string& rentDate,
           const std::string& returnDate, const std::string& status);
    ~Rental() = default;

    const std::string& getRentalId() const;
    const std::string& getCustomerUsername() const;
    const std::string& getVehicleId() const;
    const std::string& getStatus() const;
    double getTotalCharge() const;
    int getDays() const;

    void markReturned(const std::string& returnDate);
    bool belongsTo(const std::string& username) const;
    bool isActive() const;
    std::string serialize() const;
    void displaySummary() const;
};

#endif
