#ifndef SERVER_SERVER_H
#define SERVER_SERVER_H

struct game_data;
struct list;

typedef struct server_data {
    int epollfd;
    int listen_socket;
    struct list *clients;
    struct game_data *game;
} server_data_t;

#endif //SERVER_SERVER_H

