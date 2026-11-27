#include <assert.h>
#include <iostream>
#include "controller.h"
using namespace tank;
struct HW:Hardware {uint16_t last[16]{};bool off=true,on=false;
 void gate(bool b)override{off=b;}void power(bool b)override{on=b;}
 bool initialize()override{return true;}bool frame(const uint16_t (&a)[16])override{for(unsigned i=0;i<16;i++)last[i]=a[i];return true;}
 bool healthy()override{return true;}bool save(const Calibration&)override{return true;}
};
int main(){
 static_assert(CASE_YAW_MIN==-30&&CASE_YAW_MAX==30,"Mock checked case range");
 HW h;Controller c(h);c.begin(0);c.link(true,0);for(auto& w:c.cal.wheels)w.calibrated=true;char reply[200];
 c.command("MOTOR ARM",400,reply,sizeof(reply));c.command("AUTO SCAN",400,reply,sizeof(reply));assert(std::string(reply)=="ACK AUTO SCAN");
 c.tick(450);c.tick(750);assert(c.heading()==-30&&c.mode==Mode::Scan);
 for(uint32_t now=800;now<4800;now+=50){c.command("MOTOR HEARTBEAT",now,reply,sizeof(reply));c.tick(now);for(unsigned i=0;i<6;i++)if(c.active())assert(h.last[i]==1500);}
 assert(!c.active()&&h.off&&!h.on&&c.heading()==0);
 c.command("MOTOR ARM",5000,reply,sizeof(reply));c.command("TURRET 31",5000,reply,sizeof(reply));assert(!c.active()&&h.off&&!h.on);
 std::cout<<"PASS scan (mock case limits only)\n";
}
