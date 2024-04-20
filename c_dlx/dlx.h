#ifndef DLX_H
#define DLX_H

#include <stdint.h>
#include "ecp.h"

typedef uint32_t node_t;

// Dancing Links
typedef struct {
    node_t *L, *R, *U, *D, *S, *C, *N, *I;
    uint32_t size;
} dlx_t;

void dlx_init(dlx_t* dlx, ecp_t* ecp);
void dlx_destroy(dlx_t* dlx);
void dlx_cover(dlx_t* dlx, node_t c);
void dlx_uncover(dlx_t* dlx, node_t c);

#endif