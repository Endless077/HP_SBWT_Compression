#include <vector>
#include "rle.hpp"

vector<string> explode(const string& str, const char& ch) {
    string next;
    vector<string> result;
    // For each character in the string
    for (string::const_iterator it = str.begin(); it != str.end(); it++) {
        // If we've hit the terminal character
        if (*it == ch) {
            // If we have some characters accumulated
            if (!next.empty()) {
                // Add them to the result vector
                result.push_back(next);
                next.clear();
            }
        } else {
            // Accumulate the next character into the sequence
            next += *it;
        }
    }
    if (!next.empty())
         result.push_back(next);
    return result;
}

std::string RunLengthEncoding(const std::string &s) {
  std::string encoded_string;
  for (int i = 0; i < s.length(); i++) {
    int count = 1;
    while (i + 1 < s.length() && s[i] == s[i + 1]) {
      count++;
      i++;
    }
    encoded_string += std::to_string(count) + '-' + s[i];
  }
  return encoded_string;
}

std::string RunLengthDecoding(const std::string &s) {
  std::string decoded_string;
  for (int i = 0; i < s.length(); i++) {
    int count = 0;
    while (isdigit(s[i])) {
      count = count * 10 + (s[i] - '0');
      i++;
    }
    i++;  // skip the separator '-'
    for (int j = 0; j < count; j++) {
      decoded_string += s[i];
    }
  }
  return decoded_string;
}

std::string rleEncode(const std::string &s) {
  std::string encoded_string;
  vector<string> numbers = explode(s, ' ');
  for (int i = 0; i < numbers.size(); i++) {
    int count = 1;
    while (i + 1 < numbers.size() && numbers[i] == numbers[i + 1]) {
      count++;
      i++;
    }
    encoded_string += std::to_string(count) + ' ' + numbers[i] + " ";
  }
  return encoded_string;
}

std::string rleDecode(const std::string &s) {
  std::string decoded_string;
  vector<string> numbers = explode(s, ' ');
  string num = numbers[numbers.size() -1];
  if (num.size() > 1 && num[0] == '0')
    numbers[numbers.size() - 1] = "0";
  for (int i = 0; i < numbers.size(); i++) {
    int count = stoi(numbers[i]);
    i++;
    for (int j = 0; j < count; j++) {
      decoded_string += numbers[i] + " ";
    }
  }
  return decoded_string;
}
