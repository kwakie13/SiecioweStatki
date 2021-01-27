#ifndef SERVER_LIST_H
#define SERVER_LIST_H

#include "stdlib.h"

typedef struct list_item {
    void *data;
    struct list_item *next;
} list_item_t;

typedef struct list {
    list_item_t *items;
} list_t;

list_t *create_list();
list_item_t *create_list_item(void *data);

void free_list(list_t *list);
void free_list_item(list_item_t *item);

void insert_to_list(list_t *list, void *data);
void remove_from_list(list_t *list, void *item);
void *pop_from_list(list_t *list);

#endif //SERVER_LIST_H
