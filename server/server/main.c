#include "protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct position_data_t {
    int alive;
    pkt_position_t position;
} position_data_t;

typedef struct player_data {
    uint8_t id;
    int fd;
    pkt_buffer_t *receive_buffer;
    position_data_t positions[INITIAL_POSITIONS];
} player_data_t;

#define STATE_WAITING 0
#define STATE_GAMEPLAY 1
#define STATE_AWAITING_FILE_INFO 2
#define STATE_AWAITING_FILE_DATA 3

typedef struct game_data {
    player_data_t players[PLAYER_COUNT];
    int state;
} game_data_t;

int create_listen_socket(uint16_t port)
{
    return 0;
}

int make_socket_unblocking(int socket)
{

}

int main(int argc, char *argv[])
{
    int listen_socket = create_listen_socket(SERVER_PORT);
    if (listen_socket == -1) {
        perror("Could not create listen socket\n");
        return 1;
    }



    epoll


}