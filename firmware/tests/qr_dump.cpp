#include <stdio.h>
#include "qr.h"
int main(int,char** argv){tank::Qr q;if(!q.encode(argv[1])){puts("FAIL");return 1;}printf("%d %d\n",q.size,q.mask);for(int y=0;y<q.size;y++){for(int x=0;x<q.size;x++)putchar(q.m[y][x]?'1':'0');putchar('\n');}}
