#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
namespace pet {
enum class State : uint8_t { Idle, Ask, Thinking, Processing, Accepted, Cancelled };
enum class Command : uint8_t { Idle, Ask, Thinking, Processing, Accepted, Cancelled, Ping, None, Layout };
inline const char* name(State s) {
  static const char* const names[] = {"idle", "ask", "thinking", "processing", "accepted", "cancelled"};
  return names[static_cast<unsigned>(s)];
}
struct LineParser {
  char data[48]{}; size_t count=0; bool dropping=false;
  Command feed(char c) {
    if(c=='\n') {
      if(dropping) { dropping=false; count=0; return Command::None; }
      if(count && data[count-1]=='\r') --count;
      data[count]=0; count=0;
      if(!strcmp(data,"ping")) return Command::Ping;
      if(!strcmp(data,"layout")) return Command::Layout;
      for(unsigned i=0;i<6;i++) if(!strcmp(data,name(static_cast<State>(i)))) return static_cast<Command>(i);
      return Command::None;
    }
    if(dropping) return Command::None;
    if((static_cast<uint8_t>(c)<32 && c!='\r') || static_cast<uint8_t>(c)>126 || count>=sizeof(data)-1) {
      dropping=true; count=0; return Command::None;
    }
    data[count++]=c; return Command::None;
  }
};
struct StateMachine {
  State persistent=State::Idle, transient=State::Idle; bool momentary=false; uint32_t started=0;
  void receive(State s,uint32_t now) {
    if(s==State::Ask) {persistent=s;momentary=false;return;}
    if(s==State::Accepted || s==State::Cancelled) { transient=s; started=now; momentary=true; }
    else persistent=s;
  }
  State effective(uint32_t now) {
    if(momentary && uint32_t(now-started)>=900) momentary=false;
    return momentary?transient:persistent;
  }
};
enum class Press : uint8_t { None, Short, Long };
struct Button {
  bool candidate=false, stable=false, armed=true, active=false; uint32_t changed=0, down=0;
  void begin(bool pressed,uint32_t now) {
    candidate=stable=pressed; armed=!pressed; active=false; changed=down=now;
  }
  uint32_t heldFor(uint32_t now) const {return active?uint32_t(now-down):0;}
  Press update(bool pressed,uint32_t now) {
    if(pressed!=candidate) { candidate=pressed; changed=now; }
    if(stable==candidate || uint32_t(now-changed)<30) return Press::None;
    stable=candidate;
    if(stable) { if(armed) { active=true; down=now; } return Press::None; }
    armed=true;
    if(!active) return Press::None;
    active=false;
    return uint32_t(now-down)>=800?Press::Long:Press::Short;
  }
};
struct Blink {
  uint32_t next=3000, began=0, rng=0xC1A0DEU; bool shut=false;
  void begin(uint32_t now,uint32_t seed) { rng=seed?seed:0xC1A0DEU; next=now+2500; shut=false; }
  int height(uint32_t now) {
    if(!shut && int32_t(now-next)>=0) { shut=true; began=now; }
    if(shut && uint32_t(now-began)>=160) { shut=false; rng^=rng<<13; rng^=rng>>17; rng^=rng<<5; next=now+2600+rng%2200; }
    if(!shut) return 65;
    uint32_t elapsed=now-began;
    int h=elapsed<60?65-int(elapsed):elapsed<95?5:5+int(elapsed-95);
    return h>65?65:h;
  }
};
} // namespace pet
