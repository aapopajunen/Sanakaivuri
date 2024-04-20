#ifndef ECP_H
#define ECP_H

#include <stdint.h>
#include <stdbool.h>
#include "util.h"

// Exact Cover Problem
typedef struct {
  ivec_t U;
  ivec_t S;
  ivec_t idxs; // end indices
} ecp_t;

__declspec(dllexport) void ecp_init(ecp_t* ecp);
__declspec(dllexport) void ecp_destroy(ecp_t* ecp);
__declspec(dllexport) void ecp_push_universe(ecp_t* ecp, uint32_t* u, uint32_t n);
__declspec(dllexport) void ecp_push_subset(ecp_t* ecp, uint32_t* s, uint32_t n);
__declspec(dllexport) bool ecp_s_contains(ecp_t* ecp, uint32_t s_idx, uint32_t u_idx);
__declspec(dllexport) void ecp_solve(ecp_t* ecp, results_t* results);

#endif