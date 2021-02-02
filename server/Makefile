CC=gcc

CFLAGS=-c -O2 -Wall -std=gnu99

SERVER_FLAGS=$(CFLAGS) -I./server/

all: server

clean:
	rm -f out/*
	rm -f build/server/*.o

server: out/server

build/server:
	mkdir -p build/server

out:
	mkdir -p out

build/server/%.o: server/%.c
	$(CC) $(SERVER_FLAGS) $< -o $@

out/server: out build/server build/server/main.o build/server/list.o build/server/network.o build/server/buffer.o build/server/protocol.o build/server/game.o
	$(CC) build/server/*.o -o out/server


