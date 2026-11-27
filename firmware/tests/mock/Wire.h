#pragma once
#include <stdint.h>
#include <stddef.h>
struct MockWire {
 uint8_t regs[256]{};uint8_t at=0;bool first=true;
 void beginTransmission(uint8_t){first=true;}
 size_t write(uint8_t b){if(first){at=b;first=false;}else regs[at++]=b;return 1;}
 size_t write(const uint8_t* b,unsigned n){for(unsigned i=0;i<n;i++)write(b[i]);return n;}
 int endTransmission(bool=true){return 0;}
 unsigned requestFrom(uint8_t,uint8_t n){return n;}
 uint8_t read(){return regs[at++];}
};
extern MockWire Wire;
