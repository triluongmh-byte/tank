#pragma once
#include <stdio.h>
#include "face.h"
namespace pet {
struct HostStatus {
  uint32_t seconds=0,at=0;int wifi=-1,battery=-1,charging=-1;bool valid=false;
  bool fresh(uint32_t now) const {return valid && uint32_t(now-at)<60000;}
  void clock(char* out,size_t size,uint32_t now) const {
    if(!fresh(now)){snprintf(out,size,"--:--");return;}
    uint32_t s=(seconds+uint32_t(now-at)/1000)%86400;
    snprintf(out,size,"%02u:%02u",unsigned(s/3600),unsigned(s/60%60));
  }
};
struct HostStatusParser {
  char line[64]{};unsigned used=0;bool invalid=false;
  bool feed(char c,HostStatus& status,uint32_t now){
    if(c!='\n'){
      if(uint8_t(c)<32 && c!='\r')invalid=true;
      if(used>=sizeof(line)-1)invalid=true;
      if(!invalid)line[used++]=c;
      return false;
    }
    if(used && line[used-1]=='\r')--used;
    line[used]=0;bool ok=false;
    if(!invalid && !strncmp(line,"HOST ",5)){
      // Parse bounded decimal fields without accepting signs, junk or overflow.
      int values[4]{};const char* p=line+5;bool good=true;
      for(unsigned i=0;i<4 && good;i++){
        bool negative=*p=='-';if(negative)++p;
        if(*p<'0'||*p>'9'){good=false;break;}
        int value=0;unsigned digits=0;
        while(*p>='0'&&*p<='9'){if(++digits>5){good=false;break;}value=value*10+(*p++-'0');}
        values[i]=negative?-value:value;
        if(i<3){if(*p++!=' ')good=false;}else if(*p)good=false;
      }
      if(good && values[0]>=0 && values[0]<86400 && values[1]>=-1 && values[1]<=4 && values[2]>=-1 && values[2]<=100 && values[3]>=-1 && values[3]<=1){
        status.seconds=uint32_t(values[0]);status.wifi=values[1];status.battery=values[2];status.charging=values[3];status.at=now;status.valid=true;ok=true;
      }
    }
    used=0;invalid=false;return ok;
  }
};
inline void renderStatusBar(Canvas& c,const HostStatus& status,uint32_t now,bool sleeping=false){
  c.rect(0,0,W,48,0);
  uint16_t ink=sleeping?rgb(32,35,40):rgb(190,198,210),muted=sleeping?rgb(7,9,12):rgb(40,48,60);
  char clock[8],percent[8];status.clock(clock,sizeof(clock),now);
  drawText(c,clock,actionFont,12,42,ink,22,48);
  bool fresh=status.fresh(now);int wifi=fresh?status.wifi:-1,battery=fresh?status.battery:-1;
  // Four signal bars describe the Mac's Wi-Fi, never an ESP radio connection.
  for(int i=0;i<4;i++)c.rect(123+i*5,39-i*3,3,4+i*3,wifi>i?ink:muted);
  if(wifi<0)drawText(c,"?",actionFont,144,42,ink,22,48);
  else if(!wifi)c.line(123,29,141,42,1,ink);
  c.rect(163,30,18,12,ink);c.rect(164,31,16,10,0);c.rect(181,33,2,6,ink);
  if(battery>=0){int fill=(14*battery+50)/100;if(fill)c.rect(165,32,fill,8,ink);snprintf(percent,sizeof(percent),"%d%%",battery);}
  else snprintf(percent,sizeof(percent),"--");
  drawText(c,percent,actionFont,226-textWidth(percent,actionFont),42,ink,22,48);
  if(fresh && status.charging==1){c.line(158,29,154,35,1,ink);c.line(154,35,159,35,1,ink);c.line(159,35,155,42,1,ink);}
}
} // namespace pet
