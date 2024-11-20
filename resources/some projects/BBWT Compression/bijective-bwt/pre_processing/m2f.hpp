#ifndef M2F_HPP
#define M2F_HPP

#include <iostream>
#include <iterator>
#include <sstream>
#include <vector>

using namespace std;

class MTF {

    unsigned char symbolTable[257];

    public:inline string encode(string str);

    inline string decode(string str);

    private:inline void moveToFront(int i);

    inline void fillSymbolTable();

};

#endif