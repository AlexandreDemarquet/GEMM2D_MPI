#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <cblas.h>
#include "utils.h"
#include "dsmat.h"
#include "gemms.h"

void p2p_i_transmit_A(int p, int q, Matrix *A, int i, int l) {
  int j, b;
  int me, my_row, my_col;
  MPI_Comm_rank(MPI_COMM_WORLD, &me);
  node_coordinates_2i(p,q,me,&my_row,&my_col);

  int node, tag;
  Block * Ail;
  Ail =  & A->blocks[i][l];
  b = A->b;
  /* transmit A[i,l] using MPI_Issend/recv */
  if (me == Ail->owner /* I own A[i,l] */) {
    // MPI_Issend Ail to my row
    for (j = 0; j < q; j++) {
      if (j != my_col) {
        node = get_node(p, q, my_row, j);
        tag = 0; // or any other tag you want to use
        MPI_Issend(Ail->c, b*b, MPI_FLOAT, node, tag, MPI_COMM_WORLD, &Ail->request);
        // printf("Node %d sent A[%d,%d] to node %d\n", me, i, l, node);
      }
    }
  } else if (Ail-> row == my_row /* A[i,l] is stored on my row */) {
    Ail->c = calloc(b*b,sizeof(float));
    // MPI_Irecv Ail
    tag = 0; 
    MPI_Irecv(Ail->c, b*b, MPI_FLOAT, Ail->owner, tag, MPI_COMM_WORLD, &Ail->request);
  }

}

void p2p_i_transmit_B(int p, int q, Matrix *B, int l, int j) {
  int i,b;
  int me, my_row, my_col;
  MPI_Comm_rank(MPI_COMM_WORLD, &me);
  node_coordinates_2i(p,q,me,&my_row,&my_col);

  int node, tag;
  Block * Blj;
  Blj =  & B->blocks[l][j];
  b = B->b;
  /* transmit B[l,j] using MPI_Issend/recv */
  if (Blj->owner == me /* I own B[l,j] */) {
    // MPI_Issend Blj to my column
    for (i = 0; i < p; i++) {
      if (i != my_row) {
        node = get_node(p, q, i, my_col);
        tag = 0; // or any other tag you want to use
        MPI_Issend(Blj->c, b*b, MPI_FLOAT, node, tag, MPI_COMM_WORLD, &Blj->request);
        // printf("Node %d sent B[%d,%d] to node %d\n", me, l, j, node);
      }
    }
  } else if (Blj->col == my_col /* B[l,j] is stored on my column */) {
    Blj->c = calloc(b*b,sizeof(float));
    // MPI_Irecv B[l,j]
    tag = 0;
    MPI_Irecv(Blj->c, b*b, MPI_FLOAT, Blj->owner, tag, MPI_COMM_WORLD, &Blj->request);
  }

}

void p2p_i_wait_AB(int p, int q, Matrix *A, Matrix* B, Matrix* C, int l) {
  int me, my_row, my_col;
  MPI_Comm_rank(MPI_COMM_WORLD, &me);
  node_coordinates_2i(p,q,me,&my_row,&my_col);

  int i, j;
  Block *Ail, *Blj;
  /*  wait for A[i,l] and B[l,j] if I need them */
  for (i = 0; i < A->mb ; i++) {
    Ail = &(A->blocks[i][l]);
    if (Ail->owner != me && my_row == Ail->row) {/* I need A[i,l] for my computation */
            // MPI_Wait Ail
            MPI_Wait(&Ail->request, MPI_STATUS_IGNORE);
    }
  }
  for (j =0; j < B->nb; j++) {
    Blj = &(B->blocks[l][j]);
    if (Blj->owner != me && my_col == Blj->col) {/* I need B[l,j] for my computation */
            // MPI_Wait Blj
            MPI_Wait(&Blj->request, MPI_STATUS_IGNORE);
            
        }
  }

  /* Alternative suggestion : iterate over blocks of C */
}
