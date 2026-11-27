#pragma once
#include <stdint.h>
namespace tank {
// Nonblocking trigger/capture; opposite sensors alternate, >=60ms between any pings.
// IO supplies trigger(sensor, level), echo(sensor), takePulse(sensor, widthUs), clear(sensor).
template<class IO> class Sonars {
  IO& io;unsigned sensor=0;uint32_t at=0,last=0;int yaw=0;bool first=true;
  enum Phase {Quiet,Trigger,Wait} phase=Quiet;
public:
  explicit Sonars(IO& i):io(i){}
  bool triggering()const{return phase==Trigger;}
  template<class Sink> void tick(uint32_t us,uint32_t ms,int heading,Sink& sink) {
    if(phase==Quiet) {
      if(!first&&uint32_t(us-last)<60000)return;
      first=false;last=at=us;yaw=heading;io.clear(sensor);
      if(io.echo(sensor)){sink.sample(sensor,0,false,yaw,ms);sensor^=1;return;}
      io.trigger(sensor,true);phase=Trigger;return;
    }
    if(phase==Trigger){if(uint32_t(us-at)<12)return;io.trigger(sensor,false);phase=Wait;at=us;return;}
    uint32_t width=0;
    if(io.takePulse(sensor,width)){
      unsigned mm=unsigned((width*343u+1000u)/2000u);sink.sample(sensor,mm,width>=116&&width<=23324&&heading==yaw,yaw,ms);phase=Quiet;sensor^=1;
    }else if(uint32_t(us-at)>=25000){sink.sample(sensor,0,false,yaw,ms);phase=Quiet;sensor^=1;}
  }
};
}
