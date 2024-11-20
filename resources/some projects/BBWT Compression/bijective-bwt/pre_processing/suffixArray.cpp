#include <map>
#include <numeric>
#include "suffixArray.hpp"

vector<int> sort_bucket(const string &str, vector<int> &bucket, int order) {
    map<string, vector<int>> d;
    for (int i : bucket) {
        string key = str.substr(i, order);
        d[key].push_back(i);
    }
    vector<int> result;
    for (auto &kv : d) {
        if (kv.second.size() > 1) {
            vector<int> res = sort_bucket(str, kv.second, order * 2);
            result.insert(result.end(), res.begin(), res.end());
        }
        else {
            result.push_back(kv.second[0]);
        }
    }
    return result;
};

vector <int> suffix_array_manber_myers(const string &str) {
    vector <int> indices(str.length());
    iota(indices.begin(), indices.end(), 0);
    return sort_bucket(str, indices, 1);
};