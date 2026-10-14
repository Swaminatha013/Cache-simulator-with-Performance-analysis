#include <stdio.h>
#define N 48
#define T 8
double A[N][N],B[N][N],C[N][N];
int main(){
  for(int i=0;i<N;i++)for(int j=0;j<N;j++){A[i][j]=i+j;B[i][j]=i-j;C[i][j]=0;}
  for(int ii=0;ii<N;ii+=T)for(int jj=0;jj<N;jj+=T)for(int kk=0;kk<N;kk+=T)
   for(int i=ii;i<ii+T;i++)for(int j=jj;j<jj+T;j++)for(int k=kk;k<kk+T;k++)C[i][j]+=A[i][k]*B[k][j];
  printf("%f\n",C[N-1][N-1]);return 0;}
