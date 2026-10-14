#include <stdio.h>
#include <stdlib.h>
typedef struct node{int v;struct node*next;}node;
int main(){ node*head=NULL; srand(2);
  for(int i=0;i<4000;i++){node*n=malloc(sizeof(node));n->v=rand();n->next=head;head=n;}
  long s=0; for(int r=0;r<5;r++)for(node*p=head;p;p=p->next)s+=p->v;
  printf("%ld\n",s);return 0;}
