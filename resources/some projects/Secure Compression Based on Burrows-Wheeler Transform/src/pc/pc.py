from dahuffman import HuffmanCodec
import pickle
#import json
import pc.lzw as lzw
import pc.arithmetic_compress as arithmetic_compress
import pc.arithmetic_decompress as arithmetic_decompress
import pc.ae_lib.arithmeticcoding as arithmeticcoding
import bz2
import contextlib
import os

def compress(input, flag: int):
    '''
    To select Desired Algorithm:\n
    0 = Huffman\n
    1 = Arithmetic Coding (Non implementato)\n
    2 = LZW\n
    3 = BZip2
    '''
    encoded = ""

    if flag == 0:
        print("using Huffman")
        codec = HuffmanCodec.from_data(input)
        encoded = codec.encode(input)
        fileOutputPCCodec = open("TestFiles/Output/outputPCCodec.txt", "wb")
        pickle.dump(codec, fileOutputPCCodec)
        
    elif flag == 1:
        print("using Arithmetic Coding")
        '''file_in = open("TestFiles/Output/outputRLE.txt", "rb")
        file_out = open("TestFiles/Output/outputPC.txt", "wb")
        ppm_compress.compress(file_in, file_out)'''

        inputfile = "TestFiles/Output/outputRLE.txt"
        outputfile = "TestFiles/Output/outputPC.txt"
        '''with open("TestFiles/Output/outputRLE.txt", "rb") as inp, \
                contextlib.closing(arithmeticcoding.BitOutputStream(open("TestFiles/Output/outputPC.txt", "wb"))) as bitout:
            ppm_compress.compress(inp, bitout)'''
        arithmetic_compress.main(inputfile, outputfile)
        return 
        
    elif flag == 2:
        print("using LZW")
        encoded, dictionary = lzw.compress(input)
        fileOutputDict = open("TestFiles/Output/outputDictLZW.txt", "wb")
        pickle.dump(dictionary, fileOutputDict)
        
        # LZW
    elif flag == 3:
        print("using bzip2")
        encoded = bz2.compress(input.encode())

    fileOutputPC = open("TestFiles/Output/outputPC.txt", "wb")
    pickle.dump(encoded, fileOutputPC)


def decompress(input, flag):
    '''
    To select Desired Algorithm:\n
    0 = Huffman\n
    1 = Arithmetic Coding\n
    2 = LZW\n
    3 = BZip2
    '''

    output = ""
    
    if flag == 0:
        print("using Huffman")
        codecFile = open("TestFiles/Output/outputPCCodec.txt", "rb")
        codec = pickle.load(codecFile)
        output = codec.decode(input)
    
    elif flag == 1:
        print("using Arithmetic Coding")
        inputfile = "TestFiles/Output/outputPC.txt"
        tempFile = "TestFiles/Output/tempDecoded.txt"
        arithmetic_decompress.main(inputfile, tempFile)
        temp = open(tempFile, "rb")
        tempOutput = temp.read()
        temp.close()
        os.remove(tempFile)
        output = tempOutput.decode()

    elif flag == 2:
        print("using LZW")
        fileDict = open("TestFiles/Output/outputDictLZW.txt", "rb")
        dictionary = pickle.load(fileDict)
        output = lzw.decompress(input, dictionary).decode()
    elif flag == 3:
        print("using bzip2")
        output = bz2.decompress(input).decode()

    return output 

if __name__ == "__main__":
    input = "money"
    encoded = compress(input, 1)
    print("CODIFICA:", encoded)
    decoded = decompress(encoded, 1)
    print("Decodifica:", decoded, "UGUALI?", input == decoded)