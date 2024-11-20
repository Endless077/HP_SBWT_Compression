#include "arithmetic_code.hpp"

Encode::Encode(void)
{
	buffer = 0;
	bits_in_buf = 0;

	low = 0;
	high = MAX_VALUE;
	opposite_bits = 0;
}

Encode::~Encode(void)
{
}

void Encode::encode(const char *infile, const char *outfile)
{
	in.open(infile, ios::binary | ios::in);
	out.open(outfile, ios::binary | ios::out);
	if (!in || !out)
	{
		cout<<"Error: Can`t open file"<<endl;
		return;
	}
	while (true)
	{
		int ch;
		int symbol;
		ch = in.get();
		if (in.eof())
		{
			break;
		}
		symbol = char_to_index[ch];
		encode_symbol(symbol);
		update_tables(symbol);
	}
	encode_symbol(EOF_SYMBOL);
	end_encoding();
	in.close();
	out.close();
}

void Encode::encodeData(std::string str_in, const char *outfile)
{
	out.open(outfile, ios::binary | ios::out);
	if (!out) {
		cout<< "Error: Can`t open file" <<endl;
		return;
	}
	int i = 0;
	while (true) {
		int ch;
		int symbol;
		ch = (unsigned char) str_in[i++];
		if (str_in[i - 1] == EOF || str_in[i - 1] ==0) {
			break;
		}
		symbol = char_to_index[ch];
		encode_symbol(symbol);
		update_tables(symbol);
	}
	encode_symbol(EOF_SYMBOL);
	end_encoding();
	in.close();
	out.close();
}

void Encode::encode_symbol(int symbol)
{
	int range;

	range = high - low;
	high = low + (range * cum_freq [symbol - 1]) / cum_freq [0];
	low = low + (range * cum_freq [symbol]) / cum_freq [0];
	for (;;)
	{
	if (high < HALF)
		output_bits(0);
	else if (low >= HALF)
	{
		output_bits(1);
		low -= HALF;
		high -= HALF;
	}
	else if (low >= FIRST_QTR && high < THIRD_QTR)
	{
		opposite_bits++;
		low -= FIRST_QTR;
		high -= FIRST_QTR;
	}
	else
		break;
	low = 2 * low;
	high = 2 * high;
	}
}

void Encode::end_encoding(void)
{
  opposite_bits++;
  if (low < FIRST_QTR)
    output_bits(0);
  else
    output_bits(1);

  out.put(buffer >> bits_in_buf);
}

void Encode::output_bits(int bit)
{
	write_bit(bit);
	while (opposite_bits > 0)
	{
		write_bit(!bit);
		opposite_bits--;
	}
}

void Encode::write_bit(int bit)
{
	buffer >>= 1;
	if (bit)
	buffer |= 0x80;
	bits_in_buf++;
	if (bits_in_buf == 8)
	{
		out.put(buffer);
		bits_in_buf = 0;
	}
}

Compress::Compress(void)
{
	int i;
	for ( i = 0; i < NO_OF_CHARS; i++)
	{
		char_to_index[i] = i + 1;
		index_to_char[i + 1] = i;
	}
	for ( i = 0; i <= NO_OF_SYMBOLS; i++)
	{
		freq[i] = 1;
		cum_freq[i] = NO_OF_SYMBOLS - i;
	}
	freq[0] = 0;
}

Compress::~Compress(void)
{
}

void Compress::update_tables(int sym_index)
{
  int i;
  if (cum_freq[0] == MAX_FREQ)
  {
    int cum = 0;
    for ( i = NO_OF_SYMBOLS; i >= 0; i--)
    {
      freq[i] = (freq[i] + 1) / 2;
      cum_freq[i] = cum;
      cum += freq[i];
    }
  }
  for ( i = sym_index; freq[i] == freq[i - 1]; i--);
  if (i < sym_index)
  {
	int ch_i, ch_symbol;
    ch_i = index_to_char[i];
    ch_symbol = index_to_char[sym_index];
    index_to_char[i] = ch_symbol;
    index_to_char[sym_index] = ch_i;
    char_to_index[ch_i] = sym_index;
    char_to_index[ch_symbol] = i;
  }
  freq[i]++;
  while (i > 0)
  {
	i--;
    cum_freq[i]++;
  }
}

Decode::Decode(void)
{
	buffer = 0;
	bits_in_buf = 0;
	end_decoding = false;

	low = 0;
	high = MAX_VALUE;
}

Decode::~Decode(void)
{
}

void Decode::load_first_value(void)
{
	value = 0;
	for (int i = 1; i <= CODE_VALUE; i++)
		value = 2 * value + get_bit();
}

void Decode::decode(const char *infile, const char *outfile)
{
	in.open(infile, ios::binary | ios::in);
	out.open(outfile, ios::binary | ios::out);
	if (!in || !out)
	{
		cout<<"Error: Can`t open file"<<endl;
		return;
	}
	load_first_value();
	while (true)
	{
		int ch;
		int sym_index;
		sym_index = decode_symbol();
		if ((sym_index == EOF_SYMBOL) || end_decoding)
			break;
		ch = index_to_char[sym_index];
		out.put(ch);
		update_tables(sym_index);
	}
	in.close();
	out.close();
}

std::string Decode::decodeData(const char *infile) {
	std::string str_out = "";
	char app_char;
	std::string s;
	in.open(infile, ios::binary | ios::in);
	if (!in) {
		cout << "Error: Can`t open file" << endl;
		return "";
	}
	load_first_value();
	while (true) {
		int ch;
		int sym_index;
		sym_index = decode_symbol();
		if ((sym_index == EOF_SYMBOL) || end_decoding)
			break;
		ch = index_to_char[sym_index];
		app_char = (char)ch;
		str_out.push_back(app_char);
		update_tables(sym_index);
	}
	in.close();
	out.close();
	return str_out;
}


int Decode::decode_symbol(void)
{
	int range;
	int cum; 
	int symbol_index;

	range = high - low;
	cum = ((((value - low) + 1) * cum_freq[0] - 1) / range); // +- Íóæíî äëÿ òî ëè îêðóãëåíèÿ òî ëè ïðåîáðàçîâàíèÿ, íî èíà÷å íå ðàáîòàåò
	for (symbol_index = 1; cum_freq[symbol_index] > cum; symbol_index++);
	high = low + (range * cum_freq[symbol_index - 1]) / cum_freq[0];
	low = low + (range * cum_freq[symbol_index]) / cum_freq[0];
	for (;;)
	{
		if (high < HALF)
		{
		}
		else if (low >= HALF)
		{
			value -= HALF;
			low -= HALF;
			high -= HALF;
		}
		else if (low >= FIRST_QTR && high < THIRD_QTR)
		{
			value -= FIRST_QTR;
			low -= FIRST_QTR;
			high -= FIRST_QTR;
		}
		else
			break;
		low = 2 * low;
		high = 2 * high;
		value = 2 * value + get_bit();
	}
	return symbol_index;
}

int Decode::get_bit(void)
{
	int t;
	if (bits_in_buf == 0)
	{
		buffer = in.get();
		if (buffer == EOF)
		{
			end_decoding = true;
			return -1;
		}
		bits_in_buf= 8;
	}
	t = buffer & 1;
	buffer >>= 1;
	bits_in_buf--;
	return t;
}