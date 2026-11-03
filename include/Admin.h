#ifndef RIDE_EASE_ADMIN_H
#define RIDE_EASE_ADMIN_H

#include <string>

class Admin {
private:
    std::string username_;
    std::string password_;

public:
    Admin(const std::string& username = "admin",
          const std::string& password = "admin123");
    ~Admin() = default;

    bool verifyPassword(const std::string& password) const;
    const std::string& getUsername() const;
};

#endif
