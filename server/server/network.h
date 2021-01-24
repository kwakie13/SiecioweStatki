#ifndef SERVER_NETWORK_H
#define SERVER_NETWORK_H

#include "protocol.h"
#include "buffer.h"
#include "list.h"
#include <sys/socket.h>

typedef struct client_data {
    int fd;
    struct sockaddr_storage address;

    pkt_header_t received_header;
    pkt_buffer_t *receive_buffer;
    list_t *send_buffers;

    char is_player;
    uint8_t player_id;
} client_data_t;

client_data_t *create_client();
void free_client(client_data_t *client);

void send_to_client(client_data_t *client, pkt_buffer_t *buffer);
void broadcast_to_players(list_t *clients, pkt_buffer_t *buffer);
void broadcast_to_clients(list_t *clients, pkt_buffer_t *buffer);

#endif //SERVER_NETWORK_H
