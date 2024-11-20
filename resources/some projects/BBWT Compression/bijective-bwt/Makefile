CC = g++
CFLAGS = 
SRC = compression/huffman

COMPRESSION = ./compression
PRE_PROCESSING = ./pre_processing
BBWT_CFL = ./pre_processing/bbwt_cfl
BWT = ./pre_processing/bwt

OBJS_COMPRESSION = $(wildcard ${COMPRESSION}/*.cpp)
OBJS_PRE_PROCESSING = $(wildcard ${PRE_PROCESSING}/*.cpp)
OBJS_BBWT_CFL = $(wildcard ${BBWT_CFL}/*.cpp)
OBJS_BWT = $(wildcard ${BWT}/*.cpp)

OBJS = ${OBJS_COMPRESSION} ${OBJS_PRE_PROCESSING} ${OBJS_BWT} ${OBJS_BBWT_CFL}

main: ${OBJS}
	$(CC) -I${COMPRESSION} -I${PRE_PROCESSING} -I${BWT} -I${BBWT_CFL} ${OBJS} ./main.cpp $(CFLAGS) -o main

%.o: %.cpp ${DEPS}
	${CC} -I${COMPRESSION} -I${PRE_PROCESSING} -I${BWT} -I${BBWT_CFL} -c -o $@ $< ${CFLAGS}

clean:
	rm -r main compressed decompressed