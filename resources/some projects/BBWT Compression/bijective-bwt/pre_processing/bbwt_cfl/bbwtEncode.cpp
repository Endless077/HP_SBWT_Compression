#include <iostream>

#include "suffixArray.hpp"
#include "cfl.hpp"
#include "bbwtEncode.hpp"

bool less_rotation(const std::vector<std::string> &factors, Rotation i, Rotation j) {
    int i_w = i.w, i_r = i.r, i_length = factors[i_w].size();
    int j_w = j.w, j_r = j.r, j_length = factors[j_w].size();
    for (int k = 0; k < i_length * j_length; ++k) {
        if ((int) (unsigned char) factors[i_w][i_r] < (int) (unsigned char) factors[j_w][j_r]) {
            return true;
        } else if ((int) (unsigned char) factors[i_w][i_r] > (int) (unsigned char) factors[j_w][j_r]) {
            return false;
        }
        i_r++;
        j_r++;
        if (i_r == i_length)
            i_r = 0;
        if (j_r == j_length)
            j_r = 0;
    }
    return false;
}

std::vector<Rotation> merge_rotation(const std::vector<std::string> &factors, const std::vector<Rotation> &a, const std::vector<Rotation> &b) {
    int a_length = a.size(), b_length = b.size(), length = a_length + b_length;
    std::vector<Rotation> out(length);
    int i = 0, j = 0, k = 0;
    while (i < a_length && j < b_length) {
        if (less_rotation(factors, b[j], a[i])) {
            out[k] = b[j];
            j++;
        } else {
            out[k] = a[i];
            i++;
        }
        k++;
    }
    if (i < a_length) {
        for (int m = i; m < a_length; ++m)
            out[k++] = a[m];
    }
    else if (j < b_length) {
        for (int m = j; m < b_length; ++m)
            out[k++] = b[m];
    }
    return out;
}

std::vector<Rotation> merge_rotations(const std::vector<std::string> &factors, std::vector<std::vector<Rotation>> rotations_of_all_factors) {
    std::vector<Rotation> merged;
    while (rotations_of_all_factors.size() > 0) {
        merged = merge_rotation(factors, merged, rotations_of_all_factors[0]);
        rotations_of_all_factors.erase(rotations_of_all_factors.begin());
    }
    return merged;
}

std::vector<Rotation> sort_rotations(const std::vector<std::string> &factors, std::vector<std::vector<Rotation>> &rotations_of_all_factors){
    for(long unsigned int i = 0; i < rotations_of_all_factors.size();i++) {
        auto suffix_array = suffix_array_manber_myers(factors[i]);
        for (long unsigned int j = 0; j < rotations_of_all_factors[i].size();j++){
            rotations_of_all_factors[i][j].r = suffix_array[j];
        }
    }
    return merge_rotations(factors, rotations_of_all_factors);
}

std::string bbwtEncode(const std::string str) {
    auto factors = cfl(str);
    std::string out(str.size(), ' ');
    
    std::vector<std::vector<Rotation>> rotations_of_factors;
    for (long unsigned int i = 0; i < factors.size();i++) {
        std::vector<Rotation> rotations_of_w(factors[i].size());
        for (long unsigned int j = 0; j < factors[i].size();j++) {
            rotations_of_w[j] = Rotation{(int) i, (int) j};
        }
        rotations_of_factors.push_back(rotations_of_w);
    }
    auto sorted_rotations_of_factors = sort_rotations(factors, rotations_of_factors);
    for (long unsigned int i = 0; i < sorted_rotations_of_factors.size();i++){
        int i_r = sorted_rotations_of_factors[i].r -1;
        if (i_r < 0) {
            i_r += factors[sorted_rotations_of_factors[i].w].size();
        }
        out[i] = factors[sorted_rotations_of_factors[i].w][i_r];
    }
    return out;
}