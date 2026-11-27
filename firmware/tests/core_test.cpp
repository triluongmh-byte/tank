#include <assert.h>
#include <array>
#include <algorithm>
#include <string>
#include <vector>
#include <iostream>
#include "controller.h"
#include "pca9685.h"
#include "calibration_store.h"
#include "sonar.h"
using namespace tank;
struct Mock:Hardware {
 bool off=true,on=false,ok=true;std::vector<std::string> events;std::array<uint16_t,16> latest{};
 void gate(bool b)override{off=b;events.push_back(b?"disable":"enable");}
 void power(bool b)override{on=b;events.push_back(b?"power-on":"power-off");}
 bool initialize()override{assert(off&&!on);events.push_back("init");return ok;}
 bool frame(const uint16_t (&us)[16])override{for(unsigned i=0;i<16;i++)latest[i]=us[i];events.push_back("frame");for(unsigned i=7;i<16;i++)assert(us[i]==0);return ok;}
 bool healthy()override{return ok;}
 bool save(const Calibration& c)override{return c.valid();}
};
struct Rig {
 Mock hw;Controller c{hw};char out[300]{};
 Rig(){c.begin(0);c.link(true,0);for(auto& w:c.cal.wheels)w.calibrated=true;}
 std::string cmd(const char* line,uint32_t at=400){c.command(line,at,out,sizeof(out));return out;}
 void arm(uint32_t now=400){assert(cmd("MOTOR ARM",now)=="ACK MOTOR ARM");}
 void range(uint32_t now=400){for(unsigned i=0;i<2;i++){c.sample(0,1000,true,0,now);c.sample(1,1000,true,0,now);}}
 void running(uint32_t now=400){arm(now);range(now);assert(cmd("MOTOR DRIVE FWD",now).find("ACK")==0);c.tick(now+50);assert(c.stage==Stage::CenterWait);range(now+350);c.tick(now+350);assert(c.stage==Stage::Run);}
 void off(){assert(!hw.on&&hw.off&&!c.active()&&!c.isArmed());}
};
static void safety(){
 Rig r;r.off();r.running();assert(r.hw.latest[0]==1530&&r.hw.latest[3]==1470&&r.hw.latest[6]==1500);
 const auto& e=r.hw.events;auto power=std::find(e.begin(),e.end(),"power-on"),enable=std::find(e.begin(),e.end(),"enable");assert(power<enable&&*(power-1)=="frame");
 r.c.stop();r.off();assert(r.cmd("MOTOR DRIVE FWD").find("ERR")==0);r.off();
 r.c.button(true);assert(r.cmd("MOTOR ARM")=="ERR MOTOR inhibited");r.off();r.c.button(false);assert(r.cmd("MOTOR DRIVE FWD").find("ERR")==0);
 r.running(800);r.c.button(true);r.off();r.c.button(false);r.off();
 r.running(1200);r.c.link(false,1300);r.off();r.c.link(true,1400);r.off();
 r.running(1600);r.c.sleep(true);r.off();assert(r.cmd("MOTOR ARM",1700).find("ERR")==0);r.c.sleep(false);r.off();
 r.running(2000);r.hw.ok=false;r.c.tick(2100);assert(r.c.stage==Stage::Fault);r.off();assert(r.cmd("MOTOR ARM",2200)=="ERR MOTOR i2c");
 r.hw.ok=true;r.running(2400);r.hw.ok=false;r.c.sample(0,10,true,0,2455);r.c.tick(2455);r.off();
 // Failure while neutral is programmed must never power the load.
 Rig f;f.arm();f.range();f.hw.ok=false;assert(f.cmd("MOTOR DRIVE FWD").find("ERR")==0);f.off();assert(std::find(f.hw.events.begin(),f.hw.events.end(),"power-on")==f.hw.events.end());
 // Stale data during power ramp never enables PWM.
 Rig s;s.arm();s.range();s.cmd("MOTOR DRIVE FWD");s.c.tick(450);assert(s.hw.latest[0]==1500);s.c.tick(1250);s.off();
}
static void timing(){
 Rig r;r.running();r.c.tick(1150);r.off();assert(std::string(r.c.reason)=="link-timeout");
 Rig d;d.arm();assert(d.cmd("MOTOR TEST 5 + 2000ms").find("ACK")==0);d.c.tick(450);
 for(uint32_t t=500;t<=2500;t+=100){d.cmd("MOTOR HEARTBEAT",t);d.c.tick(t);}
 assert(d.c.stage==Stage::Neutral);for(unsigned i=0;i<16;i++)assert(d.hw.latest[i]==(i==5?1500:0));d.c.tick(2540);d.off();
 // Uint32 millis rollover maintains lease and deadline behavior.
 Rig w;uint32_t t=0xFFFFFF00u;w.c.begin(t-400);w.arm(t);w.range(t);assert(w.cmd("MOTOR DRIVE FWD",t).find("ACK")==0);w.c.tick(t+50);w.cmd("MOTOR HEARTBEAT",t+600);w.range(t+600);w.c.tick(t+600);assert(w.c.active());w.c.tick(t+1400);w.off();
}
static void parsing(){
 Rig r;MotionParser p;auto feed=[&](const std::string& s){bool reply=false;for(char c:s)reply=p.feed(c,r.c,400,r.out,sizeof(r.out))||reply;return reply;};
 r.running();assert(feed("MOTOR DRIVE FWD junk\n"));r.off();
 const char* bad[]={"MOTOR TEST 6 +\n","MOTOR TEST 1 + 200000ms\n","CAL SET 0 999999999 1 50\n","TURRET -71\n","TURRET 71\n","AUTO MAYBE\n","MOTOR\n","MOTOR DRIVE FWD\rX\n"};
 for(auto s:bad){r.arm();assert(feed(s));assert(std::string(r.out).find("ERR")==0);r.off();}
 r.running(400);assert(feed(std::string(700,'X')+"\n"));r.off();
 r.running(400);assert(feed(std::string("MOTOR TEST 1 +")+char(0)+"\n"));r.off();
 assert(feed("MOTOR CAPS\r\n"));assert(std::string(r.out).find("tank-v1")!=std::string::npos);
 assert(!feed("TITLE "+std::string(320,'4')+"\n"));
 assert(!feed("MOTOR DRIVE"));r.off();assert(feed("\n"));r.off();
 // Deterministic hostile-byte framing, with output range and off-state invariants.
 uint32_t seed=7;for(unsigned k=0;k<3000;k++){r.arm();for(unsigned i=0;i<100;i++){seed=seed*1664525u+1013904223u;p.feed(char(seed>>24),r.c,400,r.out,sizeof(r.out));}p.feed('\n',r.c,400,r.out,sizeof(r.out));assert(!r.hw.on&&r.hw.off);}
}
static void mapping(){
 for(int i=0;i<6;i++){Rig r;r.arm();std::string cmd="MOTOR TEST "+std::to_string(i)+" +";assert(r.cmd(cmd.c_str()).find("ACK")==0);r.c.tick(450);for(unsigned j=0;j<16;j++)assert(r.hw.latest[j]==(j==unsigned(i)?1600:0));}
 Rig r;for(auto& w:r.c.cal.wheels)w.calibrated=false;r.arm();r.range();assert(r.cmd("MOTOR DRIVE FWD")=="ERR MOTOR calibration");r.off();
 for(unsigned i=0;i<6;i++){std::string cmd="CAL SET "+std::to_string(i)+" 1510 "+(i<3?"1":"-1")+" 90";assert(r.cmd(cmd.c_str()).find("ACK")==0);}
 r.arm();r.range();assert(r.cmd("MOTOR DRIVE FWD").find("ACK")==0);r.c.tick(450);r.range(750);r.c.tick(750);assert(r.hw.latest[0]==1537&&r.hw.latest[3]==1483);r.c.stop();
 r.arm();assert(r.cmd("TURRET 0")=="ACK TURRET");r.c.tick(450);assert(r.hw.latest[6]==1500);r.c.stop();
}
static void arbitration(){
 Rig r;r.running();assert(r.cmd("AUTO ON",460)=="ERR MOTOR busy");assert(r.c.mode==Mode::Manual);r.c.stop();
 r.arm();r.range();assert(r.cmd("AUTO ON")=="ACK AUTO ON");r.c.tick(450);r.range(750);r.c.tick(750);assert(r.c.mode==Mode::Auto&&r.hw.latest[0]==1525);
 r.c.sample(0,100,false,0,760);r.c.tick(760);r.off(); // unknown cuts power, no automatic restart
 r.arm(800);r.range(800);assert(r.cmd("AUTO ON",800)=="ACK AUTO ON");r.c.tick(850);r.range(1150);r.c.tick(1150);assert(r.c.active());r.c.tick(1401);r.off(); // stale cuts power
 r.arm(1500);r.range(1500);assert(r.cmd("AUTO ON",1500)=="ACK AUTO ON");r.c.tick(1550);r.range(1850);r.c.tick(1850);
 assert(r.cmd("TURRET 0",1860)=="ERR MOTOR inhibited");r.off(); // stop prior source, fresh arm required

}
struct Bus {uint8_t regs[256]{};bool ok=true;unsigned waited=0;
 bool write(uint8_t r,const uint8_t* data,unsigned n){if(!ok)return false;for(unsigned i=0;i<n;i++){regs[r+i]=data[i];if(r+i>=0xFA&&r+i<=0xFD)for(unsigned ch=0;ch<16;ch++)regs[6+4*ch+(r+i-0xFA)]=data[i];}return true;}
 bool read(uint8_t r,uint8_t* data,unsigned n){if(!ok)return false;memcpy(data,regs+r,n);return true;}
 void waitUs(unsigned n){waited+=n;}
};
static void registers(){
 Bus b;Pca9685<Bus> p(b);assert(p.begin());assert(b.waited>=500&&b.regs[0xFE]==121&&b.regs[1]==4);
 for(unsigned ch=0;ch<16;ch++)assert(b.regs[6+4*ch+3]==16);
 uint16_t frame[16]{};for(unsigned i=0;i<7;i++)frame[i]=1500;assert(p.frame(frame));
 for(unsigned ch=0;ch<7;ch++){assert(b.regs[6+4*ch]==0);assert((b.regs[8+4*ch]|(b.regs[9+4*ch]<<8))==307);}
 for(unsigned ch=7;ch<16;ch++)assert(b.regs[9+4*ch]==16);
 b.regs[0xFE]=100;assert(!p.healthy());b.ok=false;assert(!p.frame(frame));
}
static void storage(){Calibration c,d;for(unsigned i=0;i<6;i++){c.wheels[i].neutral=1400+i*20;c.wheels[i].calibrated=true;}uint8_t bytes[CAL_SIZE]{};encode(c,bytes);assert(decode(bytes,d)&&d.ready());assert(d.wheels[5].neutral==1500&&d.wheels[5].direction==-1);
 for(unsigned i=0;i<CAL_SIZE;i++){bytes[i]^=1;assert(!decode(bytes,d));bytes[i]^=1;}
 c.wheels[0].direction=0;encode(c,bytes);assert(!decode(bytes,d));}
struct Echo {bool high[2]{},pulse=false;uint32_t width=0;std::vector<unsigned> triggers;
 void trigger(unsigned i,bool b){high[i]=b;if(b)triggers.push_back(i);}
 bool echo(unsigned){return false;}
 bool takePulse(unsigned,uint32_t& w){if(!pulse)return false;pulse=false;w=width;return true;}
 void clear(unsigned){}
};
struct Sink {unsigned count=0,index=9,mm=0;bool valid=false;int yaw=0;void sample(unsigned i,unsigned d,bool v,int h,uint32_t){index=i;mm=d;valid=v;yaw=h;count++;}};
static void sonar(){Echo e;Sonars<Echo> s(e);Sink sink;
 s.tick(0,0,0,sink);assert(e.high[0]);s.tick(11,0,0,sink);assert(e.high[0]);s.tick(12,0,0,sink);assert(!e.high[0]);
 e.width=5800;e.pulse=true;s.tick(6000,6,0,sink);assert(sink.valid&&sink.mm==995&&sink.index==0);
 s.tick(59999,59,0,sink);assert(e.triggers.size()==1);s.tick(60000,60,0,sink);assert(e.high[1]);s.tick(60012,60,0,sink);s.tick(85012,85,0,sink);assert(!sink.valid&&sink.index==1);
 s.tick(120000,120,0,sink);s.tick(120012,120,0,sink);e.width=5800;e.pulse=true;s.tick(126000,126,20,sink);assert(!sink.valid);
}
int main(int argc,char** argv){std::string group=argc>1?argv[1]:"all";if(group=="all"||group=="safety"){safety();timing();arbitration();}if(group=="all"||group=="parser")parsing();if(group=="all"||group=="io"){mapping();registers();storage();sonar();}std::cout<<"PASS "<<group<<"\n";}
