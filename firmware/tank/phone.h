#pragma once
// Phone control logic (release note 10). Pure C++: no WiFi/Arduino types, so the whole API is host-tested.
// Constants marked UNTESTED are engineering targets, not verified on hardware.
#include <stdio.h>
#include <string.h>
#include "controller.h"
#include "http_lite.h"
namespace tank {
constexpr uint32_t PHONE_LEASE_MS=500;      // UNTESTED: wheels stop 500 ms after the last move
constexpr uint32_t PHONE_IDLE_MS=5000;      // UNTESTED: session released when owner is silent this long
constexpr int PHONE_MAX_PCT=60;             // UNTESTED: 100% speed = 60% of calibrated pulse span
constexpr const char* const PHONE_SPEEDS[3]={"0.4","0.65","1"};
constexpr int PHONE_SPEED_PCT[3]={40,65,100};
struct NetIface {   // implemented on target by Wi-Fi glue, mocked on host. Never exposes passwords.
  virtual ~NetIface()=default;
  virtual int scan(char* json,size_t n)=0;                         // 0 running, 1 done (json filled), -1 failed
  virtual bool join(const char* ssid,const char* pass,const char*& err)=0;
  virtual void describe(char* out,size_t n)=0;                     // ssid + ip text only
  virtual unsigned clients()=0;
};
struct HttpReply {
  int code=200;const char* type="application/json; charset=utf-8";char body[900]{};bool page=false;
  void json(int c,const char* s){code=c;snprintf(body,sizeof(body),"%s",s);}
  void err(int c,const char* msg){code=c;snprintf(body,sizeof(body),"{\"error\":\"%s\"}",msg);}
};
class Phone {
  Controller& c;NetIface& net;uint32_t (*rnd)();
  uint32_t token=0,lastSeq=0,seen=0;bool haveSeq=false,assembly=false;uint8_t speed=1;int dir=0;
  Block lastBlock=Block::None;int lastSide=-1;
  static const char* blockMsg(Block b,int side) {
    const char* s=side==1?"sau":"trước";
    static char buf[2][96];static int k=0;char* o=buf[k^=1];
    switch(b){
      case Block::NoData:snprintf(o,96,"Chưa có dữ liệu sonar %s tin cậy",s);return o;
      case Block::Stale:snprintf(o,96,"Dữ liệu sonar %s đã cũ",s);return o;
      case Block::Blocked:snprintf(o,96,"Có vật cản phía %s",s);return o;
      case Block::Turret:return "Turret chưa ở giữa hoặc đang ổn định";
      default:return "";
    }
  }
  bool owns(const HttpRequest& q)const{uint32_t t;return token&&q.uintParam("token",t)&&t==token&&c.phoneUp();}
  void release(const char* why){if(token||c.phoneUp()){c.stop(why);c.phoneLink(false,0);}token=0;dir=0;assembly=false;haveSeq=false;}
  // Direction code (0 stop,1 fwd,2 back,3 left,4 right,5 fwd-left,6 fwd-right,7 back-left,8 back-right).
  static bool mix(int d,int pct,int& l,int& r) {
    int in=pct*40/100;  // inner wheels at 40% of outer on a diagonal arc
    switch(d){
      case 0:l=r=0;return true;       case 1:l=r=pct;return true;      case 2:l=r=-pct;return true;
      case 3:l=-pct;r=pct;return true; case 4:l=pct;r=-pct;return true;
      case 5:l=in;r=pct;return true;   case 6:l=pct;r=in;return true;
      case 7:l=-in;r=-pct;return true; case 8:l=-pct;r=-in;return true;
      default:return false;
    }
  }
  void status(const HttpRequest& q,uint32_t now,HttpReply& o) {
    uint32_t t=0;bool mine=q.uintParam("token",t)&&token&&t==token;
    if(mine)seen=now;
    char sf[24],sr[24];
    auto fmt=[&](unsigned n,char* b,size_t cap,bool& ok){const Range& r=c.ranges[n];ok=c.rangeBlock(n,now)==Block::None||(r.valid&&!elapsed(now,r.at,FRESH_MS)&&r.good>=2);
      if(ok)snprintf(b,cap,"%u",r.mm);else snprintf(b,cap,"-1");};
    bool fok,rok;fmt(0,sf,sizeof(sf),fok);fmt(1,sr,sizeof(sr),rok);
    char net_[96];net.describe(net_,sizeof(net_));
    const char* mode=assembly?"rap":(c.active()?(c.mode==Mode::Phone?"dien-thoai":c.mode==Mode::Auto?"tu-do":c.mode==Mode::Scan?"quet":"host"):"dung");
    char txt[300];
    snprintf(txt,sizeof(txt),"Chế độ: %s\\nSonar trước: %s\\nSonar sau: %s\\nĐèn: chưa nối\\n%s%s",mode,fok?sf:"không hợp lệ",rok?sr:"không hợp lệ",net_,mine?"":(token?"\\nĐiện thoại khác đang điều khiển":""));
    snprintf(o.body,sizeof(o.body),"{\"mode\":\"%s\",\"reason\":\"%s\",\"owner\":%s,\"locked\":%s,\"speed\":%s,\"front\":%s,\"rear\":%s,\"frontValid\":%s,\"rearValid\":%s,\"light\":\"chua-noi\",\"block\":\"%s\",\"text\":\"%s\"}",
      mode,c.reason,mine?"true":"false",assembly?"true":"false",PHONE_SPEEDS[speed],sf,sr,fok?"true":"false",rok?"true":"false",
      lastBlock!=Block::None?blockMsg(lastBlock,lastSide):"",txt);
  }
  void move(const HttpRequest& q,uint32_t now,HttpReply& o) {
    uint32_t sq,d,fresh;
    if(!q.uintParam("seq",sq)||!q.uintParam("dir",d)||!q.uintParam("fresh",fresh)||d>8||fresh>1){o.err(400,"Lệnh không hợp lệ");return;}
    if(!owns(q)){c.stop("session");o.err(409,"Phiên điều khiển đã đổi — mở lại trang");return;}
    // Stale or replayed sequence numbers never move or stop-and-restart anything.
    if(haveSeq&&int32_t(sq-lastSeq)<=0){o.err(409,"Lệnh cũ bị bỏ qua");return;}
    haveSeq=true;lastSeq=sq;seen=now;
    if(d==0){dir=0;c.stop("phone-release");o.json(200,"{\"ok\":true,\"moving\":false}");return;}
    if(assembly){c.stop("assembly");o.err(423,"Đang ở trang Ráp: lái bị khóa");return;}
    if(!fresh&&!(c.active()&&c.mode==Mode::Phone)){dir=0;o.err(409,"Lease đã hết — nhấn lại để chạy");return;}
    int l,r;mix(int(d),PHONE_SPEED_PCT[speed],l,r);
    int side=-1;Block b=Block::None;
    // While powering up the controller itself waits for a fresh echo (and times out); the guard runs on start and in Run.
    if(!(c.active()&&c.mode==Mode::Phone&&c.stage!=Stage::Run))b=c.driveBlock(l,r,now,side);
    if(b!=Block::None){
      if(c.active()&&c.mode==Mode::Phone)c.stop("sonar");
      dir=0;lastBlock=b;lastSide=side;
      snprintf(o.body,sizeof(o.body),"{\"error\":\"%s\",\"blocked\":true}",blockMsg(b,side));o.code=423;return;
    }
    lastBlock=Block::None;
    if(!c.phoneDrive(l,r,now,PHONE_LEASE_MS)){
      dir=0;const char* m=!strcmp(c.reason,"busy-source")?"Host hoặc chế độ tự động đang điều khiển — bấm DỪNG trước":!strcmp(c.reason,"sonar")?"Sonar chặn hướng này":"Xe chưa sẵn sàng (nút dừng, lỗi I2C hoặc đang ngủ)";
      o.err(409,m);return;
    }
    dir=int(d);o.json(200,"{\"ok\":true,\"moving\":true}");
  }
  bool cmd(const char* line,uint32_t now,char* rep,size_t n){return c.command(line,now,rep,n);}
  void cal(HttpReply& o) {
    char b[600];int k=snprintf(b,sizeof(b),"{\"neutral\":[");
    for(int i=0;i<6;i++)k+=snprintf(b+k,sizeof(b)-k,"%s%u",i?",":"",c.cal.wheels[i].neutral);
    k+=snprintf(b+k,sizeof(b)-k,"],\"span\":[");
    for(int i=0;i<6;i++)k+=snprintf(b+k,sizeof(b)-k,"%s%u",i?",":"",c.cal.wheels[i].span);
    k+=snprintf(b+k,sizeof(b)-k,"],\"direction\":[");
    for(int i=0;i<6;i++)k+=snprintf(b+k,sizeof(b)-k,"%s%d",i?",":"",c.cal.wheels[i].direction);
    k+=snprintf(b+k,sizeof(b)-k,"],\"calibrated\":[");
    for(int i=0;i<6;i++)k+=snprintf(b+k,sizeof(b)-k,"%s%s",i?",":"",c.cal.wheels[i].calibrated?"true":"false");
    snprintf(b+k,sizeof(b)-k,"],\"turretCenter\":%u,\"yawMin\":%d,\"yawMax\":%d}",c.cal.turretCenter,CASE_YAW_MIN,CASE_YAW_MAX);
    o.json(200,b);
  }
  void assemblyOnly(const HttpRequest& q,HttpReply& o,bool& ok){
    ok=false;if(!owns(q)){o.err(409,"Phiên điều khiển đã đổi — mở lại trang");return;}
    if(!assembly){o.err(423,"Chỉ dùng ở trang Ráp");return;}ok=true;
  }
  void handleAssembly(const HttpRequest& q,uint32_t now,HttpReply& o) {
    char rep[260]{},line[100];bool ok;
    if(!strcmp(q.path,"/api/cal")){cal(o);return;}
    assemblyOnly(q,o,ok);if(!ok)return;seen=now;
    uint32_t ch=0,d=0;char s[16];
    if(!strcmp(q.path,"/api/trim")) {
      char kind[4],delta[8];int dl=0;
      if(!q.uintParam("ch",ch)||ch>5||!q.param("kind",kind,sizeof(kind))||!q.param("delta",delta,sizeof(delta))){o.err(400,"Lệnh không hợp lệ");return;}
      dl=atoi(delta);Wheel w=c.cal.wheels[ch];
      if(kind[0]=='n'&&(dl==5||dl==-5))w.neutral=uint16_t(int(w.neutral)+dl);
      else if(kind[0]=='s'&&(dl==10||dl==-10))w.span=uint16_t(int(w.span)+dl);
      else if(kind[0]=='d')w.direction=int8_t(-w.direction);
      else {o.err(400,"Lệnh không hợp lệ");return;}
      snprintf(line,sizeof(line),"CAL SET %u %u %d %u",ch,w.neutral,w.direction,w.span);
      cmd(line,now,rep,sizeof(rep));
      if(strncmp(rep,"ACK",3)){o.err(409,"Giá trị ngoài giới hạn hoặc xe đang chạy");return;}
      o.json(200,"{\"ok\":true}");return;
    }
    if(!strcmp(q.path,"/api/turretcal")) {
      char delta[8];if(!q.param("delta",delta,sizeof(delta))){o.err(400,"Lệnh không hợp lệ");return;}
      int dl=atoi(delta);if(dl!=5&&dl!=-5){o.err(400,"Lệnh không hợp lệ");return;}
      snprintf(line,sizeof(line),"CAL TURRET %d %u",int(c.cal.turretCenter)+dl,c.cal.turretUsPerDegree);
      cmd(line,now,rep,sizeof(rep));if(strncmp(rep,"ACK",3)){o.err(409,"Giá trị ngoài giới hạn");return;}
      o.json(200,"{\"ok\":true}");return;
    }
    if(!strcmp(q.path,"/api/save")){cmd("CAL SAVE",now,rep,sizeof(rep));if(strncmp(rep,"ACK",3)){o.err(500,"Không lưu được hiệu chuẩn");return;}o.json(200,"{\"ok\":true}");return;}
    // Jog and turret need an armed controller and exactly one bounded command.
    if(!strcmp(q.path,"/api/jog")) {
      char dd[8];if(!q.uintParam("ch",ch)||ch>5||!q.param("d",dd,sizeof(dd))){o.err(400,"Lệnh không hợp lệ");return;}
      int dv=atoi(dd);if(dv<-1||dv>1){o.err(400,"Lệnh không hợp lệ");return;}
      if(c.active()){o.err(409,"Xe đang chạy");return;}
      if(!c.phoneArm(now)){o.err(409,"Xe chưa sẵn sàng");return;}
      snprintf(line,sizeof(line),"MOTOR TEST %u %s",ch,dv>0?"+":dv<0?"-":"0");
      cmd(line,now,rep,sizeof(rep));if(strncmp(rep,"ACK",3)){o.err(409,"Không thử được lúc này");return;}
      o.json(200,"{\"ok\":true}");return;
    }
    if(!strcmp(q.path,"/api/turret")) {
      if(!q.param("pos",s,sizeof(s))){o.err(400,"Lệnh không hợp lệ");return;}
      int a=!strcmp(s,"min")?CASE_YAW_MIN:!strcmp(s,"max")?CASE_YAW_MAX:!strcmp(s,"center")?0:999;
      if(a==999){o.err(400,"Lệnh không hợp lệ");return;}
      if(c.active()){o.err(409,"Xe đang chạy");return;}
      if(!c.phoneArm(now)){o.err(409,"Xe chưa sẵn sàng");return;}
      snprintf(line,sizeof(line),"TURRET %d",a);cmd(line,now,rep,sizeof(rep));
      if(strncmp(rep,"ACK",3)){o.err(409,"Turret bị khóa hoặc ngoài giới hạn");return;}
      o.json(200,"{\"ok\":true}");return;
    }
    (void)d;o.err(404,"Không có");
  }
public:
  Phone(Controller& ctl,NetIface& n,uint32_t (*r)()):c(ctl),net(n),rnd(r){}
  bool hasSession()const{return token!=0;}
  bool driving()const{return dir!=0&&c.active()&&c.mode==Mode::Phone;}
  bool locked()const{return assembly;}
  // Called every loop: session idle timeout and AP client loss.
  void tick(uint32_t now) {
    if(!token)return;
    if(net.clients()==0)release("ap-client-lost");
    else if(elapsed(now,seen,PHONE_IDLE_MS))release("session-idle");
  }
  void stopAll(const char* why){dir=0;c.stop(why);}
  void handle(const HttpRequest& q,uint32_t now,HttpReply& o) {
    const bool get=!strcmp(q.method,"GET")||!strcmp(q.method,"HEAD"),post=!strcmp(q.method,"POST");
    if(strncmp(q.path,"/api/",5)) {                       // every non-API path (captive probes too) serves the page
      if(!get){o.err(405,"Phương thức không hỗ trợ");return;}
      o.page=true;o.code=200;o.type="text/html; charset=utf-8";return;
    }
    if(!strcmp(q.path,"/api/status")&&get){status(q,now,o);return;}
    if(!strcmp(q.path,"/api/cal")&&get){handleAssembly(q,now,o);return;}
    if(!post){o.err(405,"Phương thức không hỗ trợ");return;}
    if(!strcmp(q.path,"/api/stop")){stopAll("phone-stop");dir=0;o.json(200,"{\"ok\":true}");return;}   // STOP needs no token and always wins
    if(!strcmp(q.path,"/api/session")) {
      uint32_t t;do{t=rnd()&0x7fffffff;}while(!t||t==token);
      if(c.mode==Mode::Phone)c.stop("session");c.phoneLink(true,now);token=t;seen=now;haveSeq=false;dir=0;assembly=false;
      snprintf(o.body,sizeof(o.body),"{\"token\":\"%u\"}",unsigned(t));return;
    }
    if(!strcmp(q.path,"/api/move")){move(q,now,o);return;}
    if(!strcmp(q.path,"/api/scan")){char b[700];int s=net.scan(b,sizeof(b));if(s==1)o.json(200,b);else if(s==0)o.json(200,"{\"busy\":true}");else o.err(500,"Không quét được Wi-Fi");return;}
    if(!strcmp(q.path,"/api/wifi")) {
      char ssid[40],pw[80]{};if(!q.param("ssid",ssid,sizeof(ssid))||!*ssid||strlen(ssid)>32){o.err(400,"Tên Wi-Fi không hợp lệ");return;}
      q.param("password",pw,sizeof(pw));size_t pl=strlen(pw);
      if(pl>63||(pl&&pl<8)){o.err(400,"Mật khẩu phải từ 8 đến 63 ký tự");return;}
      stopAll("wifi-setup");const char* e="";
      if(!net.join(ssid,pw,e)){o.err(409,*e?e:"Không kết nối được Wi-Fi nhà");return;}
      memset(pw,0,sizeof(pw));o.json(200,"{\"ok\":true}");return;
    }
    if(!owns(q)){o.err(409,"Phiên điều khiển đã đổi — mở lại trang");return;}
    seen=now;
    if(!strcmp(q.path,"/api/speed")){char v[8];if(!q.param("value",v,sizeof(v))){o.err(400,"Lệnh không hợp lệ");return;}
      for(unsigned i=0;i<3;i++)if(!strcmp(v,PHONE_SPEEDS[i])){stopAll("speed");speed=uint8_t(i);o.json(200,"{\"ok\":true}");return;}
      o.err(400,"Tốc độ không hợp lệ");return;}
    if(!strcmp(q.path,"/api/light")){o.err(409,"Đèn chưa nối — chưa có chân điều khiển");return;}
    if(!strcmp(q.path,"/api/assembly")){uint32_t a;if(!q.uintParam("active",a)||a>1){o.err(400,"Lệnh không hợp lệ");return;}
      stopAll("assembly");assembly=a==1;o.json(200,"{\"ok\":true}");return;}
    handleAssembly(q,now,o);
  }
};
}
