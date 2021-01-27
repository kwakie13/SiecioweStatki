#ifndef SERVER_PROTOCOL_H
#define SERVER_PROTOCOL_H

#include "buffer.h"
#include "stdint.h"

#define MAX_PACKET_SIZE 2100000
#define POSITION_COUNT 5
#define PLAYER_COUNT 4
#define SERVER_PORT 3124

typedef struct pkt_header {
    uint32_t type;
    uint32_t size;
} pkt_header_t;

typedef struct pkt_string {
    uint32_t size;
    char *data;
} pkt_string_t;

typedef struct pkt_position {
    uint8_t x;
    uint8_t y;
} pkt_position_t;

// logowanie

// klient -> serwer
#define PKT_LOGIN_ID 1
typedef struct pkt_login {
    pkt_string_t username;
    pkt_position_t positions[POSITION_COUNT];
} pkt_login_t;

// server -> klient
#define PKT_LOGIN_ACK_ID 2
typedef struct pkt_login_ack {
    uint8_t player_id;
} pkt_login_ack_t;

// tury

// server -> klient
#define PKT_TURN_START_ID 3
typedef struct pkt_turn_start {
    uint32_t turn;
    uint8_t player_id;
} pkt_turn_start_t;

// klient -> serwer
#define PKT_TURN_MOVE_ID 4
typedef struct pkt_turn_move {
    uint32_t turn;
    uint8_t picked_player_id;
    pkt_position_t position;
} pkt_turn_move_t;

// server -> klient
#define PKT_TURN_END_ID 5
typedef struct pkt_turn_end {
    uint32_t turn;
    uint8_t player_id;
    uint8_t picked_player_id;
    pkt_position_t position;
    uint8_t success;
} pkt_turn_end_t;

// gra

// server -> klient
#define PKT_GAME_START_ID 6
typedef struct pkt_game_start {
    uint32_t game_id;
} pkt_game_start_t;

// server -> klient
#define PKT_GAME_END_ID 7
typedef struct pkt_game_end {
    uint32_t game_id;
    uint8_t winner_player_id;
} pkt_game_end_t;

// transfer plików

// klient -> serwer
#define PKT_FILE_START_ID 8
typedef struct pkt_file_start {
    pkt_string_t name;
    uint32_t size;
} pkt_file_start_t;

// klient -> serwer
#define PKT_FILE_BLOCK_ID 9
typedef struct pkt_file_block {
    pkt_string_t block;
} pkt_file_block_t;

uint8_t decode_u8(pkt_buffer_t *buffer);
void encode_u8(uint8_t number, pkt_buffer_t *buffer);

uint32_t decode_u32(pkt_buffer_t *buffer);
void encode_u32(uint32_t number, pkt_buffer_t *buffer);

pkt_string_t create_string(const char *data, uint32_t size);
pkt_string_t decode_string(pkt_buffer_t *buffer);
void encode_string(pkt_string_t string, pkt_buffer_t *buffer);
void free_string(pkt_string_t string);

pkt_header_t decode_header(pkt_buffer_t *buffer);
void encode_header(uint32_t type, uint32_t size, pkt_buffer_t *buffer);

pkt_position_t decode_position(pkt_buffer_t *buffer);
void encode_position(pkt_position_t position, pkt_buffer_t *buffer);

pkt_login_t *decode_login(pkt_buffer_t *buffer);
void free_login(pkt_login_t *login);

pkt_turn_move_t *decode_turn_move(pkt_buffer_t *buffer);
void free_turn_move(pkt_turn_move_t *turn);

pkt_file_start_t *decode_file_start(pkt_buffer_t *buffer);
void free_file_start(pkt_file_start_t *file);

pkt_file_block_t *decode_file_block(pkt_buffer_t *buffer);
void free_file_block(pkt_file_block_t *file);

void encode_login_ack(pkt_login_ack_t login, pkt_buffer_t *buffer);
void encode_turn_start(pkt_turn_start_t turn, pkt_buffer_t *buffer);
void encode_turn_end(pkt_turn_end_t turn, pkt_buffer_t *buffer);
void encode_game_start(pkt_game_start_t game, pkt_buffer_t *buffer);
void encode_game_end(pkt_game_end_t game, pkt_buffer_t *buffer);

#endif //SERVER_PROTOCOL_H
