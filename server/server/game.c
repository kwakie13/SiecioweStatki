#include "game.h"
#include "stdio.h"

game_data_t *create_game()
{
    game_data_t *game = calloc(sizeof(game_data_t), 1);

    return game;
}

void free_game(game_data_t *game)
{
    free(game);
}

void game_receive_login(server_data_t *server, client_data_t *client, pkt_login_t *login)
{
    // TODO
}

void game_receive_file_start(server_data_t *server, client_data_t *client, pkt_file_start_t *file)
{
    printf("file_start: %d\n", file->size);
    // TODO
}

void game_receive_file_block(server_data_t *server, client_data_t *client, pkt_file_block_t *file)
{
    // TODO
}

void game_receive_turn_move(server_data_t *server, client_data_t *client, pkt_turn_move_t *move)
{
    // TODO
}
