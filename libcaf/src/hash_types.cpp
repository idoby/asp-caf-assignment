#include "hash_types.h"
#include "caf.h"

std::string hash_object(const Blob& blob) {
    return blob.hash;
}

std::string hash_object(const Tree& tree) {
    std::string acc_std;

    for (const auto& [key, record] : tree.records) {
        acc_std += record.name + std::to_string(static_cast<int>(record.type)) + record.hash;
    }

    return hash_string(acc_std);
}

std::string hash_object(const Commit& commit) {
    std::string acc;

    acc += commit.tree_hash;
    acc += commit.author;
    acc += commit.message;
    acc += std::to_string(commit.timestamp);

    for (const auto& parent : commit.parents) {
        acc += parent;
    }

    return hash_string(acc);
}