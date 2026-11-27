#pragma once
#include <Arduino.h>
#include <SPI.h>
#include "pins.h"
namespace tank {
// ST7789 240x240 over SPI (write-only). Frames stream in 20-row bands, one band per show() call,
// so no single call blocks the control loop for more than ~1 ms.
class Display {
  static constexpr unsigned W=240,H=240,BAND=20;
  SPIClass spi{VSPI};const uint16_t* src=nullptr;unsigned pos=0,end=0,base=0;bool ok=false;
  void cmd(uint8_t c){digitalWrite(LCD_DC,LOW);spi.transfer(c);digitalWrite(LCD_DC,HIGH);}
  void cmd(uint8_t c,std::initializer_list<uint8_t> d){digitalWrite(LCD_CS,LOW);cmd(c);for(uint8_t x:d)spi.transfer(x);digitalWrite(LCD_CS,HIGH);}
  void window(unsigned y0,unsigned y1){
    cmd(0x2A,{0,0,0,uint8_t(W-1)});cmd(0x2B,{uint8_t(y0>>8),uint8_t(y0),uint8_t(y1>>8),uint8_t(y1)});
  }
public:
  bool begin() {
    digitalWrite(LCD_BL,LOW);pinMode(LCD_BL,OUTPUT);
    digitalWrite(LCD_CS,HIGH);pinMode(LCD_CS,OUTPUT);pinMode(LCD_DC,OUTPUT);pinMode(LCD_RST,OUTPUT);
    spi.begin(LCD_SCK,-1,LCD_MOSI,LCD_CS);spi.setFrequency(LCD_HZ);spi.setDataMode(SPI_MODE0);
    digitalWrite(LCD_RST,LOW);delay(10);digitalWrite(LCD_RST,HIGH);delay(120);
    spi.beginTransaction(SPISettings(LCD_HZ,MSBFIRST,SPI_MODE0));
    cmd(0x01,{});delay(120);cmd(0x11,{});delay(120);
    cmd(0x3A,{0x55});cmd(0x36,{0x00});cmd(0x21,{});  // RGB565, normal scan, inversion on (typical 1.54" IPS)
    cmd(0x13,{});cmd(0x29,{});delay(20);
    spi.endTransaction();
    ok=true;digitalWrite(LCD_BL,HIGH);return true;
  }
  bool busy()const{return pos<end;}
  // Queue rows [y0,y0+rows) held in buf (big-endian RGB565 already, as pet::Canvas stores them).
  bool start(const uint16_t* buf,unsigned y0,unsigned rows){if(!ok||busy()||y0+rows>H||rows%BAND)return false;src=buf;pos=y0;end=y0+rows;base=y0;return true;}
  // One 20-row band per call (~1 ms). Returns false only if not initialized.
  bool step(){
    if(!ok)return false;if(!busy())return true;
    spi.beginTransaction(SPISettings(LCD_HZ,MSBFIRST,SPI_MODE0));
    window(pos,pos+BAND-1);
    digitalWrite(LCD_CS,LOW);cmd(0x2C);spi.writeBytes(reinterpret_cast<const uint8_t*>(src+(pos-base)*W),W*BAND*2);digitalWrite(LCD_CS,HIGH);
    spi.endTransaction();pos+=BAND;return true;
  }
};
}
