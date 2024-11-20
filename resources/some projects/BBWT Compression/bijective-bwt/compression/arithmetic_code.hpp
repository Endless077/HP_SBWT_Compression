#include <stdio.h>
#include <iostream>
#include <string>
#include <fstream>

using std::ifstream;
using std::ofstream;
using std::cout;
using std::endl;
using std::ios;

const int CODE_VALUE = 16;
const int MAX_VALUE = ((1 << CODE_VALUE) - 1);
const int MAX_FREQ = 16383;

const int FIRST_QTR = (MAX_VALUE / 4 + 1);
const int HALF = (2 * FIRST_QTR);
const int THIRD_QTR = (3 * FIRST_QTR);

const int NO_OF_CHARS = 256;
const int EOF_SYMBOL = (NO_OF_CHARS + 1);
const int NO_OF_SYMBOLS = (NO_OF_CHARS + 1);

class Compress
{
public:
	unsigned char index_to_char [NO_OF_SYMBOLS];
	int char_to_index [NO_OF_CHARS];
	int cum_freq [NO_OF_SYMBOLS + 1];
	int freq [NO_OF_SYMBOLS + 1];

	Compress(void);
	~Compress(void);
	void update_tables(int sym_index);

};

class Encode : public Compress
{
	int low, high;
	int opposite_bits;
	int buffer;
	int	bits_in_buf;

	ifstream in;
	ofstream out;
public:
	Encode(void);
	~Encode(void);
	
	void write_bit( int bit);
	void output_bits(int bit);
	void end_encoding(void);
	void encode_symbol(int symbol);
	void encode(const char *infile, const char *outfile);
	void encodeData(std::string str_in, const char *outfile);

};


class Decode : public Compress
{
	int low, high;
	int value;

	int buffer;
	int	bits_in_buf;
	bool end_decoding;

	ifstream in;
	ofstream out;
public:
	Decode(void);
	~Decode(void);

	void load_first_value(void);
	void decode(const char *infile, const char *outfile);
	std::string decodeData(const char *infile);
	int decode_symbol(void);
	int get_bit(void);
};