#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>

struct sockaddr_in endpoint;
char myHostName[1024];
char buf[1024];

int main() {

    socklen_t sin_size;

    int counter, received;

    struct sockaddr_in incoming;

    struct hostent *heLocalHost;

    char sign;
    int sdServerSocket, bindSock, sdConnection;

    sin_size = sizeof(struct sockaddr_in);

    sdServerSocket = socket(PF_INET, SOCK_STREAM, 0);

    gethostname(myHostName, 1023);
    heLocalHost = gethostbyname(myHostName);

    endpoint.sin_family = AF_INET;
    endpoint.sin_port = htons(2137);
    endpoint.sin_addr.s_addr = INADDR_ANY;

    memset(&(endpoint.sin_zero), 0, 8);


    bindSock = bind(sdServerSocket, (struct sockaddr *) &endpoint, sizeof(struct sockaddr));

    if (bindSock < 0) {
        printf("bind nie powiodl sie");
        return 1;
    }

    listen(sdServerSocket, 10);

    sin_size = sizeof(struct sockaddr_in);


    while ((sdConnection = accept(sdServerSocket, (struct sockaddr *) &incoming, &sin_size))) {
        if (sdConnection == -1) {
            continue;
        }
        printf("POLACZENIE Z %s:%d\n", inet_ntoa(incoming.sin_addr), ntohs(incoming.sin_port));

        counter = 1024;

        char *pointer = buf;
        int capacity = 12;

        while (capacity > 0) {
            received = recv(sdConnection, pointer, capacity, 0);

            if (received < 0) {
                perror("recv sie nie powiodl\n");
                break;
            }
            printf("odebrano: %s\n", buf);

            capacity -= received;
            pointer += received;
            /*
            if (send(sdConnection, &buf, 1024, 0) < 0) { printf("send sie nie powiodl\n"); }

            close(sdConnection);
             */
        }
        close(sdConnection);
    }

    printf("\n%s\n", buf);


    return 0;

}
