#pragma once
#include <stdint.h>
#include <string.h>
#include "pet_logic.h"
namespace pet {
inline uint32_t utf8Next(const char*& p) {
  uint8_t c=uint8_t(*p++);
  if(c<128) return c;
  int count=c>=0xC2 && c<=0xDF?1:c>=0xE0 && c<=0xEF?2:c>=0xF0 && c<=0xF4?3:-1;
  if(count<0) return 0xFFFFFFFF;
  uint32_t value=c&((1<<(6-count))-1);
  for(int i=0;i<count;i++) { uint8_t b=uint8_t(*p);if(b<0x80 || b>0xBF) return 0xFFFFFFFF;value=(value<<6)|(b&63);++p; }
  if((count==1 && value<128)||(count==2 && value<2048)||(count==3 && value<65536)||value>0x10FFFF||(value>=0xD800 && value<=0xDFFF)) return 0xFFFFFFFF;
  return value;
}
struct DisplayText {
  char title[161]="Codex",action[97]="";
  uint32_t titleAt=0,actionAt=0;
};
enum class TextEvent : uint8_t { None, Title, Action };
struct TextParser {
  char line[328]{};unsigned used=0;bool dropping=false;
  static int hex(char c) {return c>='0' && c<='9'?c-'0':c>='a' && c<='f'?c-'a'+10:c>='A' && c<='F'?c-'A'+10:-1;}
  TextEvent feed(char c,DisplayText& text,uint32_t now) {
    if(c!='\n') {
      if(dropping) return TextEvent::None;
      if(uint8_t(c)<32 && c!='\r') {dropping=true;used=0;return TextEvent::None;}
      if(used>=sizeof(line)-1) {dropping=true;used=0;return TextEvent::None;}
      line[used++]=c;return TextEvent::None;
    }
    if(dropping) {dropping=false;used=0;return TextEvent::None;}
    if(used && line[used-1]=='\r') --used;
    line[used]=0;used=0;
    bool title=!strncmp(line,"TITLE ",6),action=!strncmp(line,"ACTION ",7);
    if(!title && !action) return TextEvent::None;
    const char* raw=line+(title?6:7);size_t length=strlen(raw);
    if(length%2 || length/2>(title?160:96)) return TextEvent::None;
    char decoded[161]{};
    for(size_t i=0;i<length;i+=2) {
      int a=hex(raw[i]),b=hex(raw[i+1]);if(a<0 || b<0) return TextEvent::None;
      uint8_t byte=uint8_t(a*16+b);if(byte<32 || byte==127) return TextEvent::None;
      decoded[i/2]=char(byte);
    }
    const char* p=decoded;while(*p) {uint32_t code=utf8Next(p);if(code==0xFFFFFFFF || (code>=127 && code<160)) return TextEvent::None;}
    char* target=title?text.title:text.action;
    if(strcmp(target,decoded)) {strcpy(target,decoded);if(title) text.titleAt=now;else text.actionAt=now;}
    return title?TextEvent::Title:TextEvent::Action;
  }
};
inline const char* defaultAction(State state) {
  static const char* names[]={"Idle","Waiting for approval","Thinking","Working","Accepted","Cancelled"};
  return names[unsigned(state)];
}
} // namespace pet
