#   _______     _____     ________  
#  |_   __ \   |_   _|   |_   __  | 
#    | |__) |    | |       | |_ \_| 
#    |  __ /     | |   _   |  _| _  
#   _| |  \ \_  _| |__/ | _| |__/ | 
#  |____| |___||________||________|     (Run Length Encoding)

###################################################################################################

def flush_run(encoded, symbol, run_length):
    """
    Write the symbol and its run_length to the encoded list.
    
    Args:
        encoded (list[int]): The output list where encoded data is stored.
        symbol (int): The symbol to encode.
        run_length (int): The number of repetitions of the symbol.
    """
    if run_length == 1:
        # Single occurrence
        if symbol == 255:
            # Single 255 -> write "255 0"
            encoded.extend([255, 0])
        else:
            # Single symbol (not 255)
            encoded.append(symbol)
    else:
        # A run of 2 or more occurrences of the same symbol
        # If run_length > 255, split it into multiple segments
        while run_length > 255:
            encoded.extend([255, 255, symbol])
            run_length -= 255
        # Write the last (or only) run segment
        encoded.extend([255, run_length, symbol])

###################################################################################################

def rle_encode(data):
    """
    Apply Run Length Encoding (RLE) to a list of bytes (0-255).
    
    Args:
        data (list[int]): A list of integers in [0, 255].
        
    Returns:
        list[int]: The RLE-encoded list.
    """
    if not data:
        return []
    
    encoded = []
    current_symbol = data[0]
    run_length = 1
    
    # Iterate over the data starting from the second element
    for next_symbol in data[1:]:
        if next_symbol == current_symbol:
            run_length += 1
        else:
            # Flush the previous run
            flush_run(encoded, current_symbol, run_length)
            current_symbol = next_symbol
            run_length = 1
    
    # Flush the final run
    flush_run(encoded, current_symbol, run_length)
    return encoded

def rle_decode(data):
    """
    Decode a list previously encoded with rle_encode.
    
    Args:
        data (list[int]): RLE-encoded list of integers in [0, 255].
        
    Returns:
        list[int]: The original list of symbols after decoding.
    """
    decoded = []
    index = 0
    data_length = len(data)

    while index < data_length:
        value = data[index]

        if value != 255:
            # Single symbol
            decoded.append(value)
            index += 1
        else:
            # Possible run or single '255'
            if index + 1 >= data_length:
                # If there's no byte after 255, treat it as a single '255'
                decoded.append(255)
                index += 1
            else:
                run_length = data[index+1]
                if run_length == 0:
                    # Single '255'
                    decoded.append(255)
                    index += 2
                else:
                    # Run: we expect a symbol after run_length
                    if index + 2 >= data_length:
                        raise ValueError("RLE decode error: expected a symbol after run_length.")
                    symbol = data[index+2]
                    decoded.extend([symbol] * run_length)
                    index += 3

    return decoded

###################################################################################################
