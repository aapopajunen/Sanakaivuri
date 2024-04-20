#include "ecp.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "dlx.h"

bool ecp_s_contains(ecp_t* ecp, uint32_t s_idx, uint32_t u_idx) {
    uint32_t start = s_idx == 0 ? 0 : ecp->idxs.data[s_idx - 1];
    uint32_t end = ecp->idxs.data[s_idx];
    for (uint32_t i = start; i < end; ++i) {
      if (ecp->S.data[i] == ecp->U.data[u_idx]) 
        return true;
    }
    
    return false;
}

void ecp_init(ecp_t* ecp) {
  ivec_init(&ecp->U);
  ivec_init(&ecp->S);
  ivec_init(&ecp->idxs);
}

void ecp_destroy(ecp_t* ecp) {
  ivec_destroy(&ecp->U);
  ivec_destroy(&ecp->S);
  ivec_destroy(&ecp->idxs);
}

void ecp_push_universe(ecp_t* ecp, uint32_t* u, uint32_t n) {
  ivec_push(&ecp->U, u, n);
}

void ecp_push_subset(ecp_t* ecp, uint32_t* s, uint32_t n) {
  ivec_push(&ecp->S, s, n);
  uint32_t prev = ecp->idxs.size == 0 ? 0 : ecp->idxs.data[ecp->idxs.size - 1];
  uint32_t next = prev + n;
  ivec_push(&ecp->idxs, &next, 1);
}

void search(dlx_t* dlx, results_t* results, uint32_t* res, uint32_t k) {
    if (dlx->R[0] == 0) {
        results_push(results, res, k);
        return;
    }

    node_t j = dlx->R[0];
    uint32_t s = dlx->S[j];
    node_t c = j;
    while (j != 0) {
        if (dlx->S[j] < s) {
            c = j;
            s = dlx->S[j];
        }
        j = dlx->R[j];
    }

    dlx_cover(dlx, c);

    node_t r = dlx->D[c];
    while (r != c) {
        j = dlx->R[r];
        while (j != r) {
            dlx_cover(dlx, dlx->C[j]);
            j = dlx->R[j];
        }

        res[k] = dlx->I[r];
        search(dlx, results, res, k + 1);

        c = dlx->C[r];
        j = dlx->L[r];
        while (j != r) {
            dlx_uncover(dlx, dlx->C[j]);
            j = dlx->L[j];
        }
        r = dlx->D[r];
    }
    dlx_uncover(dlx, c);
}

void ecp_solve(ecp_t* ecp, results_t* results) {
    // Initialize Dancing Links
    dlx_t dlx;
    dlx_init(&dlx, ecp);

    // Init working buffer
    uint32_t* res = calloc(ecp->S.size, sizeof(uint32_t));

    // Solve
    search(&dlx, results, res, 0);

    // Free working buffer
    free(res);

    // Free dancing links
    dlx_destroy(&dlx);
}