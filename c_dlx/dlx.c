#include "dlx.h"

#include <stdlib.h>
#include <stdio.h>

const node_t EMPTY = UINT32_MAX;

void link(node_t* prev, node_t* next, node_t* nodes, uint32_t n) {
    for (uint32_t i = 0; i < n; ++i) {
        prev[nodes[i]] = nodes[(i + n - 1) % n];
        next[nodes[(i + n - 1) % n]] = nodes[i];
    }
}

void dlx_init(dlx_t* dlx, ecp_t* ecp) {
    node_t n_nodes = 0;

    // Dimensions
    uint32_t m = ecp->idxs.size; // rows
    uint32_t n = ecp->U.size;    // cols

    // root node
    node_t h = n_nodes++;

    // header nodes
    node_t* header = malloc(n * sizeof(node_t));
    for (int i = 0; i < n; ++i) header[i] = n_nodes++;

    // data nodes
    uint32_t* s_row = calloc(m, sizeof(node_t));
    uint32_t* s_col = calloc(n, sizeof(node_t));
    node_t* data = malloc(n * m * sizeof(node_t));
    for (int j = 0; j < m; ++j) { // rows
        for (int i = 0; i < n; ++i) { // cols
            if (ecp_s_contains(ecp, j, i)) {
                data[i * m + j] = n_nodes++;
                s_row[j]++;
                s_col[i]++;
            } else {
                data[i * m + j] = EMPTY;
            }
        }
    }

    // Allocate links
    dlx->L = malloc(n_nodes * sizeof(uint32_t));
    dlx->R = malloc(n_nodes * sizeof(uint32_t));
    dlx->U = malloc(n_nodes * sizeof(uint32_t));
    dlx->D = malloc(n_nodes * sizeof(uint32_t));
    dlx->S = malloc(n_nodes * sizeof(uint32_t));
    dlx->C = malloc(n_nodes * sizeof(uint32_t));
    dlx->N = malloc(n_nodes * sizeof(uint32_t));
    dlx->I = malloc(n_nodes * sizeof(uint32_t));
    dlx->size = n_nodes;

    // header meta data
    for (int i = 0; i < n; ++i) { // cols
        dlx->S[header[i]] = s_col[i];
        dlx->C[header[i]] = header[i];
        dlx->N[header[i]] = i;
    }

    // Link header nodes
    node_t* header_nodes = malloc((n + 1) * sizeof(node_t));
    header_nodes[0] = h;
    for (int i = 0; i < n; ++i) header_nodes[i + 1] = header[i];
    link(dlx->L, dlx->R, header_nodes, n + 1);
    free(header_nodes);

    // Vertical links
    for (int i = 0; i < n; ++i) { // cols
        uint32_t s = s_col[i];
        node_t* vertical_nodes = malloc((s + 1) * sizeof(node_t));
        uint32_t k = 0;
        vertical_nodes[k++] = header[i];
        for (int j = 0; j < m; ++j) { // rows
            node_t node = data[i * m + j];
            if (node != EMPTY) {
                vertical_nodes[k++] = node;
                dlx->C[node] = header[i];
                dlx->I[node] = j;
            }
        }
        link(dlx->U, dlx->D, vertical_nodes, s + 1);
        free(vertical_nodes);
    }

    // Horizontal links
    for (int j = 0; j < m; ++j) { // rows
        uint32_t s = s_row[j];
        node_t* horizontal_nodes = malloc((s) * sizeof(node_t));
        uint32_t k = 0;
        for (int i = 0; i < n; ++i) { // cols
            node_t node = data[i * m + j];
            if (node != EMPTY) horizontal_nodes[k++] = node;
        }
        link(dlx->L, dlx->R, horizontal_nodes, s);
        free(horizontal_nodes);
    }

    // Free working data structures
    free(data);
    free(header);
    free(s_row);
    free(s_col);
}

void dlx_destroy(dlx_t* dlx) {
    free(dlx->L);
    free(dlx->R);
    free(dlx->U);
    free(dlx->D);
    free(dlx->S);
    free(dlx->C);
    free(dlx->N);
    free(dlx->I);
}

void dlx_cover(dlx_t* dlx, node_t c) {
    uint32_t *L = dlx->L, *R = dlx->R, *U = dlx->U, *D = dlx->D, *S = dlx->S, *C = dlx->C;

    L[R[c]] = L[c];
    R[L[c]] = R[c];
    node_t i = D[c];
    while (i != c) {
        node_t j = R[i];
        while (j != i) {
            U[D[j]] = U[j];
            D[U[j]] = D[j];
            S[C[j]] -= 1;
            j = R[j];
        }
        i = D[i];
    }
}

void dlx_uncover(dlx_t* dlx, node_t c) {
    uint32_t *L = dlx->L, *R = dlx->R, *U = dlx->U, *D = dlx->D, *S = dlx->S, *C = dlx->C;

    node_t i = U[c];
    while (i != c) {
        node_t j = L[i];
        while (j != i) {
            S[C[j]] += 1;
            U[D[j]] = j;
            D[U[j]] = j;
            j = L[j];
        }
        i = U[i];
    }
    L[R[c]] = c;
    R[L[c]] = c;
}
