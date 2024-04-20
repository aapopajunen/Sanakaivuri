#ifndef DLX_UTIL_H
#define DLX_UTIL_H

#include <stdint.h>

typedef struct {
    uint32_t* data;
    size_t size;
    size_t capacity;
} ivec_t;

__declspec(dllexport) void ivec_init(ivec_t* v);
__declspec(dllexport) void ivec_destroy(ivec_t* v);
__declspec(dllexport) void ivec_push(ivec_t* v, uint32_t* e, uint32_t n);

typedef struct {
    ivec_t data;
    ivec_t idxs;
} results_t;

__declspec(dllexport) void results_init(results_t* results);
__declspec(dllexport) void results_destroy(results_t* results);
__declspec(dllexport) void results_push(results_t* results, uint32_t* res, uint32_t size);
__declspec(dllexport) void results_print(results_t* results);
__declspec(dllexport) void test_interface();

#endif