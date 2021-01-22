CC=gcc

CFLAGS=-c -O2 -Wall -std=gnu99

PROTOCOL_FLAGS=$(CFLAGS) -I./protocol/
SERVER_FLAGS=$(CFLAGS) -I./protocol/ -I./server/

all: server

clean:
	rm -f out/*
	rm -f build/server/*.o

server: out/server

build/protocol/%.o: protocol/%.c
	$(CC) $(PROTOCOL_FLAGS) $< -o $@

build/server/%.o: server/%.c
	$(CC) $(SERVER_FLAGS) $< -o $@

out/server: build/server/main.o build/protocol/protocol.o
	$(CC) build/server/*.o build/protocol/*.o -o out/server

