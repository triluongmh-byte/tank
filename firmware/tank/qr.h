#pragma once
// Minimal QR encoder: byte mode, error correction L, versions 1-4 (single block, up to 78 bytes). No allocation.
#include <stdint.h>
#include <string.h>
namespace tank {
struct Qr {
  static constexpr int MAXN=33;
  uint8_t size=0;bool ok=false;uint8_t mask=0;
  bool m[MAXN][MAXN]{};bool fn[MAXN][MAXN]{};
  bool dark(int x,int y)const{return x>=0&&y>=0&&x<size&&y<size&&m[y][x];}
  bool encode(const char* text) {
    static const uint8_t data[5]={0,19,34,55,80},ecc[5]={0,7,10,15,20};
    size_t len=strlen(text);int v=0;
    for(int i=1;i<=4;i++)if(len<=size_t(data[i]-2)){v=i;break;}
    ok=false;if(!v)return false;
    int nd=data[v],ne=ecc[v];uint8_t cw[80+20]{};int bits=0;
    auto put=[&](unsigned val,int n){for(int i=n-1;i>=0;i--){if((val>>i)&1)cw[bits>>3]|=uint8_t(0x80>>(bits&7));bits++;}};
    put(4,4);put(unsigned(len),8);for(size_t i=0;i<len;i++)put(uint8_t(text[i]),8);
    int cap=nd*8;int t=cap-bits<4?cap-bits:4;bits+=t;bits=(bits+7)&~7;
    for(int pad=0xEC;bits<cap;pad^=0xEC^0x11){cw[bits>>3]=uint8_t(pad);bits+=8;}
    // Reed-Solomon over GF(256), poly 0x11D.
    uint8_t exp[256],lg[256];{int x=1;for(int i=0;i<255;i++){exp[i]=uint8_t(x);lg[x]=uint8_t(i);x<<=1;if(x&0x100)x^=0x11D;}exp[255]=exp[0];}
    auto mul=[&](int a,int b)->int{return(a&&b)?exp[(lg[a]+lg[b])%255]:0;};
    uint8_t gen[20]{};gen[ne-1]=1;int root=1;   // coefficients highest degree first, leading 1 omitted
    for(int i=0;i<ne;i++){for(int j=0;j<ne;j++){gen[j]=uint8_t(mul(gen[j],root));if(j+1<ne)gen[j]^=gen[j+1];}root=mul(root,2);}
    uint8_t rem[20]{};
    for(int i=0;i<nd;i++){
      int f=cw[i]^rem[0];memmove(rem,rem+1,size_t(ne-1));rem[ne-1]=0;
      for(int k=0;k<ne;k++)rem[k]^=uint8_t(mul(gen[k],f));
    }
    memcpy(cw+nd,rem,size_t(ne));
    size=uint8_t(17+4*v);memset(m,0,sizeof(m));memset(fn,0,sizeof(fn));
    auto setf=[&](int x,int y,bool d){if(x<0||y<0||x>=size||y>=size)return;m[y][x]=d;fn[y][x]=true;};
    for(int i=0;i<size;i++){setf(6,i,i%2==0);setf(i,6,i%2==0);}
    const int fx[3]={0,size-7,0},fy[3]={0,0,size-7};
    for(int f=0;f<3;f++)for(int dy=-1;dy<=7;dy++)for(int dx=-1;dx<=7;dx++){
      int x=fx[f]+dx,y=fy[f]+dy;int d=dx<0||dy<0||dx>6||dy>6?-1:0;
      bool on=false;if(d==0){int ax=dx>3?6-dx:dx,ay=dy>3?6-dy:dy;int mn=ax<ay?ax:ay;on=mn!=1;}
      setf(x,y,on);
    }
    if(v>=2){int c=size-7;for(int dy=-2;dy<=2;dy++)for(int dx=-2;dx<=2;dx++){int a=dx<0?-dx:dx,b=dy<0?-dy:dy;setf(c+dx,c+dy,(a>b?a:b)!=1);}}
    for(int i=0;i<9;i++){fn[8][i]=fn[i][8]=true;}for(int i=0;i<8;i++){fn[8][size-1-i]=true;fn[size-1-i][8]=true;}
    setf(8,size-8,true);
    // place codewords
    int total=(nd+ne)*8,idx=0;
    for(int right=size-1;right>=1;right-=2){
      if(right==6)right=5;
      for(int vert=0;vert<size;vert++)for(int j=0;j<2;j++){
        int x=right-j;bool up=((right+1)&2)==0;int y=up?size-1-vert:vert;
        if(!fn[y][x]&&idx<total){m[y][x]=(cw[idx>>3]>>(7-(idx&7)))&1;idx++;}
      }
    }
    int best=0,bestScore=1<<30;
    for(int k=0;k<8;k++){applyMask(k);format(k);int s=penalty();if(s<bestScore){bestScore=s;best=k;}applyMask(k);}
    applyMask(best);format(best);mask=uint8_t(best);ok=true;return true;
  }
private:
  void applyMask(int k){
    for(int y=0;y<size;y++)for(int x=0;x<size;x++){
      if(fn[y][x])continue;bool inv=false;
      switch(k){case 0:inv=(x+y)%2==0;break;case 1:inv=y%2==0;break;case 2:inv=x%3==0;break;case 3:inv=(x+y)%3==0;break;
        case 4:inv=(x/3+y/2)%2==0;break;case 5:inv=x*y%2+x*y%3==0;break;case 6:inv=(x*y%2+x*y%3)%2==0;break;default:inv=((x+y)%2+x*y%3)%2==0;}
      if(inv)m[y][x]=!m[y][x];
    }
  }
  void format(int k){
    unsigned data=(1u<<3)|unsigned(k),r=data;for(int i=0;i<10;i++)r=(r<<1)^((r>>9)*0x537);
    unsigned b=((data<<10)|r)^0x5412;auto bit=[&](int i){return((b>>i)&1)!=0;};
    for(int i=0;i<=5;i++)m[i][8]=bit(i);m[7][8]=bit(6);m[8][8]=bit(7);m[8][7]=bit(8);
    for(int i=9;i<15;i++)m[8][14-i]=bit(i);
    for(int i=0;i<8;i++)m[8][size-1-i]=bit(i);for(int i=8;i<15;i++)m[size-15+i][8]=bit(i);
    m[size-8][8]=true;
  }
  int penalty()const{
    int s=0,darkN=0;
    for(int pass=0;pass<2;pass++)for(int a=0;a<size;a++){
      int run=1;unsigned hist=0;
      for(int b=0;b<size;b++){
        bool c=pass?m[b][a]:m[a][b];if(c)darkN++;
        if(b>0){bool p=pass?m[b-1][a]:m[a][b-1];if(c==p){run++;if(run==5)s+=3;else if(run>5)s++;}else run=1;}
        hist=((hist<<1)|(c?1u:0u))&0x7FF;
        if(b>=10&&(hist==0x5D0||hist==0x05D))s+=40;
      }
    }
    for(int y=0;y+1<size;y++)for(int x=0;x+1<size;x++)if(m[y][x]==m[y][x+1]&&m[y][x]==m[y+1][x]&&m[y][x]==m[y+1][x+1])s+=3;
    int totalN=size*size,diff=darkN*20-totalN*10;if(diff<0)diff=-diff;s+=((diff+totalN-1)/totalN-1)*10;
    return s;
  }
};
}
