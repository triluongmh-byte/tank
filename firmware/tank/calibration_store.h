#pragma once
#include "controller.h"
namespace tank {
constexpr unsigned CAL_SIZE=48;
inline uint32_t crc32(const uint8_t* data,unsigned n){uint32_t c=~0u;while(n--){c^=*data++;for(unsigned b=0;b<8;b++)c=(c>>1)^(0xEDB88320u&(0u-(c&1)));}return ~c;}
inline void encode(const Calibration& c,uint8_t (&b)[CAL_SIZE]) {
  memset(b,0,sizeof(b));b[0]='T';b[1]='K';b[2]=1;
  for(unsigned i=0;i<6;i++){unsigned o=4+6*i;const auto& w=c.wheels[i];b[o]=uint8_t(w.neutral);b[o+1]=uint8_t(w.neutral>>8);b[o+2]=uint8_t(w.span);b[o+3]=uint8_t(w.direction);b[o+4]=w.calibrated;}
  b[40]=uint8_t(c.turretCenter);b[41]=uint8_t(c.turretCenter>>8);b[42]=uint8_t(c.turretUsPerDegree);
  uint32_t crc=crc32(b,44);for(unsigned i=0;i<4;i++)b[44+i]=uint8_t(crc>>(8*i));
}
inline bool decode(const uint8_t (&b)[CAL_SIZE],Calibration& out) {
  if(b[0]!='T'||b[1]!='K'||b[2]!=1)return false;
  uint32_t crc=0;for(unsigned i=0;i<4;i++)crc|=uint32_t(b[44+i])<<(8*i);if(crc32(b,44)!=crc)return false;
  Calibration c;
  for(unsigned i=0;i<6;i++){unsigned o=4+6*i;if(b[o+4]>1)return false;c.wheels[i]={uint16_t(b[o]|unsigned(b[o+1])<<8),b[o+2],int8_t(b[o+3]),b[o+4]!=0};}
  c.turretCenter=b[40]|unsigned(b[41])<<8;c.turretUsPerDegree=b[42];if(!c.valid())return false;out=c;return true;
}
}
