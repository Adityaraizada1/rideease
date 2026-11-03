#ifndef RIDE_EASE_CUSTOMER_H
#define RIDE_EASE_CUSTOMER_H

#include <string>

class Customer {
private:
    std::string username_;
    std::string password_;
    std::string name_;
    std::string phone_;
    std::string email_;

public:
    Customer() = default;
    Customer(const std::string& username, const std::string& password,
             const std::string& name, const std::string& phone,
             const std::string& email);
    ~Customer() = default;

    const std::string& getUsername() const;
    const std::string& getPassword() const;
    const std::string& getName() const;
    const std::string& getPhone() const;
    const std::string& getEmail() const;

    void setName(const std::string& name);
    void setPhone(const std::string& phone);
    void setEmail(const std::string& email);
    bool verifyPassword(const std::string& password) const;
    std::string serialize() const;
    void displayDetails() const;
};

#endif
