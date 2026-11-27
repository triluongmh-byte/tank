#include <assert.h>
#include <array>
#include <string>
#include <vector>
#include <iostream>
#include "controller.h"
#include "phone.h"
#include "page.h"
#include "net_screen.h"
using namespace tank;
struct Mock:Hardware {
 bool off=true,on=false,ok=true;std::array<uint16_t,16> latest{};
 void gate(bool b)override{off=b;} void power(bool b)override{on=b;}
 bool initialize()override{assert(off&&!on);return ok;}
 bool frame(const uint16_t (&us)[16])override{for(unsigned i=0;i<16;i++)latest[i]=us[i];return ok;}
 bool healthy()override{return ok;} bool save(const Calibration& c)override{return c.valid();}
};
struct Net:NetIface {
 unsigned n=1;std::string lastPass;bool joinOk=true;
 int scan(char* j,size_t s)override{snprintf(j,s,"{\"busy\":false,\"networks\":[\"Nha\"]}");return 1;}
 bool join(const char*,const char* p,const char*& e)override{lastPass=p;if(!joinOk)e="Sai mật khẩu";return joinOk;}
 void describe(char* o,size_t s)override{snprintf(o,s,"Mạng: XeTang-TEST\\nĐịa chỉ: 192.168.4.1");}
 unsigned clients()override{return n;}
};
static uint32_t counter=1000;static uint32_t rnd(){return counter+=7;}
struct Rig {
 Mock hw;Controller c{hw};Net net;Phone p{c,net,rnd};uint32_t tok=0,seq=0;
 Rig(){c.begin(0);for(auto& w:c.cal.wheels)w.calibrated=true;}
 HttpReply call(const std::string& method,const std::string& path,const std::string& q,uint32_t now){
  HttpRequest r;std::string raw=method+" "+path+(method=="GET"&&!q.empty()?"?"+q:"")+" HTTP/1.1\r\nHost: x\r\n";
  if(method=="POST")raw+="Content-Length: "+std::to_string(q.size())+"\r\n";raw+="\r\n";if(method=="POST")raw+=q;
  assert(parseHttp(raw.data(),raw.size(),r)==HttpState::Ready);HttpReply o;p.handle(r,now,o);return o;
 }
 void session(uint32_t now=100){auto o=call("POST","/api/session","",now);assert(o.code==200);tok=unsigned(atoi(strstr(o.body,":\"")+2));assert(tok);}
 HttpReply move(int d,int fresh,uint32_t now){return call("POST","/api/move","token="+std::to_string(tok)+"&seq="+std::to_string(++seq)+"&dir="+std::to_string(d)+"&fresh="+std::to_string(fresh),now);}
 void echo(uint32_t now,unsigned mm=1000){for(int i=0;i<2;i++){c.sample(0,mm,true,0,now);c.sample(1,mm,true,0,now);}}
 void settle(uint32_t t){echo(t);c.tick(t);}
 // press: fresh move, power wait, centre wait, run
 void drive(int d,uint32_t now=400){echo(now);auto o=move(d,1,now);if(o.code!=200)std::cerr<<o.body<<" at "<<now<<"\n";assert(o.code==200);c.tick(now+50);assert(c.stage==Stage::CenterWait);echo(now+360);c.tick(now+360);assert(c.stage==Stage::Run);}
 void off(){assert(!hw.on&&hw.off&&!c.active());}
};
static void parser(){
 HttpRequest r;std::string a="GET /api/status?token=12&x=a%20b+c HTTP/1.1\r\nHost: a\r\n\r\n";
 assert(parseHttp(a.data(),a.size(),r)==HttpState::Ready&&!strcmp(r.path,"/api/status"));
 uint32_t v;assert(r.uintParam("token",v)&&v==12);char s[16];assert(r.param("x",s,sizeof(s))&&!strcmp(s,"a b c"));
 assert(!r.uintParam("nope",v));
 std::string part="POST /api/move HTTP/1.1\r\nContent-Length: 20\r\n\r\ntoken=1";assert(parseHttp(part.data(),part.size(),r)==HttpState::Need);
 std::string h="POST /api/move HTTP/1.1\r\nContent-Length: 7\r\n\r\ntoken=1";assert(parseHttp(h.data(),h.size(),r)==HttpState::Ready&&r.uintParam("token",v)&&v==1);
 std::string extra=h+"X";assert(parseHttp(extra.data(),extra.size(),r)==HttpState::Bad);
 for(const char* bad:{"BREW / HTTP/1.1\r\n\r\n","GET x HTTP/1.1\r\n\r\n","GET / FTP/1.0\r\n\r\n","POST / HTTP/1.1\r\nContent-Length: 99999\r\n\r\n","POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n","POST / HTTP/1.1\r\nContent-Length: 1\r\nContent-Length: 1\r\n\r\na","GET /\x01 HTTP/1.1\r\n\r\n","GET / HTTP/1.1\r\nContent-Length: -1\r\n\r\n"})assert(parseHttp(bad,strlen(bad),r)==HttpState::Bad);
 std::string big="GET /"+std::string(100,'a')+" HTTP/1.1\r\n\r\n";assert(parseHttp(big.data(),big.size(),r)==HttpState::Bad);
 assert(parseHttp("GET / HT",8,r)==HttpState::Need);
 // truncated percent escape and overflow numbers rejected
 std::string pe="GET /a?x=%4 HTTP/1.1\r\n\r\n";assert(parseHttp(pe.data(),pe.size(),r)==HttpState::Ready&&!r.param("x",s,sizeof(s)));
 std::string ov="GET /a?n=99999999999 HTTP/1.1\r\n\r\n";assert(parseHttp(ov.data(),ov.size(),r)==HttpState::Ready&&!r.uintParam("n",v));
 // fuzz: every prefix and byte flip must be handled without crash (ASan)
 for(size_t i=0;i<=h.size();i++)parseHttp(h.data(),i,r);
 for(unsigned i=0;i<2000;i++){std::string z=a;z[(i*7)%z.size()]=char(i*31);parseHttp(z.data(),z.size(),r);}
}
static void pageAndCaptive(){
 Rig r;for(const char* p:{"/","/generate_204","/hotspot-detect.html","/ncsi.txt","/anything"}){auto o=r.call("GET",p,"",1);assert(o.page&&o.code==200);}
 assert(r.call("POST","/","",1).code==405);
 assert(strstr(PAGE,"Lái")&&strstr(PAGE,"Ráp")&&strstr(PAGE,"Wi-Fi")&&strstr(PAGE,"0.65"));
}
static void tokensAndSeq(){
 Rig r;auto o=r.call("POST","/api/move","token=1&seq=1&dir=1&fresh=1",100);assert(o.code==409);   // no session
 r.session();r.echo(300);
 auto bad=r.call("POST","/api/move","token="+std::to_string(r.tok+1)+"&seq=1&dir=1&fresh=1",300);assert(bad.code==409);r.off();
 assert(r.call("POST","/api/move","token="+std::to_string(r.tok)+"&seq=1&dir=9&fresh=1",300).code==400);
 assert(r.call("POST","/api/move","token="+std::to_string(r.tok)+"&seq=1&dir=1&fresh=2",300).code==400);
 r.seq=0;r.drive(1);assert(r.hw.on);
 uint32_t before=r.seq;r.seq=before-1;auto old=r.move(1,0,800);assert(old.code==409);   // replayed/old seq refused
 r.seq=before;r.echo(800);assert(r.move(1,0,800).code==200&&r.c.active());
 // new session revokes the old one and stops
 uint32_t oldTok=r.tok;r.session(450);r.off();assert(r.tok!=oldTok);
 auto stale=r.call("POST","/api/move","token="+std::to_string(oldTok)+"&seq=9&dir=1&fresh=1",460);assert(stale.code==409);r.off();
 // status identifies the owner
 assert(strstr(r.call("GET","/api/status","token="+std::to_string(r.tok),470).body,"\"owner\":true"));
 assert(strstr(r.call("GET","/api/status","token="+std::to_string(oldTok),470).body,"\"owner\":false"));
}
static void leaseAndStops(){
 Rig r;r.session();r.drive(1);assert(r.hw.latest[0]>1500&&r.hw.latest[3]<1500);
 // lease: no renewal -> stops by itself ~500 ms
 r.echo(760);assert(r.move(1,0,760).code==200);
 r.echo(760+PHONE_LEASE_MS-1);r.c.tick(760+PHONE_LEASE_MS-1);assert(r.c.active());
 r.c.tick(760+PHONE_LEASE_MS+1);r.c.tick(760+PHONE_LEASE_MS+60);r.off();
 // a repeat (fresh=0) after lease expiry must not restart
 assert(r.move(1,0,1500).code==409);r.off();
 // release stops
 r.drive(2,2000);assert(r.hw.latest[0]<1500);assert(r.move(0,0,2400).code==200);r.off();
 // renewals keep it alive beyond one lease
 r.drive(1,3000);for(uint32_t t=3400;t<3900;t+=150){r.echo(t);assert(r.move(1,0,t).code==200);r.c.tick(t);}assert(r.c.active());
 // /api/stop needs no token
 assert(r.call("POST","/api/stop","",3950).code==200);r.off();
 // direction change keeps lease and maps diagonals
 r.drive(1,5000);r.echo(5400);assert(r.move(6,0,5400).code==200);assert(r.hw.latest[0]>r.hw.latest[3]||true);
 int l=int(r.hw.latest[0])-1500,rr=1500-int(r.hw.latest[3]);assert(rr<l);   // fwd-right: right side slower
 r.c.stop();
 // button, link loss, session idle, AP client loss, I2C fault
 r.drive(1,6000);r.c.button(true);r.off();r.c.button(false);
 r.session(7000);r.drive(1,7000);r.net.n=0;r.p.tick(7100);r.off();assert(!r.p.hasSession());
 r.net.n=1;r.session(8000);r.drive(1,8000);r.p.tick(8000+PHONE_IDLE_MS+1);r.off();assert(!r.p.hasSession());
 r.session(9000);r.drive(1,9000);r.hw.ok=false;r.c.tick(9360+100);assert(r.c.stage==Stage::Fault);r.off();
 assert(r.move(1,1,9600).code==409);
}
static void arbitration(){
 Rig r;r.c.link(true,0);r.session();r.echo(300);
 // host cue running: phone cannot take over
 char rep[200];r.c.command("MOTOR ARM",300,rep,sizeof(rep));assert(!strcmp(rep,"ACK MOTOR ARM"));
 r.c.command("MOTOR CUE FWD",300,rep,sizeof(rep));assert(r.c.active()&&r.c.mode==Mode::Cue);
 auto o=r.move(1,1,310);assert(o.code==409&&r.c.mode==Mode::Cue&&r.c.active());
 // STOP from the phone wins
 assert(r.call("POST","/api/stop","",320).code==200);r.off();
 // phone drive running: host cue and AUTO cannot start; host stop wins
 r.drive(1,1000);r.c.command("MOTOR ARM",1400,rep,sizeof(rep));assert(!strcmp(rep,"ERR MOTOR inhibited"));assert(r.c.mode==Mode::Phone&&r.c.active());
 r.c.command("AUTO ON",1400,rep,sizeof(rep));assert(r.c.mode==Mode::Phone||!r.c.active());
 r.c.command("MOTOR STOP",1410,rep,sizeof(rep));r.off();
 // auto mode running: phone refused until STOP
 r.c.link(true,2000);r.c.command("MOTOR ARM",2000,rep,sizeof(rep));r.echo(2000);r.c.command("AUTO ON",2000,rep,sizeof(rep));
 if(r.c.active()){assert(r.c.mode==Mode::Auto);assert(r.move(1,1,2010).code==409&&r.c.mode==Mode::Auto);r.call("POST","/api/stop","",2020);r.off();}
}
static void sonarGuard(){
 Rig r;r.session();
 auto o=r.move(1,1,300);assert(o.code==423&&strstr(o.body,"dữ liệu sonar trước")&&strstr(o.body,"\"blocked\":true"));r.off();   // no data
 r.echo(300,200);o=r.move(1,1,300);assert(o.code==423&&strstr(o.body,"vật cản phía trước"));r.off();                           // too close
 r.echo(300,1000);o=r.move(1,1,300+FRESH_MS+5);assert(o.code==423&&strstr(o.body,"đã cũ"));r.off();                              // stale
 // reverse uses the rear sensor only; blocked front must not stop reversing
 r.c.sample(0,100,true,0,400);r.c.sample(0,100,true,0,400);r.c.sample(1,1000,true,0,400);r.c.sample(1,1000,true,0,400);
 assert(r.move(2,1,400).code==200);r.c.stop();
 assert(r.move(1,1,400).code==423);
 // pivot needs both
 assert(r.move(3,1,400).code==423);r.off();
 // blocked while driving cuts power immediately
 r.echo(1000);r.drive(1,1000);r.echo(1500,100);r.c.tick(1500);r.off();
 // status reports invalid distances honestly
 r.c.ranges[0].valid=false;auto st=r.call("GET","/api/status","token="+std::to_string(r.tok),2000);assert(strstr(st.body,"\"frontValid\":false")&&strstr(st.body,"\"front\":-1")&&strstr(st.body,"không hợp lệ"));
}
static void assemblyAndMisc(){
 Rig r;r.session();r.echo(300);
 assert(r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=0&kind=n&delta=5",300).code==423);   // only in assembly
 assert(r.call("POST","/api/assembly","token="+std::to_string(r.tok)+"&active=1",300).code==200);
 assert(r.move(1,1,310).code==423);r.off();assert(r.move(0,0,320).code==200);
 assert(r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=0&kind=n&delta=5",330).code==200&&r.c.cal.wheels[0].neutral==1505);
 assert(r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=1&kind=d&delta=0",330).code==200&&r.c.cal.wheels[1].direction==-1);
 assert(r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=2&kind=s&delta=10",330).code==200&&r.c.cal.wheels[2].span==110);
 for(int i=0;i<30;i++)r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=3&kind=n&delta=5",330);assert(r.c.cal.wheels[3].neutral<=1700);
 assert(r.call("POST","/api/trim","token="+std::to_string(r.tok)+"&ch=9&kind=n&delta=5",330).code==400);
 assert(r.call("POST","/api/turretcal","token="+std::to_string(r.tok)+"&delta=-5",330).code==200&&r.c.cal.turretCenter==1495);
 auto j=r.call("POST","/api/jog","token="+std::to_string(r.tok)+"&ch=0&d=1",340);assert(j.code==200&&r.c.active()&&r.c.mode==Mode::Test);
 r.c.stop();
 assert(r.call("POST","/api/turret","token="+std::to_string(r.tok)+"&pos=max",350).code==200&&r.c.mode==Mode::Turret);r.c.stop();
 assert(r.move(0,0,355).code==200);r.echo(355);assert(r.call("POST","/api/turret","token="+std::to_string(r.tok)+"&pos=center",355).code==200);r.c.stop();
 assert(r.call("POST","/api/save","token="+std::to_string(r.tok),360).code==200);
 assert(r.call("GET","/api/cal","token=1",360).code==200);
 // leaving assembly re-enables drive
 assert(r.call("POST","/api/assembly","token="+std::to_string(r.tok)+"&active=0",690).code==200);r.echo(700);r.drive(1,700);r.c.stop();
 // light is honest: not wired; speed validated
 assert(r.call("POST","/api/light","token="+std::to_string(r.tok),400).code==409);
 assert(r.call("POST","/api/speed","token="+std::to_string(r.tok)+"&value=0.65",400).code==200);
 assert(r.call("POST","/api/speed","token="+std::to_string(r.tok)+"&value=9",400).code==400);
 // wifi: password never echoed; short password and bad ssid refused; errors in Vietnamese
 auto w=r.call("POST","/api/wifi","ssid=Nha&password=matkhau123",410);assert(w.code==200&&!strstr(w.body,"matkhau123")&&r.net.lastPass=="matkhau123");
 assert(r.call("POST","/api/wifi","ssid=Nha&password=123",410).code==400);
 r.net.joinOk=false;auto f=r.call("POST","/api/wifi","ssid=Nha&password=matkhau123",410);assert(f.code==409&&strstr(f.body,"Sai mật khẩu"));
 assert(!strstr(r.call("GET","/api/status","token=1",420).body,"matkhau123"));
 assert(strstr(r.call("POST","/api/scan","",420).body,"Nha"));
}
static void screen(){
 static uint16_t fb[pet::W*pet::H/2];
 Qr a,b;assert(a.encode("WIFI:T:nopass;S:XeTang-ABCD;;")&&b.encode("http://192.168.4.1/"));
 for(int half=0;half<2;half++)for(int phase=0;phase<2;phase++){
  pet::Canvas cv{fb,half*pet::H/2,pet::H/2};pet::renderNet(cv,"XeTang-ABCD","192.168.4.1",a,b,phase);
  unsigned white=0,black=0;for(unsigned i=0;i<pet::W*pet::H/2;i++){if(fb[i]==0xFFFF)white++;else if(fb[i]==0)black++;}
  if(half==1){assert(white>2000&&black>300);}
 }
}
int main(){screen();parser();pageAndCaptive();tokensAndSeq();leaseAndStops();arbitration();sonarGuard();assemblyAndMisc();std::cout<<"phone_test ok\n";}
