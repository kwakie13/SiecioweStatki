#include "list.h"

list_t *create_list()
{
    return calloc(sizeof(list_t), 1);
}

list_item_t *create_list_item(void *data)
{
    list_item_t *item = calloc(sizeof(list_item_t), 1);
    item->data = data;
    return item;
}

void free_list(list_t *list)
{
    free(list);
}

void free_list_item(list_item_t *item)
{
    free(item);
}

void insert_to_list(list_t *list, void *data)
{
    list_item_t *new = create_list_item(data);
    list_item_t **current = &list->items;

    while (*current) {
        current = &((*current)->next);
    }

    *current = new;
}


void remove_from_list(list_t *list, void *item)
{
    list_item_t **ptr = &list->items;

    while (*ptr) {
        list_item_t *ptr_current = *ptr;

        if (ptr_current->data == item) {
            *ptr = ptr_current->next;
            free_list_item(ptr_current);
            break;
        }

        ptr = &ptr_current->next;
    }
}

void *pop_from_list(list_t *list)
{
    list_item_t *first = list->items;
    void *data = 0;

    if (first) {
        data = first->data;
        list->items = first->next;
        free_list_item(first);
    }

    return data;
}
