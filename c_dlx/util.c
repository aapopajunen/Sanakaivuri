#include "util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void ivec_init(ivec_t* v) {
    v->data = calloc(8, sizeof(uint32_t));
    v->size = 0;
    v->capacity = 8;
}

void ivec_destroy(ivec_t* v) {
    free(v->data);
}

void ivec_push(ivec_t* v, uint32_t* e, uint32_t n) {
    while (v->size + n > v->capacity) {
      v->capacity <<= 1;
      v->data = realloc(v->data, v->capacity * sizeof(uint32_t));
    }
    memcpy(&v->data[v->size], e, n * sizeof(uint32_t));
    v->size += n;
}

void results_init(results_t* results) {
    ivec_init(&results->data);
    ivec_init(&results->idxs);
}

void results_destroy(results_t* results) {
    ivec_destroy(&results->data);
    ivec_destroy(&results->idxs);
}

void results_push(results_t* results, uint32_t* res, uint32_t size) {
    ivec_push(&results->data, res, size);
    uint32_t prev = results->idxs.size == 0 ? 0 : results->idxs.data[results->idxs.size - 1];
    uint32_t next = prev + size;
    ivec_push(&results->idxs, &next, 1);
}

void results_print(results_t* results) {
    for (uint32_t i = 0; i < results->idxs.size; ++i) {
        uint32_t start = i == 0 ? 0 : results->idxs.data[i - 1];
        uint32_t end = results->idxs.data[i];
        for (uint32_t j = start; j < end; ++j) {
            printf("%d ", results->data.data[j]);
        }
        printf("\n");
    }
}

void test_interface() {
  printf("hello wordl!\n");
}