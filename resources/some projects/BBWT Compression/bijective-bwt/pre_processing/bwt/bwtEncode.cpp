#include <vector>

#include "suffixArray.hpp"
#include "bwtEncode.hpp"

string bwtEncode(const string str) {
    string _string(str);
    _string.push_back(-1);
    vector<int> sa = suffix_array_manber_myers(_string);
    string out;
    for (int idx : sa) {
        int i = idx - 1;
        out += (i == -1) ? -1 : (unsigned char) _string[idx - 1];
    }
    return out;
    
}
