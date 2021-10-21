#ifndef SERVER_GAME_H
#define SERVER_GAME_H

#include <bits/types/FILE.h>
#include "network.h"
#include "server.h"

#define STATE_WAITING 0
#define STATE_GAMEPLAY 1
#define STATE_AWAITING_FILE_INFO 2
#define STATE_AWAITING_FILE_DATA 3

typedef struct position_data_t {
    int dead;
    pkt_position_t position;
} position_data_t;

typedef struct player_data {
    uint8_t id;
    position_data_t positions[POSITION_COUNT];
    client_data_t *client;
    pkt_string_t name;
} player_data_t;

typedef struct game_data {
    player_data_t players[PLAYER_COUNT];
    int state;
    int player_count;

    FILE *fd;
    int bytes_needed;
} game_data_t;

game_data_t *create_game();
void free_game();

void game_receive_login(server_data_t *server, client_data_t *client, pkt_login_t *login);
void game_receive_file_start(server_data_t *server, client_data_t *client, pkt_file_start_t *file);
void game_receive_file_block(server_data_t *server, client_data_t *client, pkt_file_block_t *file);
void game_receive_turn_move(server_data_t *server, client_data_t *client, pkt_turn_move_t *move);

#endif //SERVER_GAME_H

