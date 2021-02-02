#include "protocol.h"
#include "buffer.h"
#include "list.h"
#include "network.h"
#include "server.h"
#include "game.h"

#include <stdio.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>

static int make_socket_nonblocking(int socket) {
    int flags = fcntl(socket, F_GETFL, 0);

    if (flags == -1)
        return -1;

    return fcntl(socket, F_SETFL, flags | O_NONBLOCK);
}

static int create_listen_socket(uint16_t port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        return -1;
    }

    struct sockaddr_in addr;
    socklen_t addrlen = sizeof(struct sockaddr_in);
    memset(&addr, 0, sizeof(struct sockaddr_in));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sock, (struct sockaddr*) &addr, addrlen) == -1) {
        return -1;
    }

    if (listen(sock, SOMAXCONN) == -1) {
        return -1;
    }

    if (make_socket_nonblocking(sock) == -1) {
        return -1;
    }

    return sock;
}

static int add_fd_to_epoll(int epfd, int fd, uint32_t events) {
    struct epoll_event event;
    event.events = events;
    event.data.fd = fd;

    return epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event);
}

static int add_client_to_epoll(int epfd, client_data_t *client, uint32_t events) {
    struct epoll_event event;
    event.events = events;
    event.data.ptr = client;

    return epoll_ctl(epfd, EPOLL_CTL_ADD, client->fd, &event);
}

static void decode_and_dispatch(server_data_t *server, client_data_t *client) {
    void *packet;

    switch (client->received_header.type) {
        case PKT_LOGIN_ID:
            packet = decode_login(client->receive_buffer);
            game_receive_login(server, client, packet);
            free_login(packet);
            break;

        case PKT_TURN_MOVE_ID:
            packet = decode_turn_move(client->receive_buffer);
            game_receive_turn_move(server, client, packet);
            free_turn_move(packet);
            break;

        case PKT_FILE_START_ID:
            packet = decode_file_start(client->receive_buffer);
            game_receive_file_start(server, client, packet);
            free_file_start(packet);
            break;

        case PKT_FILE_BLOCK_ID:
            packet = decode_file_block(client->receive_buffer);
            game_receive_file_block(server, client, packet);
            free_file_block(packet);
            break;

        default:
            // TODO: nieznany pakiet
            return;
    }
}

static int read_until(int fd, pkt_buffer_t *buffer, int size) {
    int available = 0;
    while ((available = buffer_available_data(buffer)) < size) {
        int remaining = size - available;

        int received = read(fd, buffer->wptr, remaining);
        if (received == -1) {
            if (errno == EAGAIN) {
                return 1;
            }
            return 2;
        }
        if (received == 0) {
            return 2;
        }

        buffer->wptr = buffer->wptr + received;
    }

    return 0;
}

static void handle_client_event(server_data_t *server, client_data_t *client, uint32_t events) {
    if (events & EPOLLIN) {
        while (1) {
            if (client->received_header.type == 0) {
                int result = read_until(client->fd, client->receive_buffer, 8);
                if (result == 0) {
                    client->received_header = decode_header(client->receive_buffer);
                } else if (result == 1) {
                    break;
                } else {
                    // TODO: błąd lub klient się rozłączył
                    break;
                }
            } else {
                int result = read_until(client->fd, client->receive_buffer, client->received_header.size);
                if (result == 0) {
                    decode_and_dispatch(server, client);

                    client->received_header.type = 0;
                    buffer_clear(client->receive_buffer);
                } else if (result == 1) {
                    printf("result=1\n");
                    break;
                } else {
                    printf("result=2\n");
                    // TODO: błąd lub klient się rozłączył
                    break;
                }
            }
        }
    } else if (events & EPOLLOUT) {
        // wysyłka jest po przetworzeniu eventów
    } else if (events & EPOLLERR) {
        // TODO: błąd
    }
}

static void handle_listen_event(server_data_t *server, int fd, uint32_t events) {
    if (events & EPOLLIN) {
        client_data_t *client = create_client();

        socklen_t socklen = sizeof(struct sockaddr_storage);
        int clientfd = accept(server->listen_socket, (struct sockaddr *) &client->address, &socklen);
        if (clientfd == -1) {
            free_client(client);
            // TODO: error
            return;
        }

        if (make_socket_nonblocking(clientfd) == -1) {
            free_client(client);
            // TODO: error
            return;
        }

        client->fd = clientfd;
        insert_to_list(server->clients, client);
        add_client_to_epoll(server->epollfd, client, EPOLLIN | EPOLLOUT | EPOLLET);
    }
}

static int send_buffered_data(client_data_t *client) {
    list_item_t *item = client->send_buffers->items;
    while (item) {
        pkt_buffer_t *buffer = item->data;

        int size;
        while ((size = buffer_available_data(buffer)) > 0) {
            int written = write(client->fd, buffer->rptr, size);

            if (written == -1) {
                return errno == EAGAIN ? 0 : -1;
            }

            buffer->rptr = buffer->rptr + written;
        }

        item = item->next;
        free_buffer(buffer);
        remove_from_list(client->send_buffers, buffer);
    }

    return 0;
}

int main(int argc, char *argv[]) {
    int listen_socket = create_listen_socket(SERVER_PORT);
    if (listen_socket == -1) {
        perror("Could not create listen socket\n");
        return 1;
    }

    int epfd = epoll_create1(0);
    if (epfd == -1) {
        perror("Could not epoll fd\n");
        return 1;
    }

    if (add_fd_to_epoll(epfd, listen_socket, EPOLLIN | EPOLLET) == -1) {
        perror("Could not add listen socket to epoll\n");
        return 1;
    }

    server_data_t server;
    server.listen_socket = listen_socket;
    server.clients = create_list();
    server.epollfd = epfd;
    server.game = create_game();

    while (1) {
        struct epoll_event events[10];
        int nevents = epoll_wait(epfd, events, 10, -1);
        if (nevents == -1) {
            break;
        }

        for (int i = 0; i < nevents; i++) {
            if (events[i].data.fd == listen_socket) {
                handle_listen_event(&server, listen_socket, events[i].events);
            } else {
                handle_client_event(&server, events[i].data.ptr, events[i].events);
            }
        }

        list_item_t *item = server.clients->items;
        while (item) {
            send_buffered_data(item->data);
            item = item->next;
        }
    }

    // TODO: free
}
