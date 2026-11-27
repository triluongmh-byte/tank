#pragma once
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pins.h"
#include "mechanical_limits.h"
namespace tank {
struct Wheel { uint16_t neutral=1500,span=100; int8_t direction=1; bool calibrated=false; Wheel()=default; Wheel(uint16_t n,uint16_t s,int8_t d,bool c):neutral(n),span(s),direction(d),calibrated(c){} };
struct Calibration {
  Wheel wheels[6]; uint16_t turretCenter=1500,turretUsPerDegree=6;
  Calibration() { for(unsigned i=3;i<6;i++) wheels[i].direction=-1; }
  bool valid() const {
    for(const auto& w:wheels) if(w.neutral<1300||w.neutral>1700||w.span<10||w.span>200||(w.direction!=1&&w.direction!=-1)) return false;
    return turretCenter>=1400&&turretCenter<=1600&&turretUsPerDegree>=4&&turretUsPerDegree<=8;
  }
  bool ready() const { for(const auto& w:wheels) if(!w.calibrated)return false;return valid(); }
};
struct Hardware {
  virtual ~Hardware()=default;
  virtual void gate(bool disabled)=0;
  virtual void power(bool enabled)=0;
  virtual bool initialize()=0;
  virtual bool frame(const uint16_t (&us)[16])=0;
  virtual bool healthy()=0;
  virtual bool save(const Calibration&)=0;
};
enum class Mode:uint8_t {Idle,Cue,Manual,Auto,Test,Turret,Scan,Phone};
enum class Block:uint8_t {None,NoData,Stale,Blocked,Turret};
enum class Stage:uint8_t {Off,PowerWait,CenterWait,Run,Neutral,Fault};
struct Range { unsigned mm=0; uint32_t at=0; bool valid=false; int yaw=0; unsigned good=0; Range()=default; Range(unsigned m,uint32_t t,bool v,int y):mm(m),at(t),valid(v),yaw(y){} };
inline bool elapsed(uint32_t now,uint32_t since,uint32_t duration){return uint32_t(now-since)>=duration;}
class Controller {
  Hardware& hw;
  uint16_t target[16]{};
  uint32_t startAt=0,runAt=0,duration=0,lastLink=0,lastProbe=0,stageAt=0,yawAt=0;
  bool connected=false,usb=false,phone=false,held=false,armed=false,sleeping=false;
  int left=0,right=0,yaw=0,testIndex=-1,scanIndex=0;
  uint32_t scanAt=0;
  void cut(Stage next,const char* why) {
    hw.gate(true);hw.power(false);stage=next;mode=Mode::Idle;armed=false;
    memset(target,0,sizeof(target));left=right=0;reason=why;
  }
  bool send(const uint16_t (&out)[16]) {if(hw.frame(out))return true;cut(Stage::Fault,"i2c");return false;}
  void neutral(uint16_t (&out)[16])const {
    memset(out,0,sizeof(out));for(unsigned i=0;i<6;i++)out[i]=cal.wheels[i].neutral;
    out[6]=uint16_t(int(cal.turretCenter)+yaw*int(cal.turretUsPerDegree));
  }
  void speeds(int l,int r) {
    left=l;right=r;
    for(unsigned i=0;i<6;i++)target[i]=uint16_t(int(cal.wheels[i].neutral)+(i<3?l:r)*int(cal.wheels[i].span)*cal.wheels[i].direction/100);
  }
  bool clear(unsigned n,uint32_t now)const {return ranges[n].valid&&ranges[n].good>=2&&ranges[n].yaw==0&&yaw==0&&elapsed(now,yawAt,TURRET_SETTLE_MS)&&!elapsed(now,ranges[n].at,FRESH_MS)&&ranges[n].mm>=CLEAR_MM;}
  bool guarded(int l,int r,uint32_t now)const {
    if(!l&&!r)return true;
    if(l>=0&&r>=0)return clear(0,now);
    if(l<=0&&r<=0)return clear(1,now);
    return clear(0,now)&&clear(1,now);
  }
  bool start(Mode requested,int l,int r,uint32_t ms,uint32_t now,int single=-1,int dir=0) {
    if(!armed||held||sleeping||!connected||stage==Stage::Fault){reason="inhibited";return false;}
    if(stage!=Stage::Off){reason="busy";return false;}
    if(requested!=Mode::Test && !cal.ready()){reason="calibration";return false;}
    if(requested!=Mode::Test && !guarded(l,r,now)){reason="sonar";return false;}
    mode=requested;testIndex=single;duration=ms;startAt=stageAt=lastLink=lastProbe=now;
    neutral(target);speeds(l,r);
    if(single>=0) {memset(target,0,sizeof(target));target[single]=uint16_t(int(cal.wheels[single].neutral)+dir*int(cal.wheels[single].span));}
    // Program neutral with power OFF and OE HIGH; command pulses are sent only after the wait.
    uint16_t safe[16]{};neutral(safe);
    if(!send(safe))return false;
    hw.power(true);stage=Stage::PowerWait;reason="running";return true;
  }
  static bool number(const char* s,int lo,int hi,int& out) {
    if(!s||!*s)return false;
    const char* p=s;if(*p=='-')p++;if(!*p)return false;
    for(;*p;p++)if(*p<'0'||*p>'9')return false;
    if(strlen(s)>7)return false;
    long v=strtol(s,nullptr,10);if(v<lo||v>hi)return false;out=int(v);return true;
  }
  bool invalid(char* reply,size_t n) {cut(Stage::Off,"command");snprintf(reply,n,"ERR MOTOR command");return true;}
public:
  Calibration cal;
  Range ranges[2];
  Mode mode=Mode::Idle;Stage stage=Stage::Off;const char* reason="boot";
  explicit Controller(Hardware& h):hw(h){}
  void begin(uint32_t now) {cut(Stage::Off,"boot");yawAt=now;if(!hw.initialize())cut(Stage::Fault,"i2c");}
  void link(bool up,uint32_t now){if(!up){cut(Stage::Off,"disconnect");}else if(!connected){lastLink=now;armed=false;}usb=up;connected=usb||phone;}
  // Phone (Wi-Fi) source: its own link flag; losing it cuts immediately. Never seizes an active host/auto mode.
  void phoneLink(bool up,uint32_t now){if(!up){if(phone)cut(Stage::Off,"phone-lost");}else if(!connected){lastLink=now;armed=false;}phone=up;connected=usb||phone;}
  bool phoneUp()const{return phone;}
  Block rangeBlock(unsigned n,uint32_t now)const {
    if(yaw!=0||!elapsed(now,yawAt,TURRET_SETTLE_MS))return Block::Turret;
    const Range& r=ranges[n];
    if(!r.valid||r.good<2||r.yaw!=0)return Block::NoData;
    if(elapsed(now,r.at,FRESH_MS))return Block::Stale;
    return r.mm<CLEAR_MM?Block::Blocked:Block::None;
  }
  // side: 0 front, 1 rear, -1 nothing needed (stop).
  Block driveBlock(int l,int r,uint32_t now,int& side)const {
    side=-1;if(!l&&!r)return Block::None;
    if(l>=0&&r>=0){side=0;return rangeBlock(0,now);}
    if(l<=0&&r<=0){side=1;return rangeBlock(1,now);}
    Block f=rangeBlock(0,now);if(f!=Block::None){side=0;return f;}
    side=1;return rangeBlock(1,now);
  }
  // Hold-to-drive from the phone. Each call renews a short lease; nothing else keeps wheels moving.
  bool phoneDrive(int l,int r,uint32_t now,uint32_t lease) {
    if(!phone){reason="phone-link";return false;}
    if(active()) {
      if(mode!=Mode::Phone){reason="busy-source";return false;}
      if(held||sleeping){stop("inhibit");return false;}
      if(stage==Stage::Run&&!guarded(l,r,now)){stop("sonar");return false;}
      speeds(l,r);lastLink=startAt=now;
      if(stage==Stage::Run){runAt=now;duration=lease;if(!send(target))return false;}
      return true;
    }
    if(stage==Stage::Fault||held||sleeping){reason="inhibited";return false;}
    hw.gate(true);hw.power(false);
    if(!hw.initialize()){cut(Stage::Fault,"i2c");return false;}
    stage=Stage::Off;armed=true;lastLink=now;
    if(!start(Mode::Phone,l,r,lease,now)){stop(reason);return false;}
    return true;
  }
  // Assembly jog/turret use the validated command path; true only if the command was accepted.
  bool phoneArm(uint32_t now) {
    if(!phone||held||sleeping||active()||stage==Stage::Fault)return false;
    hw.gate(true);hw.power(false);if(!hw.initialize()){cut(Stage::Fault,"i2c");return false;}
    stage=Stage::Off;armed=true;lastLink=now;reason="armed";return true;
  }
  void stop(const char* why="stop"){cut(stage==Stage::Fault?Stage::Fault:Stage::Off,why);}
  void button(bool down){held=down;if(down)stop("button");}
  void sleep(bool value){sleeping=value;if(value)stop("sleep");}
  bool active()const{return stage==Stage::PowerWait||stage==Stage::CenterWait||stage==Stage::Run||stage==Stage::Neutral;}
  int heading()const{return yaw;}
  bool isArmed()const{return armed;}
  uint32_t watchdogBudget(uint32_t now)const {return active()?(elapsed(now,lastLink,LINK_MS)?0:LINK_MS-uint32_t(now-lastLink)):0;}
  void sample(unsigned index,unsigned mm,bool valid,int heading,uint32_t now) {
    if(index>1)return;
    bool accepted=valid&&mm>=20&&mm<=4000&&elapsed(now,yawAt,TURRET_SETTLE_MS);
    unsigned good=accepted?(ranges[index].valid&&ranges[index].yaw==heading?ranges[index].good+1:1):0;
    ranges[index]={mm,now,accepted,heading};ranges[index].good=good>2?2:good;
  }
  void tick(uint32_t now) {
    if(!active())return;
    if(held||sleeping||!connected){stop("inhibit");return;}
    if(elapsed(now,lastLink,LINK_MS)){stop("link-timeout");return;}
    if(elapsed(now,startAt,10000)){stop("max-lease");return;}
    if(elapsed(now,lastProbe,100)){lastProbe=now;if(!hw.healthy()){cut(Stage::Fault,"i2c");return;}}
    if(stage==Stage::PowerWait && elapsed(now,stageAt,POWER_SETTLE_MS)) {
      if(mode==Mode::Test){if(!send(target))return;hw.gate(false);stage=Stage::Run;stageAt=runAt=now;}
      else {
        uint16_t safe[16]{};neutral(safe);if(!send(safe))return;
        hw.gate(false);stage=Stage::CenterWait;stageAt=yawAt=now;
        ranges[0].valid=ranges[1].valid=false;
      }
    }
    if(stage==Stage::CenterWait && elapsed(now,stageAt,TURRET_SETTLE_MS)) {
      // Wheel motion waits for a powered, settled turret and a new on-axis echo.
      bool ready=(mode==Mode::Turret)||(mode==Mode::Scan)||guarded(left,right,now);
      if(mode==Mode::Auto)ready=clear(0,now);
      if(ready){if(!send(target))return;stage=Stage::Run;stageAt=runAt=scanAt=now;}
      else if(elapsed(now,stageAt,TURRET_SETTLE_MS+500)){stop("sonar");return;}
    }
    if(stage==Stage::Run) {
      if(mode==Mode::Scan && elapsed(now,scanAt,1000)) {
        if(++scanIndex>=4){stop("scan-done");return;}
        const int angles[4]={CASE_YAW_MIN,0,CASE_YAW_MAX,0};yaw=angles[scanIndex];yawAt=scanAt=now;
        ranges[0].valid=ranges[1].valid=false;target[6]=uint16_t(int(cal.turretCenter)+yaw*int(cal.turretUsPerDegree));
        if(!send(target))return;
      }
      if(mode==Mode::Auto){
        if(!clear(0,now)){stop("sonar");return;}
        int speed=25; // Unknown, stale or blocked cuts power. Fresh command is required.
        if(speed!=left){speeds(speed,speed);if(!send(target))return;}
      } else if(mode!=Mode::Test && !guarded(left,right,now)){stop("sonar");return;}
      if(elapsed(now,runAt,duration)) {
        uint16_t safe[16]{};if(mode==Mode::Test&&testIndex>=0)safe[testIndex]=cal.wheels[testIndex].neutral;else neutral(safe);if(!send(safe))return;
        stage=Stage::Neutral;stageAt=now;left=right=0;
      }
    } else if(stage==Stage::Neutral && elapsed(now,stageAt,NEUTRAL_MS))stop("deadline");
  }
  // Called with a complete validated printable ASCII line; true means motion-family reply.
  bool command(const char* line,uint32_t now,char* reply,size_t n) {
    if(!strcmp(line,"SONAR STATUS")){snprintf(reply,n,"SONAR F=%u,%u,%d R=%u,%u,%d yaw=%d",ranges[0].mm,unsigned(ranges[0].valid&&!elapsed(now,ranges[0].at,FRESH_MS)),ranges[0].yaw,ranges[1].mm,unsigned(ranges[1].valid&&!elapsed(now,ranges[1].at,FRESH_MS)),ranges[1].yaw,yaw);return true;}
    char copy[160];if(strlen(line)>=sizeof(copy))return invalid(reply,n);
    strcpy(copy,line);char* words[9]{};unsigned count=0;char* save=nullptr;
    for(char* p=strtok_r(copy," ",&save);p;p=strtok_r(nullptr," ",&save)){if(count==9)return invalid(reply,n);words[count++]=p;}
    if(!count)return false;
    if(strcmp(words[0],"MOTOR")&&strcmp(words[0],"AUTO")&&strcmp(words[0],"TURRET")&&strcmp(words[0],"CAL"))return false;
    if(!strcmp(line,"MOTOR CAPS")){snprintf(reply,n,"MOTOR CAPS tank-v1 channels=7 heartbeat=200ms calibration=required sonar=required hw=untested");return true;}
    if(!strcmp(line,"MOTOR STATUS")){snprintf(reply,n,"MOTOR %s mode=%u armed=%u yaw=%d reason=%s",stage==Stage::Fault?"FAULT":active()?"RUN":"OFF",unsigned(mode),unsigned(armed),yaw,reason);return true;}
    if(!strcmp(line,"MOTOR STOP")||!strcmp(line,"AUTO OFF")){stop();snprintf(reply,n,"ACK MOTOR STOP");return true;}
    if(!strcmp(line,"MOTOR HEARTBEAT")){lastLink=now;snprintf(reply,n,"ACK MOTOR HEARTBEAT");return true;}
    if(!strcmp(line,"MOTOR ARM")) {
      if(held||sleeping||!connected||active()){snprintf(reply,n,"ERR MOTOR inhibited");return true;}
      hw.gate(true);hw.power(false);
      if(!hw.initialize()){cut(Stage::Fault,"i2c");snprintf(reply,n,"ERR MOTOR i2c");return true;}
      stage=Stage::Off;armed=true;lastLink=now;reason="armed";snprintf(reply,n,"ACK MOTOR ARM");return true;
    }
    if(!strcmp(words[0],"CAL")) {
      if(active()||held||sleeping)return invalid(reply,n);
      if(count==2&&!strcmp(words[1],"GET")){snprintf(reply,n,"CAL ready=%u neutral=%u,%u,%u,%u,%u,%u direction=%d,%d,%d,%d,%d,%d",unsigned(cal.ready()),cal.wheels[0].neutral,cal.wheels[1].neutral,cal.wheels[2].neutral,cal.wheels[3].neutral,cal.wheels[4].neutral,cal.wheels[5].neutral,cal.wheels[0].direction,cal.wheels[1].direction,cal.wheels[2].direction,cal.wheels[3].direction,cal.wheels[4].direction,cal.wheels[5].direction);return true;}
      if(count==2&&!strcmp(words[1],"SAVE")){stop("calibration");snprintf(reply,n,hw.save(cal)?"ACK CAL SAVE":"ERR CAL storage");return true;}
      int i=0,us=0,d=0,span=0;
      if(count==6&&!strcmp(words[1],"SET")&&number(words[2],0,5,i)&&number(words[3],1300,1700,us)&&number(words[4],-1,1,d)&&d&&number(words[5],10,200,span)) {
        stop("calibration");cal.wheels[i]={uint16_t(us),uint16_t(span),int8_t(d),true};snprintf(reply,n,"ACK CAL SET %d",i);return true;
      }
      if(count==4&&!strcmp(words[1],"TURRET")&&number(words[2],1400,1600,us)&&number(words[3],4,8,span)){stop("calibration");cal.turretCenter=us;cal.turretUsPerDegree=span;snprintf(reply,n,"ACK CAL TURRET");return true;}
      return invalid(reply,n);
    }
    bool ok=false;const char* ack=nullptr;
    if(count==3&&!strcmp(words[0],"MOTOR")&&!strcmp(words[1],"DRIVE")&&(!strcmp(words[2],"FWD")||!strcmp(words[2],"BACK"))) {
      int s=!strcmp(words[2],"FWD")?30:-30;ok=start(Mode::Manual,s,s,2000,now);ack=s>0?"ACK MOTOR DRIVE FWD 2000ms":"ACK MOTOR DRIVE BACK 2000ms";
    } else if((count==4||count==5)&&!strcmp(words[0],"MOTOR")&&!strcmp(words[1],"TEST")) {
      int i=0,d=0;
      if(!strcmp(words[2],"L"))i=0;else if(!strcmp(words[2],"R"))i=3;else if(!number(words[2],0,5,i))return invalid(reply,n);
      if(!strcmp(words[3],"+"))d=1;else if(!strcmp(words[3],"-"))d=-1;else if(strcmp(words[3],"0"))return invalid(reply,n);
      if(count==5&&strcmp(words[4],"2000ms"))return invalid(reply,n);
      ok=start(Mode::Test,0,0,count==5?2000:100,now,i,d);ack="ACK MOTOR TEST";
    } else if(count==3&&!strcmp(words[0],"MOTOR")&&!strcmp(words[1],"CUE")) {
      int l=30,r=30;unsigned ms=540;
      if(!strcmp(words[2],"WORK")){l=r=-30;ms=1050;}
      else if(!strcmp(words[2],"DONE"))ms=1350;
      else if(!strcmp(words[2],"BACK"))l=r=-30;
      else if(!strcmp(words[2],"LEFT")){l=-30;r=30;}
      else if(!strcmp(words[2],"RIGHT")){l=30;r=-30;}
      else if(strcmp(words[2],"FWD"))return invalid(reply,n);
      ok=start(Mode::Cue,l,r,ms,now);
      if(ok){snprintf(reply,n,"ACK MOTOR CUE %s %ums",words[2],ms);return true;}ack="ACK MOTOR CUE";
    } else if(count==2&&!strcmp(words[0],"AUTO")&&!strcmp(words[1],"SCAN")) {
      if(CASE_YAW_MIN>=0||CASE_YAW_MAX<=0){stop("case-range");snprintf(reply,n,"ERR MOTOR case-range");return true;}
      if(active()){stop("mode-change");snprintf(reply,n,"ERR MOTOR inhibited");return true;}
      int old=yaw;scanIndex=0;yaw=CASE_YAW_MIN;yawAt=now;ranges[0].valid=ranges[1].valid=false;
      ok=start(Mode::Scan,0,0,5000,now);if(!ok)yaw=old;ack="ACK AUTO SCAN";
    } else if(count==2&&!strcmp(words[0],"AUTO")&&!strcmp(words[1],"ON")) {
      if(yaw){reason="turret";ok=false;}else ok=start(Mode::Auto,0,0,9000,now);ack="ACK AUTO ON";
    } else if(count==2&&!strcmp(words[0],"TURRET")) {
      int angle=0;if(!number(words[1],CASE_YAW_MIN,CASE_YAW_MAX,angle))return invalid(reply,n);
      // Any turret command stops the wheels first. No non-center drive is permitted.
      if(active())stop("turret");
      int old=yaw;yaw=angle;yawAt=now;ranges[0].valid=ranges[1].valid=false;
      ok=start(Mode::Turret,0,0,1000,now);if(!ok)yaw=old;ack="ACK TURRET";
    } else return invalid(reply,n);
    if(!ok&&!active())stop(reason);
    snprintf(reply,n,ok?"%s":"ERR MOTOR %s",ok?ack:reason);
    if(ok&&count==3&&!strcmp(words[1],"CUE"))snprintf(reply,n,"ACK MOTOR CUE %s %ums",words[2],unsigned(duration));
    if(ok&&(count==4||count==5)&&!strcmp(words[1],"TEST"))snprintf(reply,n,"ACK MOTOR TEST %s %s %ums",words[2],words[3],unsigned(duration));
    return true;
  }
};
// One bounded framing layer rejects truncation, controls and partial motion lines.
struct MotionParser {
  char line[600]{};unsigned used=0;bool bad=false;
  bool feed(char c,Controller& controller,uint32_t now,char* reply,size_t size) {
    if(c!='\n') {
      if((uint8_t(c)<32&&c!='\r')||uint8_t(c)>126||used>=sizeof(line)-1)bad=true;
      else if(!bad)line[used++]=c;
      return false;
    }
    if(used&&line[used-1]=='\r')used--;line[used]=0;used=0;
    if(bad){bad=false;controller.stop("parser");snprintf(reply,size,"ERR MOTOR framing");return true;}
    if(strlen(line)>150&&strncmp(line,"MOTOR",5)&&strncmp(line,"AUTO",4)&&strncmp(line,"CAL",3)&&strncmp(line,"TURRET",6))return false;
    return controller.command(line,now,reply,size);
  }
};
}
