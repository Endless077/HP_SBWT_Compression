#include <map>
#include <iostream>
#include <algorithm>

#include "bwtDecode.hpp"

vector<map<char, int>> fm_index(string bwt) {
    vector<map<char, int>> fm;
    map<char, int> firstRow;
    for (char c : bwt) {
        firstRow[(int) (unsigned char) c] = 0;
    }
    fm.push_back(firstRow);
    for (char c : bwt) {
        map<char, int> lastRow = fm.back();
        map<char, int> currentRow;
        for (auto const &symbolCount : lastRow) {
            char symbol = symbolCount.first;
            int count = symbolCount.second;
            currentRow[(int) (unsigned char) symbol] = count + (symbol == c);
        }
        fm.push_back(currentRow);
    }
    return fm;
}

map<char, int> createOffsets(const map<char, int> &lastRow) {
    map<char, int> offset;
    int n = 0;

    vector<unsigned char> keys;
    for (auto const &pair: lastRow) {
        if (pair.first != - 1)
            keys.push_back(pair.first);
    }
    sort(begin(keys), end(keys));
    keys.push_back(-1);

    for (unsigned long int i = 0; i < keys.size(); i++) {
        char symbol = keys[i];
        int count = lastRow.at(symbol);
        offset[symbol] = n;
        n += count;
    }
    return offset;
}

string recover_suffix(int i, const string &bwt, const vector<map<char, int>> &fm_index, const map<char, int> &offset) {
    string suffix;
    char c = bwt[i];
    int predecessor = offset.at(c) + fm_index[i].at(c);
    suffix = c + suffix;
    while (predecessor != i) {
        c = bwt[predecessor];
        predecessor = offset.at(c) + fm_index[predecessor].at(c);
        suffix = c + suffix;
    }
    return suffix;
}

string bwtDecode(string str) {
    vector<map<char, int>> fm = fm_index(str);
    auto offset = createOffsets(fm.back());
    int i = str.find(-1);
    string s = recover_suffix(i, str, fm, offset);
    return s.substr(0, s.length() - 1);
}
