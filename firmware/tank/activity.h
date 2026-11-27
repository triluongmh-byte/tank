#pragma once
#include <stdint.h>
#include <string.h>
#include "pet_logic.h"
namespace pet {
enum class ActivityEvent { None, Sessions, Celebrate };
struct Activity {
  unsigned sessions=0;
  uint32_t started=0;
  bool active=false;
  char lastId[17]{};
  void update(State state,uint32_t now,bool interaction=false) {
    if(state!=State::Idle || sessions || interaction || uint32_t(now-started)>=1000) active=false;
  }
};
struct ActivityParser {
  char line[40]{};
  unsigned length=0;
  bool invalid=false;
  ActivityEvent feed(char ch,Activity& data,uint32_t now) {
    if(ch!='\n') {
      if(ch=='\r') {if(length<sizeof(line)-1) line[length++]=ch;else invalid=true;}
      else if(ch<32 || ch>126 || length>=sizeof(line)-1) invalid=true;
      else line[length++]=ch;
      return ActivityEvent::None;
    }
    if(length && line[length-1]=='\r') --length;
    line[length]=0;ActivityEvent result=ActivityEvent::None;
    if(!invalid && !strncmp(line,"SESSIONS ",9)) {
      unsigned value=0,n=length-9;bool valid=n>=1 && n<=3;
      for(unsigned i=9;i<length;i++) {
        if(line[i]<'0' || line[i]>'9') {valid=false;break;}
        value=value*10+unsigned(line[i]-'0');
      }
      if(valid) {data.sessions=value;if(value) data.active=false;result=ActivityEvent::Sessions;}
    } else if(!invalid && length==26 && !strncmp(line,"CELEBRATE ",10)) {
      bool valid=true;
      for(unsigned i=10;i<26;i++) if(!((line[i]>='0' && line[i]<='9') || (line[i]>='a' && line[i]<='f'))) valid=false;
      if(valid) {
        if(strcmp(data.lastId,line+10)) {
          strcpy(data.lastId,line+10);
          data.started=now;data.active=data.sessions==0;
        }
        result=ActivityEvent::Celebrate;
      }
    }
    length=0;invalid=false;return result;
  }
};
} // namespace pet
