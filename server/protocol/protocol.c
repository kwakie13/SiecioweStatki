#include "protocol.h"

#include "stdlib.h"
#include "string.h"
#include "assert.h"
#include <arpa/inet.h>

pkt_buffer_t *create_buffer(int capacity)
{
    pkt_buffer_t *buffer = malloc(sizeof(pkt_buffer_t));
    uint8_t *data = calloc(sizeof(uint8_t), capacity);

    buffer->capacity = capacity;
    buffer->data = data;
    buffer->pointer = data;

    return buffer;
}

void free_buffer(pkt_buffer_t *buffer)
{
    free(buffer->data);
    free(buffer);
}

uint8_t decode_u8(pkt_buffer_t *buffer)
{
    assert(buffer->data + buffer->capacity <= buffer->pointer + 1);

    uint8_t number = *buffer->pointer;
    buffer->pointer = buffer->pointer + 1;

    return number;
}

void encode_u8(uint8_t number, pkt_buffer_t *buffer)
{
    assert(buffer->data + buffer->capacity <= buffer->pointer + 1);

    *buffer->pointer = number;
    buffer->pointer = buffer->pointer + 1;
}

uint32_t decode_u32(pkt_buffer_t *buffer)
{
    assert(buffer->data + buffer->capacity <= buffer->pointer + 4);

    uint32_t number = *(uint32_t*) buffer->pointer;
    buffer->pointer = buffer->pointer + 4;

    return ntohl(number);
}

void encode_u32(uint32_t number, pkt_buffer_t *buffer)
{
    assert(buffer->data + buffer->capacity <= buffer->pointer + 4);

    number = htonl(number);

    *((uint32_t*) buffer->pointer) = number;
    buffer->pointer = buffer->pointer + 4;
}

pkt_string_t create_string(const char *data, uint32_t size)
{
    pkt_string_t str;

    str.size = size;
    str.data = malloc((size_t) size);
    memcpy(str.data, data, size);

    return str;
}

pkt_string_t decode_string(pkt_buffer_t *buffer)
{
    uint32_t size = decode_u32(buffer);

    assert(buffer->data + buffer->capacity <= buffer->pointer + size);
    pkt_string_t string = create_string((const char*) buffer->pointer, size);
    buffer->pointer = buffer->pointer + size;

    return string;
}

void encode_string(pkt_string_t string, pkt_buffer_t *buffer)
{
    assert(buffer->data + buffer->capacity <= buffer->pointer + string.size + 4);

    encode_u32(string.size, buffer);
    memcpy(buffer->pointer, string.data, string.size);
    buffer->pointer = buffer->pointer + string.size;
}

void free_string(pkt_string_t string)
{
    free(string.data);
}

pkt_header_t decode_header(pkt_buffer_t *buffer)
{
    pkt_header_t header;
    header.type = decode_u32(buffer);
    header.size = decode_u32(buffer);
    return header;
}

void encode_header(uint32_t type, uint32_t size, pkt_buffer_t *buffer)
{
    encode_u32(type, buffer);
    encode_u32(size, buffer);
}

pkt_position_t decode_position(pkt_buffer_t *buffer)
{
    pkt_position_t position;
    position.x = decode_u8(buffer);
    position.y = decode_u8(buffer);
    return position;
}

void encode_position(pkt_position_t position, pkt_buffer_t *buffer)
{
    encode_u8(position.x, buffer);
    encode_u8(position.y, buffer);
}

pkt_login_t *decode_login(pkt_buffer_t *buffer)
{
    pkt_login_t *login = malloc(sizeof(pkt_login_t));

    login->username = decode_string(buffer);

    for (int i = 0; i < INITIAL_POSITIONS; ++i) {
        login->positions[i] = decode_position(buffer);
    }

    return login;
}

void free_login(pkt_login_t *login)
{
    free_string(login->username);
    free(login);
}

pkt_turn_move_t decode_turn_move(pkt_buffer_t *buffer)
{
    pkt_turn_move_t move;
    move.turn = decode_u32(buffer);
    move.picked_player_id = decode_u8(buffer);
    move.position = decode_position(buffer);

    return move;
}

pkt_file_start_t *decode_file_start(pkt_buffer_t *buffer)
{
    pkt_file_start_t *login = malloc(sizeof(pkt_file_start_t));

    login->name = decode_string(buffer);
    login->size = decode_u32(buffer);

    return login;
}

void free_file_start(pkt_file_start_t *login)
{
    free_string(login->name);
    free(login);
}

pkt_file_block_t *decode_file_block(pkt_buffer_t *buffer)
{
    pkt_file_block_t *login = malloc(sizeof(pkt_file_block_t));

    login->block = decode_string(buffer);

    return login;
}

void free_file_block(pkt_file_block_t *login)
{
    free_string(login->block);
    free(login);
}

void encode_login_ack(pkt_login_ack_t login, pkt_buffer_t *buffer)
{
    encode_u8(login.player_id, buffer);
}

void encode_turn_start(pkt_turn_start_t login, pkt_buffer_t *buffer)
{
    encode_u32(login.turn, buffer);
    encode_u8(login.player_id, buffer);
}

void encode_turn_end(pkt_turn_end_t login, pkt_buffer_t *buffer)
{
    encode_u32(login.turn, buffer);
    encode_u8(login.player_id, buffer);
    encode_u8(login.picked_player_id, buffer);
    encode_position(login.position, buffer);
    encode_u8(login.success, buffer);
}

void encode_game_start(pkt_game_start_t login, pkt_buffer_t *buffer)
{
    encode_u32(login.game_id, buffer);
}

void encode_game_end(pkt_game_end_t login, pkt_buffer_t *buffer)
{
    encode_u32(login.game_id, buffer);
    encode_u8(login.winner_player_id, buffer);
}
