#include "Admin.h"

Admin::Admin(const std::string& username, const std::string& password)
    : username_(username), password_(password) {}

bool Admin::verifyPassword(const std::string& password) const { return password_ == password; }
const std::string& Admin::getUsername() const { return username_; }
