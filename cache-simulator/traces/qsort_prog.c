#include <stdio.h>
#include <stdlib.h>
static int cmp(const void*a,const void*b){return *(int*)a-*(int*)b;}
int main(){ int n=6000; int*a=malloc(n*sizeof(int)); srand(1);
  for(int i=0;i<n;i++)a[i]=rand()%100000;
  qsort(a,n,sizeof(int),cmp); printf("%d\n",a[n/2]); free(a); return 0;}
