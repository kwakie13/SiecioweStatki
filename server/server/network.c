#include "network.h"

client_data_t *create_client()
{
    client_data_t *client = calloc(sizeof(client_data_t), 1);

    client->receive_buffer = create_buffer(MAX_PACKET_SIZE);
    client->send_buffers = create_list();

    return client;
}

void free_client(client_data_t *client)
{
    void *buffer = 0;
    while ((buffer = pop_from_list(client->send_buffers))) {
        free_buffer(buffer);
    }

    free_list(client->send_buffers);
    free_buffer(client->receive_buffer);
    free(client);
}

void send_to_client(client_data_t *client, pkt_buffer_t *buffer)
{
    insert_to_list(client->send_buffers, buffer);
}

void broadcast_to_players(list_t *clients, pkt_buffer_t *buffer)
{
    list_item_t *item = clients->items;
    while (item) {
        client_data_t *client = item->data;
        if (client->is_player) {
            pkt_buffer_t *cloned = buffer_clone(buffer);
            send_to_client(client, cloned);
        }

        item = item->next;
    }

    free_buffer(buffer);
}

void broadcast_to_clients(list_t *clients, pkt_buffer_t *buffer)
{
    list_item_t *item = clients->items;
    while (item) {
        client_data_t *client = item->data;
        pkt_buffer_t *cloned = buffer_clone(buffer);
        send_to_client(client, cloned);

        item = item->next;
    }

    free_buffer(buffer);
}
