#pragma once
#include "face.h"
#include "usage_logic.h"
namespace pet {
inline void claudeMark(Canvas& c,int x,int y,int radius,uint16_t color) {
  for(unsigned i=0;i<12;i++) {
    float angle=float(i)*6.2831853f/12;
    c.line(x+int(cosf(angle)*radius/3),y+int(sinf(angle)*radius/3),
           x+int(cosf(angle)*radius),y+int(sinf(angle)*radius),2,color);
  }
}
inline void renderUsage(Canvas& c,const UsageData& data,State state,uint32_t now) {
  c.rect(0,0,W,H,rgb(9,12,18));
  uint16_t coral=rgb(217,119,87),white=rgb(242,245,251),muted=rgb(155,167,187);
  bool codex=data.provider==Provider::Codex;
  if(codex) {
    c.line(16,49,24,56,2,coral);c.line(24,56,16,63,2,coral);
    c.line(27,63,36,63,2,coral);
  } else claudeMark(c,25,56,9,coral);
  drawText(c,codex?"Codex usage":"Claude usage",actionFont,46,63,white,0,240);
  c.rect(12,69,216,1,rgb(32,41,60));
  for(unsigned i=0;i<2;i++) {
    int y=94+int(i)*60;char pct[12],reset[64];
    if(data.percent[i]<0) snprintf(pct,sizeof(pct),"—");else snprintf(pct,sizeof(pct),"%ld%%",(long)data.percent[i]);
    drawText(c,pct,titleFont,12,y,white,0,240);
    const char* label=i?"Weekly":codex?"5-hour":"Current";
    drawText(c,label,actionFont,228-textWidth(label,actionFont),y-2,muted,0,240);
    c.roundRect(12,y+7,216,9,3,rgb(28,39,60));
    int width=data.percent[i]<0?0:216*data.percent[i]/100;
    if(width) c.roundRect(12,y+7,width,9,3,i?rgb(102,214,166):rgb(120,166,244));
    formatReset(data.remaining(i,now),reset,sizeof(reset));
    drawText(c,reset,actionFont,12,y+34,muted,0,240);
  }
  char hint[80]{};
  if(!data.any()) snprintf(hint,sizeof(hint),"No usage data yet");
  else if(data.age(now)>600) snprintf(hint,sizeof(hint),"Updated %llu min ago",(unsigned long long)(data.age(now)/60));
  // Truncate extreme stale ages to the viewport, keeping all drawing bounded.
  drawText(c,hint,actionFont,12,209,muted,194,213);
  c.rect(12,215,216,1,rgb(32,41,60));
  if(!codex) claudeMark(c,19,226,5,coral);
  // Leave the lowest descender inside the235-row content area before the global5px shift.
  drawText(c,usageFooter(state,now),actionFont,31,231,coral,216,235);
}
} // namespace pet
