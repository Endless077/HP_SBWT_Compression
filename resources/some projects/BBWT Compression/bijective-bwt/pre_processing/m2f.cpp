#include "m2f.hpp"
   
string MTF::encode(string str) {
    fillSymbolTable();
    vector<int> output;
    for(string::iterator it = str.begin(); it != str.end(); it++ ) {
        for(int i = 0; i < 257; i++) {
            if((unsigned char) *it == symbolTable[i]) {
                output.push_back(i);
                moveToFront((int) (unsigned char) i);
                break;
            }
        }
    }
        
    string r;
    for(vector<int>::iterator it = output.begin(); it != output.end(); it++) {
	    ostringstream ss;
        ss << *it;
        r += ss.str() + " ";
    }
    return r;
}

string MTF::decode(string str) {
    fillSymbolTable();
    istringstream iss(str); 
    vector<int> output;
    copy(istream_iterator<int>(iss), istream_iterator<int>(), back_inserter<vector<int> >(output));
    string r;
	
    for(vector<int>::iterator it = output.begin(); it != output.end(); it++) {
	    r.append(1, symbolTable[*it]);
	    moveToFront(*it);
	}

	return r;
}

void MTF::moveToFront(int i) {
    char t = symbolTable[i];
    for(int z = i - 1; z >= 0; z--) {
        symbolTable[z + 1] = symbolTable[z];
    }
    symbolTable[0] = t;
}

void MTF::fillSymbolTable() {
    for(int x = 0; x < 256; x++)
        symbolTable[x] = x;
    symbolTable[256] = -1;
}

/*
int main() {
    MTF mtf;
    string a, str[] = { "broood", "bananaaa", "hiphophiphop" };

    for( int x = 0; x < 3; x++ ) {
        a = str[x];
        cout << a << " -> encoded = ";
        a = mtf.encode( a );
        cout << a << "; decoded = " << mtf.decode( a ) << endl;
    }
    
    return 0;
}
*/