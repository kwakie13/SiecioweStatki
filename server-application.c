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
#include <errno.h>

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
        printf("COULD NOT BIND.. EXITING THE PROGRAM\n");
        exit(EXIT_FAILURE);
    }
    printf("CHECK SOCKET CREATED\n");

    isBlocking = disableSocketBlocking(baseSocket);
    if (isBlocking != 1){
        printf("COULD NOT BLOCK SOCKET.. EXITING THE PROGRAM\n");
        exit(EXIT_FAILURE);
    }
    printf("CHECK UNBLOCKING SOCKET\n");

    listener = listen(baseSocket, LISTEN_BACKLOG);
    if (listener == -1){
        printf("COULD NOT LISTEN.. EXITING THE PROGRAM\n");
        exit(EXIT_FAILURE);
    }
    printf("CHECK SOCKET LISTEN\n");

    /* EPOLL */

    selector = epoll_create1(0);
    if (selector == -1){
        printf("COULD NOT CREATE EPOLL.. EXITING THE PROGRAM\n");
        exit(EXIT_FAILURE);
    }

    event.data.fd = baseSocket;
    event.events = EPOLLIN | EPOLLET;

    alterSelectorInterest = epoll_ctl(selector, EPOLL_CTL_ADD, baseSocket, &event);

    events = calloc(MAX_EPOLL_EVENTS, sizeof(event));

    //infinite loop with epoll wait here
    int loopEnded = 0;
    while(!loopEnded){
        printf("CHECK 2\n");


        int selectorWait;

        selectorWait = epoll_wait(selector, events, MAX_EPOLL_EVENTS, -1);
        if (selectorWait == -1) {
            printf("COULD NOT WAIT FOR EVENTS.. CLOSING THE EVENT\n");
            continue;
        }

        int eventIter;
        for( eventIter=0 ; eventIter < selectorWait; eventIter++){
            printf("CHECK 3\n");

            if (events[eventIter].data.fd == baseSocket){

                while(1){
                    printf("CHECK 4\n");


                    struct sockaddr_storage address_in;
                    socklen_t address_in_len = sizeof(struct sockaddr_storage);
                    int socketAccept, socketUnBlocked, alterInterestLists;

                    socketAccept = accept(baseSocket, (struct sockaddr*) &address_in, &address_in_len);

                    if (socketAccept == -1) {
                        perror("NO CONNECTIONS TO PROCESS OR ACCEPT ERROR\n");
                        break;
                    }

                    socketUnBlocked = disableSocketBlocking(socketAccept);
                    if (!socketUnBlocked){
                        printf("EVENT SOCKED COULD NOT BE UNBLOCKED..\n");
                        exit(EXIT_FAILURE);
                    }

                    event.data.fd = socketAccept;
                    event.events = EPOLLIN | EPOLLET;

                    alterInterestLists = epoll_ctl(selector, EPOLL_CTL_ADD, socketAccept,&event);
                    printf("socket accepted: %d\n", socketAccept);
                    if(alterInterestLists == -1){
                        printf("COULD NOT ALTER INTEREST LIST..\n");
                        exit(EXIT_FAILURE);
                    }





                }

            } else {

                int dataIsRead = 0;
                char bufferinio[2048];
                printf("CHECK 6\n");
                while (1) {
                    size_t read_count;
                    char buf[1024];
                    printf("CHECK 7 %d\n", events[eventIter].data.fd);

                    read_count = read(events[eventIter].data.fd, buf, sizeof(buf));
                    printf("ASDF : %zu\n", read_count);
                    if (read_count == -1) {

                        perror("CHECK 8\n");

                        if (errno != EAGAIN) {
                            dataIsRead = 1;
                        }

                        break;

                    }
                    else if (read_count == 0) {

                        printf("CHECK 9\n");

                        dataIsRead = 1;
                        strcat(bufferinio, buf);
                        break;
                    } else {

                        printf("CHECK 10\n");

                    }


                }
                if (dataIsRead) {
                    printf("DZIALA\n");
                    printf("\n%s\n", bufferinio);
                    close(events[eventIter].data.fd);

                }



            }


        }

    }

    free(events);

    close(selector);

    close(baseSocket);

    return 0;
}

int createSocket(int port){

    int baseSocket, bindSocket;
    struct sockaddr_in endpoint;

    baseSocket = socket(PF_INET, SOCK_STREAM, 0);
    if (baseSocket == -1){
        printf("SOCKET() ERROR\n");
    }
    printf("CHECK FUNCTION1 SOCKET()\n");


    endpoint.sin_family = AF_INET;
    endpoint.sin_port = htons(port);
    endpoint.sin_addr.s_addr = INADDR_ANY;

    memset(&(endpoint.sin_zero), 0, 8);

    bindSocket = bind(baseSocket, (struct sockaddr *) &endpoint, sizeof(struct sockaddr));
    if (bindSocket < 0){
        printf("BIND() ERROR\n");
        return -1;
    }
    printf("CHECK FUNCTION1 BIND()\n");

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
