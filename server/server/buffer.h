#ifndef SERVER_BUFFER_H
#define SERVER_BUFFER_H

#include "stdint.h"

typedef struct pkt_buffer {
    int capacity;
    uint8_t *wptr;
    uint8_t *rptr;
    uint8_t *data;
} pkt_buffer_t;

pkt_buffer_t *create_buffer(int capacity);
void free_buffer(pkt_buffer_t *buffer);

void write_to_buffer(pkt_buffer_t *buffer, void *data, int size);
int buffer_available_data(pkt_buffer_t *buffer);
int buffer_remaining_space(pkt_buffer_t *buffer);
int buffer_size(pkt_buffer_t *buffer);
void buffer_clear(pkt_buffer_t *buffer);
pkt_buffer_t *buffer_clone(pkt_buffer_t *buffer);

#endif //SERVER_BUFFER_H
