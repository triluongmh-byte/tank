#pragma once
#include <stdint.h>
#include "pins.h"
namespace tank {
// Bus: write(register, bytes, count), read(register, bytes, count), waitUs().
template<class Bus> class Pca9685 {
  Bus& bus;
  bool reg(uint8_t r,uint8_t value){return bus.write(r,&value,1);}
public:
  explicit Pca9685(Bus& b):bus(b){}
  bool initialize() {
    // Sleep required before PRESCALE; AI enabled. MODE2 OUTDRV=1, OUTNE=00 => low with OE high.
    if(!reg(0x00,0x30)||!reg(0x01,0x04)||!reg(0xFE,PCA_PRESCALE))return false;
    uint8_t off[]={0,0,0,0x10};
    if(!bus.write(0xFA,off,4))return false;
    for(unsigned i=0;i<16;i++)if(!bus.write(0x06+4*i,off,4))return false;
    // ALL_LED writes broadcast into channel registers (NXP section 7.3.4).
    // Do not clear ALL_LED afterward: that would overwrite the per-channel full-off bits.
    if(!reg(0x00,0x20))return false;
    bus.waitUs(600);if(!reg(0x00,0xA0))return false;
    return healthy();
  }
  static uint16_t ticks(uint16_t us) {
    // 25MHz nominal oscillator, PRESCALE=121 => frame 19988.48us (~50.029Hz).
    return uint16_t((uint32_t(us)*25u+61u)/122u);
  }
  bool frame(const uint16_t (&us)[16]) {
    // Small bursts stay below Wire's smallest supported buffer. ACK checked per channel.
    for(unsigned i=0;i<16;i++) {
      uint8_t b[4]={0,0,0,0x10};
      if(us[i]){if(us[i]<500||us[i]>2500)return false;unsigned t=ticks(us[i]);b[2]=uint8_t(t);b[3]=uint8_t(t>>8);}
      if(!bus.write(0x06+4*i,b,4))return false;
    }
    return true;
  }
  bool begin(){return initialize();}
  bool healthy() {
    uint8_t mode=0,mode2=0,pre=0;
    return bus.read(0,&mode,1)&&bus.read(1,&mode2,1)&&bus.read(0xFE,&pre,1)&&
           (mode&0x70)==0x20&&(mode2&0x1F)==0x04&&pre==PCA_PRESCALE;
  }
};
}
