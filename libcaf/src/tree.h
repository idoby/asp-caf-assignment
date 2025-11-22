#ifndef TREE_H
#define TREE_H

#include <unordered_map>
#include <map>

#include <string>
#include <utility>

#include "tree_record.h"

class Tree {
public:
   const std::map<std::string, TreeRecord> records;   // Changed from unordered_map to map
   explicit Tree(const std::map<std::string, TreeRecord>& records): records(records) {} // Changed from unordered_map to map

    std::map<std::string, TreeRecord>::const_iterator record(const std::string& key) const { // Changed from unordered_map to map
        return records.find(key);
    }

};

#endif // TREE_H

