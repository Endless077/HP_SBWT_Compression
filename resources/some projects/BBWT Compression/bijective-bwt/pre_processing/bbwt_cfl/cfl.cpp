#include "cfl.hpp"

vector<string> cfl(string str) {
    vector<string> words;
    while (str.length() > 0) {
        int i = 0;
        int j = 1;
        while (j < (int) str.length() && (unsigned char) str[i] <= (unsigned char) str[j]) {
            if (str[i] == str[j]) {
                i++;
            } else {
                i = 0;
            }
            j++;
        }
        int l = j - i;
        while (i >= 0) {
            words.push_back(str.substr(0, l));
            str = str.substr(l);
            i -= l;
        }
    }
    return words;
}