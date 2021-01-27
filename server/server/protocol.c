#include "protocol.h"

#include "stdlib.h"
#include "string.h"
#include "assert.h"
#include <arpa/inet.h>

uint8_t decode_u8(pkt_buffer_t *buffer)
{
    assert(buffer_available_data(buffer) >= 1);

    uint8_t number = *buffer->rptr;
    buffer->rptr = buffer->rptr + 1;

    return number;
}

void encode_u8(uint8_t number, pkt_buffer_t *buffer)
{
    assert(buffer_remaining_space(buffer) >= 1);

    *buffer->wptr = number;
    buffer->wptr = buffer->wptr + 1;
}

uint32_t decode_u32(pkt_buffer_t *buffer)
{
    assert(buffer_available_data(buffer) >= 4);

    uint32_t number = *(uint32_t*) buffer->rptr;
    buffer->rptr = buffer->rptr + 4;

    return ntohl(number);
}

void encode_u32(uint32_t number, pkt_buffer_t *buffer)
{
    assert(buffer_remaining_space(buffer) >= 4);

    number = htonl(number);

    *((uint32_t*) buffer->wptr) = number;
    buffer->wptr = buffer->wptr + 4;
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

    assert(buffer_available_data(buffer) >= size);
    pkt_string_t string = create_string((const char*) buffer->rptr, size);
    buffer->rptr = buffer->rptr + size;

    return string;
}

void encode_string(pkt_string_t string, pkt_buffer_t *buffer)
{
    encode_u32(string.size, buffer);
    write_to_buffer(buffer, string.data, string.size);
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

    for (int i = 0; i < POSITION_COUNT; ++i) {
        login->positions[i] = decode_position(buffer);
    }

    return login;
}

void free_login(pkt_login_t *login)
{
    free_string(login->username);
    free(login);
}

pkt_turn_move_t *decode_turn_move(pkt_buffer_t *buffer)
{
    pkt_turn_move_t *move = malloc(sizeof(pkt_turn_move_t));

    move->turn = decode_u32(buffer);
    move->picked_player_id = decode_u8(buffer);
    move->position = decode_position(buffer);

    return move;
}

void free_turn_move(pkt_turn_move_t *turn)
{
    free(turn);
}

pkt_file_start_t *decode_file_start(pkt_buffer_t *buffer)
{
    pkt_file_start_t *file = malloc(sizeof(pkt_file_start_t));

    file->name = decode_string(buffer);
    file->size = decode_u32(buffer);

    return file;
}

void free_file_start(pkt_file_start_t *file)
{
    free_string(file->name);
    free(file);
}

pkt_file_block_t *decode_file_block(pkt_buffer_t *buffer)
{
    pkt_file_block_t *file = malloc(sizeof(pkt_file_block_t));

    file->block = decode_string(buffer);

    return file;
}

void free_file_block(pkt_file_block_t *file)
{
    free_string(file->block);
    free(file);
}

void encode_login_ack(pkt_login_ack_t login, pkt_buffer_t *buffer)
{
    encode_u8(login.player_id, buffer);
}

void encode_turn_start(pkt_turn_start_t turn, pkt_buffer_t *buffer)
{
    encode_u32(turn.turn, buffer);
    encode_u8(turn.player_id, buffer);
}

void encode_turn_end(pkt_turn_end_t turn, pkt_buffer_t *buffer)
{
    encode_u32(turn.turn, buffer);
    encode_u8(turn.player_id, buffer);
    encode_u8(turn.picked_player_id, buffer);
    encode_position(turn.position, buffer);
    encode_u8(turn.success, buffer);
}

void encode_game_start(pkt_game_start_t game, pkt_buffer_t *buffer)
{
    encode_u32(game.game_id, buffer);
}

void encode_game_end(pkt_game_end_t game, pkt_buffer_t *buffer)
{
    encode_u32(game.game_id, buffer);
    encode_u8(game.winner_player_id, buffer);
}
