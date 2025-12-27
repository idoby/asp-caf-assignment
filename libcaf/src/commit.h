#ifndef COMMIT_H
#define COMMIT_H

#include <string>
#include <ctime>
#include <vector>

class Commit {
public:
    /* Immutable commit metadata*/
    const std::string tree_hash;  // Hash of the tree object
    const std::string author;     // Author of the commit
    const std::string message;    // Commit message
    const std::time_t timestamp;  // Timestamp of the commit
    const std::vector<std::string> parents; // Parents commit hashes

    Commit(const std::string& tree_hash,
           const std::string& author,
           const std::string& message,
           std::time_t timestamp,
           const std::vector<std::string>& parents):
          tree_hash(tree_hash), author(author), message(message), timestamp(timestamp), parents(parents) {}

};

#endif // COMMIT_H
