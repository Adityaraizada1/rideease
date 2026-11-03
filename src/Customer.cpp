#include "Customer.h"

#include <iomanip>
#include <iostream>
#include <sstream>

Customer::Customer(const std::string& username, const std::string& password,
                   const std::string& name, const std::string& phone,
                   const std::string& email)
    : username_(username), password_(password), name_(name), phone_(phone), email_(email) {}

const std::string& Customer::getUsername() const { return username_; }
const std::string& Customer::getPassword() const { return password_; }
const std::string& Customer::getName() const { return name_; }
const std::string& Customer::getPhone() const { return phone_; }
const std::string& Customer::getEmail() const { return email_; }

void Customer::setName(const std::string& name) { name_ = name; }
void Customer::setPhone(const std::string& phone) { phone_ = phone; }
void Customer::setEmail(const std::string& email) { email_ = email; }
bool Customer::verifyPassword(const std::string& password) const { return password_ == password; }

std::string Customer::serialize() const {
    std::ostringstream out;
    out << username_ << '|' << password_ << '|' << name_ << '|' << phone_ << '|' << email_;
    return out.str();
}

void Customer::displayDetails() const {
    std::cout << "Name     : " << name_ << '\n'
              << "Username : " << username_ << '\n'
              << "Phone    : " << phone_ << '\n'
              << "Email    : " << email_ << '\n';
}
