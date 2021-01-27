#include "buffer.h"

#include "stdlib.h"
#include "string.h"
#include "assert.h"

pkt_buffer_t *create_buffer(int capacity)
{
    pkt_buffer_t *buffer = malloc(sizeof(pkt_buffer_t));
    uint8_t *data = calloc(sizeof(uint8_t), capacity);

    buffer->capacity = capacity;
    buffer->data = data;
    buffer->rptr = data;
    buffer->wptr = data;

    return buffer;
}

void free_buffer(pkt_buffer_t *buffer)
{
    free(buffer->data);
    free(buffer);
}

void write_to_buffer(pkt_buffer_t *buffer, void *data, int size)
{
    assert(buffer_remaining_space(buffer) >= size);

    memcpy(buffer->wptr, data, size);

    buffer->wptr = buffer->wptr + size;
}

int buffer_available_data(pkt_buffer_t *buffer)
{
    return (int) (buffer->wptr - buffer->rptr);
}

int buffer_remaining_space(pkt_buffer_t *buffer)
{
    return (int) (buffer->data - buffer->wptr + buffer->capacity);
}

void buffer_clear(pkt_buffer_t *buffer)
{
    buffer->wptr = buffer->data;
    buffer->rptr = buffer->data;
}

pkt_buffer_t *buffer_clone(pkt_buffer_t *buffer)
{
    int roffset = (int) (buffer->rptr - buffer->data);
    int woffset = (int) (buffer->wptr - buffer->data);

    pkt_buffer_t *cloned = create_buffer(buffer->capacity);
    memcpy(cloned->data, buffer->data, woffset);
    cloned->wptr = cloned->wptr + woffset;
    cloned->rptr = cloned->rptr + roffset;

    return cloned;
}