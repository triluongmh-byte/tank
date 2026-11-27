#pragma once
// 240x240 network screen: AP name, address, QR (join Wi-Fi / open page). Pure drawing, host-testable.
#include <stdio.h>
#include "face.h"
#include "qr.h"
namespace pet {
inline void drawQr(Canvas& c,const tank::Qr& q,int x,int y,int scale) {
  c.rect(x-scale*4,y-scale*4,(q.size+8)*scale,(q.size+8)*scale,0xFFFF);   // 4-module quiet zone
  for(int j=0;j<q.size;j++)for(int i=0;i<q.size;i++)if(q.m[j][i])c.rect(x+i*scale,y+j*scale,scale,scale,0);
}
// phase false: QR #1 joins the open network; phase true: QR #2 opens the page.
inline void renderNet(Canvas& c,const char* ssid,const char* url,const tank::Qr& wifiQr,const tank::Qr& urlQr,bool phase) {
  c.clear();
  drawText(c,"Xe tăng: nối điện thoại",actionFont,8,22,rgb(255,255,255),0,240,0,240);
  char line[64];
  snprintf(line,sizeof(line),"Wi-Fi: %s",ssid);drawText(c,line,actionFont,8,48,rgb(120,220,140),0,240,0,240);
  snprintf(line,sizeof(line),"Mở: %s",url);drawText(c,line,actionFont,8,72,rgb(120,200,255),0,240,0,240);
  drawText(c,phase?"Quét để mở trang":"Quét để vào Wi-Fi",actionFont,8,96,rgb(220,200,120),0,240,0,240);
  const tank::Qr& q=phase?urlQr:wifiQr;int scale=132/(q.size+8);if(scale<2)scale=2;
  drawQr(c,q,(240-q.size*scale)/2,104+scale*4,scale);
}
}
