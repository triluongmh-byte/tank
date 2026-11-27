#pragma once
#include <stdint.h>
#include <string.h>
#include "pet_logic.h"
namespace pet {
enum class ToolMood { Generic, Read, Edit, Test };
enum class FunEvent { None, Mood, Power };
struct Fun {
  ToolMood mood=ToolMood::Generic;
  bool sleeping=false,waking=false,heart=false,strokeEligible=false;
  unsigned strokes=0;
  uint32_t wakeAt=0,heartAt=0,strokeAt=0;
  void power(bool sleep,uint32_t now) {
    if(sleep==sleeping) return;
    sleeping=sleep;waking=!sleep;wakeAt=now;
    heart=false;strokes=0;strokeEligible=false;
  }
  void update(State state,uint32_t now,bool held,uint32_t heldElapsed,Press press,bool usage) {
    if(sleeping || state!=State::Idle || usage) {
      heart=false;strokes=0;strokeEligible=false;
      if(state!=State::Idle) waking=false;
      return;
    }
    if(waking && uint32_t(now-wakeAt)>=1200) waking=false;
    if(heart && uint32_t(now-heartAt)>=1800) heart=false;
    if(strokes && uint32_t(now-strokeAt)>12000) strokes=0;
    if(held && heldElapsed>=800) strokeEligible=true;
    if(press==Press::Short) {strokes=0;heart=false;}
    if(press==Press::Long && strokeEligible) {
      strokeAt=now;
      if(++strokes==3) {strokes=0;heart=true;heartAt=now;}
    }
    if(!held) strokeEligible=false;
  }
};
struct FunParser {
  char line[24]{};
  unsigned length=0;
  bool invalid=false;
  FunEvent feed(char ch,Fun& fun,uint32_t now) {
    if(ch!='\n') {
      if((uint8_t(ch)<32 && ch!='\r') || uint8_t(ch)>126 || length>=sizeof(line)-1) invalid=true;
      else line[length++]=ch;
      return FunEvent::None;
    }
    if(length && line[length-1]=='\r') --length;
    line[length]=0;FunEvent result=FunEvent::None;
    if(!invalid) {
      if(!strcmp(line,"POWER sleep") || !strcmp(line,"POWER awake")) {
        fun.power(!strcmp(line,"POWER sleep"),now);result=FunEvent::Power;
      } else {
        const char* words[]={"MOOD generic","MOOD read","MOOD edit","MOOD test"};
        for(unsigned i=0;i<4;i++) if(!strcmp(line,words[i])) {fun.mood=ToolMood(i);result=FunEvent::Mood;}
      }
    }
    length=0;invalid=false;return result;
  }
};
// Dream icons cycle fish, coffee and terminal, without changing lifecycle data.
inline int dreamKind(uint32_t idleElapsed) {
  if(idleElapsed<30000 || idleElapsed%40000<30000 || idleElapsed%40000>=34000) return -1;
  return int((idleElapsed/40000)%3);
}
} // namespace pet
