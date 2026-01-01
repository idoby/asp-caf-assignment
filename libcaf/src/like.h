#ifndef LIKE_H
#define LIKE_H

#include <string>
#include <ctime>

class Like {
public:
    const std::string commit_hash;   
    const std::string user;          
    const std::time_t timestamp;    

    Like(const std::string& commit_hash, const std::string& user, std::time_t timestamp) commit_hash(commit_hash),user(user), timestamp(timestamp) {}
};
#endif