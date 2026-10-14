#include <stdio.h>
#define N 48
double A[N][N],B[N][N],C[N][N];
int main(){
  for(int i=0;i<N;i++)for(int j=0;j<N;j++){A[i][j]=i+j;B[i][j]=i-j;C[i][j]=0;}
  for(int i=0;i<N;i++)for(int j=0;j<N;j++)for(int k=0;k<N;k++)C[i][j]+=A[i][k]*B[k][j];
  printf("%f\n",C[N-1][N-1]);return 0;}
