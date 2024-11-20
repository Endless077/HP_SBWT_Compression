#include <iostream>

#include "bbwtDecode.hpp"

std::vector<int> _construct_t(const std::string &data) {
    std::vector<int> t(data.size());
    std::vector<int> counts(65536, 0);
    for (int i = 0; i < (int) data.size(); i++) {
        counts[(unsigned char) data[i]]++;
    }
    std::vector<int> cum_counts(65536, 0);
    for (int i = 1; i < 65536; i++) {
        cum_counts[i] = cum_counts[i - 1] + counts[i - 1];
    }
    for (int i = 0; i < (int) data.size(); i++) {
        t[i] = cum_counts[(unsigned char) data[i]];
        cum_counts[(unsigned char) data[i]]++;
    }
    return t;
}

std::string bbwtDecode(const std::string &data) {
    std::vector<int> t = _construct_t(data);
    std::string out(data.size(), '\0');
    int i = data.size() - 1;
    for (int j = 0; j < (int) data.size(); j++) {
        if (t[j] == -1) {
            continue;
        }
        int k = j;
        while (t[k] != -1) {
            out[i] = (unsigned char) data[k];
            i--;
            int k_temp = t[k];
            t[k] = -1;
            k = k_temp;
        }
    }
    return out;
}