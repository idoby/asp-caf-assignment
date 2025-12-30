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
    std::string parents_str;
    for (const auto& parent : commit.parents) {
        parents_str += parent;
    }
    return hash_string(commit.tree_hash + commit.author + commit.message +
                       std::to_string(commit.timestamp) + parents_str);
}