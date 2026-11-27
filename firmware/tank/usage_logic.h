#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include "pet_logic.h"
namespace pet {
enum class Provider {Claude,Codex};
struct UsageData {
  Provider provider=Provider::Codex;
  int32_t percent[2]={-1,-1},seconds[2]={-1,-1};
  uint32_t receivedAt=0,ageAt=0;uint64_t sourceAge=0;bool received=false;
  int32_t remaining(unsigned i,uint32_t now) const {
    if(seconds[i]<0) return -1;
    uint32_t elapsed=uint32_t(now-receivedAt)/1000;
    return elapsed>=uint32_t(seconds[i])?0:seconds[i]-int32_t(elapsed);
  }
  uint64_t age(uint32_t now) const {return sourceAge+uint32_t(now-ageAt)/1000;}
  bool any() const {return percent[0]>=0 || percent[1]>=0;}
};
struct UsageParser {
  char line[96]{};unsigned used=0;bool dropping=false;
  bool providerCommand=false;
  static bool integers(const char* p,int32_t* values,unsigned count) {
    for(unsigned i=0;i<count;i++) {
      while(*p==' ') ++p;
      if(!(*p=='-' || (*p>='0' && *p<='9'))) return false;
      errno=0;char* end=nullptr;long value=strtol(p,&end,10);
      if(end==p || errno==ERANGE || value<-1 || value>2147483647L || (*end && *end!=' ')) return false;
      values[i]=int32_t(value);p=end;
    }
    while(*p==' ') ++p;
    return !*p;
  }
  bool feed(char c,UsageData& data,uint32_t now) {
    providerCommand=false;
    if(c!='\n') {
      if(dropping) return false;
      if((uint8_t(c)<32 && c!='\r') || uint8_t(c)>126 || used>=sizeof(line)-1) {dropping=true;used=0;return false;}
      line[used++]=c;return false;
    }
    if(dropping) {dropping=false;used=0;return false;}
    if(used && line[used-1]=='\r') --used;
    line[used]=0;used=0;
    if(!strcmp(line,"PROVIDER codex") || !strcmp(line,"PROVIDER claude")) {
      Provider next=!strcmp(line,"PROVIDER codex")?Provider::Codex:Provider::Claude;
      if(next!=data.provider) {data=UsageData{};data.provider=next;}
      providerCommand=true;return true;
    }
    if(!strncmp(line,"USAGE_AGE ",10)) {
      int32_t value;if(!data.received || !integers(line+10,&value,1) || value<0) return false;
      data.sourceAge=uint32_t(value);data.ageAt=now;return true;
    }
    if(strncmp(line,"USAGE ",6)) return false;
    int32_t v[4];if(!integers(line+6,v,4)) return false;
    for(unsigned i=0;i<4;i+=2) if(v[i]>100 || (v[i]<0)!=(v[i+1]<0)) return false;
    for(unsigned i=0;i<2;i++) {data.percent[i]=v[2*i];data.seconds[i]=v[2*i+1];}
    data.received=true;data.receivedAt=data.ageAt=now;data.sourceAge=0;return true;
  }
};
inline void formatReset(int32_t seconds,char* out,size_t size) {
  if(seconds<0) {snprintf(out,size,"Resets in —");return;}
  uint32_t minutes=uint32_t(seconds)/60,hours=minutes/60,days=hours/24;
  if(days) snprintf(out,size,"Resets in %lud %luh",(unsigned long)days,(unsigned long)(hours%24));
  else if(hours) snprintf(out,size,"Resets in %luh %lum",(unsigned long)hours,(unsigned long)(minutes%60));
  else snprintf(out,size,"Resets in %lum",(unsigned long)minutes);
}
struct UsageView {
  bool showing=false;uint32_t shownAt=0;
  void begin(uint32_t now) {showing=false;shownAt=now;}
  bool update(State state,Press press,uint32_t now,bool petting=false) {
    // Literal priority in the brief: ANY non-idle state shows the face. Ask
    // cannot be covered by a short press, a timer, or a pending transient.
    if(state!=State::Idle || petting) {showing=false;return false;}
    if(showing) {
      if(press!=Press::None || uint32_t(now-shownAt)>=60000) showing=false;
    } else if(press==Press::Short) {showing=true;shownAt=now;}
    return showing;
  }
};
inline const char* usageFooter(State state,uint32_t now) {
  static const char* const words[]={"Philosophizing…","Pondering…","Crunching…","Noodling…","Cogitating…","Musing…","Reasoning…","Considering…","Reflecting…","Contemplating…","Untangling…","Ruminating…"};
  if(state==State::Thinking || state==State::Processing) return words[(now/3000)%12];
  if(state==State::Ask) return "Waiting for approval";
  if(state==State::Accepted) return "Accepted";
  if(state==State::Cancelled) return "Cancelled";
  return "Idle";
}
} // namespace pet
