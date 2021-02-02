#include "game.h"
#include "stdio.h"
#include "string.h"
#include "protocol.h"

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

    if (server->game->state != STATE_WAITING) {
        return;
    }

    uint8_t player_id = ++server->game->player_count;

    for (int i = 0; i < PLAYER_COUNT; ++i) {
        if (server->game->players[i].id == 0) {
            server->game->players[i].id = player_id;
            server->game->players[i].client = client;

            // (petla)
            for (int j=0; j < POSITION_COUNT; ++j){
                server->game->players[i].positions[j].position = login->positions[j];
            }

            //server->game->players[i].positions[0].position = login->positions[0];

            server->game->players[i].name = clone_string(login->username);

            break;
        }
    }

    // send_to_client(client, buffer3);

    client->is_player = 1;
    client->player_id = player_id;

    pkt_login_ack_t ack_login;
    ack_login.player_id = player_id;

    pkt_buffer_t *buffer_login_ack = create_buffer(sizeof(pkt_header_t) + sizeof(pkt_login_ack_t));
    encode_header(PKT_LOGIN_ACK_ID, login_ack_length(ack_login), buffer_login_ack);
    encode_login_ack(ack_login, buffer_login_ack);

    send_to_client(client, buffer_login_ack);

    if (server->game->player_count == PLAYER_COUNT) {
        server->game->state = STATE_GAMEPLAY;

        pkt_game_start_t start;
        start.game_id = 1;//was 0

        for (int i = 0; i < PLAYER_COUNT; ++i) {
            start.player_names[i] = server->game->players[i].name;
        }

        pkt_turn_start_t start_turn;
        start_turn.player_id = 1; // TODO: wybrac kto startuje
        start_turn.turn = 1;

        uint32_t gs_len = game_start_length(start);
        pkt_buffer_t *buffer_game_start = create_buffer(sizeof(pkt_header_t) + gs_len);

        encode_header(PKT_GAME_START_ID, gs_len, buffer_game_start);
        encode_game_start(start, buffer_game_start);

        broadcast_to_players(server->clients, buffer_game_start);

        uint32_t ts_len = turn_start_length(start_turn);
        pkt_buffer_t *buffer_turn_start = create_buffer(sizeof(pkt_header_t) + ts_len);
        encode_header(PKT_TURN_START_ID, ts_len, buffer_turn_start);
        encode_turn_start(start_turn, buffer_turn_start);

        broadcast_to_players(server->clients, buffer_turn_start);

    }

}

void game_receive_file_start(server_data_t *server, client_data_t *client, pkt_file_start_t *file)
{
    // todo: sprawdzic zwyciezce

    char *filename = calloc(sizeof(char), file->name.size + 1);
    memcpy(filename, file->name.data, file->name.size);

    // todo: zapis pliku do katalogu ( concat albo chdir() )
    FILE *fd = fopen(filename, "wb");
    free(filename);

    server->game->fd = fd;
    server->game->bytes_needed = file->size;
    server->game->state = STATE_AWAITING_FILE_DATA;

}

void game_receive_file_block(server_data_t *server, client_data_t *client, pkt_file_block_t *file)
{
    // TODO if
    int written = fwrite(file->block.data, 1, file->block.size, server->game->fd);

    server->game->bytes_needed -= written;

    if (server->game->bytes_needed <= 0) {
        fclose(server->game->fd);
    }
}

int is_game_over(server_data_t *server)
{
    int won_player = 0;
    int won_players = 0;

    for (int i = 0; i < PLAYER_COUNT; ++i) {
        player_data_t *player = &server->game->players[i];
        int alive_positions = 0;

        for (int j = 0; j < POSITION_COUNT; ++j) {
            position_data_t *position = &player->positions[j];

            if (position->dead == 0) {
                alive_positions++;
            }
        }

        if (alive_positions > 0) {
            won_players++;
            won_player = player->id;
        }
    }

    if (won_players == 1) {
        return won_player;
    }

    return 0;
}

void game_receive_turn_move(server_data_t *server, client_data_t *client, pkt_turn_move_t *move)
{

    player_data_t *playerData;

    for(int j=0; j<PLAYER_COUNT; ++j){
        if (server->game->players[j].id == move->picked_player_id){
            playerData = &server->game->players[j];
            break;
        }
    }

    // TODO: jesli nie znaleziono; wyrzuc

    pkt_position_t newPosition;
    newPosition = move->position;
    int i = 0;
    int shot = 0;
    for(i = 0; i<POSITION_COUNT; ++i){
        pkt_position_t currentPosition = playerData->positions[i].position;
        if (currentPosition.x == newPosition.x && currentPosition.y == newPosition.y) {
            if (playerData->positions[i].dead == 0) {
                shot = 1;
            }
            break;
        }
    }

    int whos_next = 0;

    if (shot) {
        playerData->positions[i].dead = 1;
        whos_next = client->player_id;
    } else {
        whos_next = move->picked_player_id;
    }

    int won_player = is_game_over(server);

    if (won_player != 0) {
        //koniec gry bez konca tury
        pkt_game_end_t game_end ;
        game_end.game_id = 1;
        game_end.winner_player_id = won_player;

        pkt_buffer_t *buffer_game_end = create_buffer(sizeof(pkt_header_t) + sizeof(pkt_game_end_t));
        encode_header(PKT_GAME_END_ID, game_end_length(game_end), buffer_game_end);
        encode_game_end(game_end, buffer_game_end);

        broadcast_to_players(server->clients, buffer_game_end);

        server->game->state = STATE_AWAITING_FILE_INFO;

    } else {
        // koniec tury

        pkt_turn_end_t end_turn;
        end_turn.position = move->position;
        end_turn.turn = move->turn;
        end_turn.picked_player_id = move->picked_player_id;
        end_turn.player_id = client->player_id;
        end_turn.success = shot;

        pkt_buffer_t *buffer_turn_end = create_buffer(sizeof(pkt_header_t) + sizeof(pkt_turn_end_t));
        encode_header(PKT_TURN_END_ID, turn_end_length(end_turn), buffer_turn_end);
        encode_turn_end(end_turn, buffer_turn_end);

        broadcast_to_players(server->clients, buffer_turn_end);

        //nowa tura
        pkt_turn_start_t start_turn2;
        start_turn2.player_id = whos_next;
        start_turn2.turn = move->turn + 1;

        pkt_buffer_t *buffer_turn_start2 = create_buffer(sizeof(pkt_header_t) + sizeof(pkt_turn_start_t));
        encode_header(PKT_TURN_START_ID, turn_start_length(start_turn2), buffer_turn_start2);
        encode_turn_start(start_turn2, buffer_turn_start2);

        broadcast_to_players(server->clients, buffer_turn_start2);
    }

}
