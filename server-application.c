#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/epoll.h>

#define USED_PORT 2137
#define LISTEN_BACKLOG 10
#define MAX_EPOLL_EVENTS 32

int createSocket();
int disableSocketBlocking();

int main() {

    int baseSocket, isBlocking, listener;

    int selector, alterSelectorInterest;

    struct epoll_event event;
    struct epoll_event *events;

    /* SOCKET SET UP */

    baseSocket = createSocket(USED_PORT);
    if (baseSocket == -1){
        printf("COULD NOT BIND.. EXITING THE PROGRAM");
        exit(EXIT_FAILURE);
    }

    isBlocking = disableSocketBlocking(baseSocket);
    if (isBlocking != 1){
        printf("COULD NOT BLOCK SOCKET.. EXITING THE PROGRAM");
        exit(EXIT_FAILURE);
    }

    listener = listen(baseSocket, LISTEN_BACKLOG);
    if (listener == -1){
        printf("COULD NOT LISTEN.. EXITING THE PROGRAM");
        exit(EXIT_FAILURE);
    }

    /* EPOLL */

    selector = epoll_create1(0);
    if (selector == -1){
        printf("COULD NOT CREATE EPOLL.. EXITING THE PROGRAM");
        exit(EXIT_FAILURE);
    }

    event.data.fd = baseSocket;
    event.events = EPOLLIN | EPOLLET;

    alterSelectorInterest = epoll_ctl(selector, EPOLL_CTL_ADD, baseSocket, &event);

    events = calloc(MAX_EPOLL_EVENTS, sizeof(event));

    //infinite loop with epoll wait here



    close(selector);

    close(baseSocket);

    return 0;
}

int createSocket(int port){

    int baseSocket, bindSocket;
    struct sockaddr_in endpoint;

    baseSocket = socket(PF_INET, SOCK_STREAM, 0);
    if (baseSocket == -1){
        printf("SOCKET() ERROR");
    }

    endpoint.sin_family = AF_INET;
    endpoint.sin_port = htons(port);
    endpoint.sin_addr.s_addr = INADDR_ANY;

    memset(&(endpoint.sin_zero), 0, 8);

    bindSocket = bind(baseSocket, (struct sockaddr *) &endpoint, sizeof(struct sockaddr));
    if (bindSocket < 0){
        printf("BIND() ERROR");
        return -1;
    }

    return baseSocket;

}


int disableSocketBlocking(int baseSocket){

    int flags, setSocket;

    flags = fcntl(baseSocket, F_GETFL, 0);
    if (flags == -1) {
        return 0;
    }

    setSocket = fcntl(baseSocket, F_SETFL, flags| O_NONBLOCK);
    if (setSocket == -1) {
        return 0;
    }

    return 1;
}
