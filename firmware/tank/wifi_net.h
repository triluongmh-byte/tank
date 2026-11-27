#pragma once
// ESP32 Wi-Fi/HTTP glue for the phone UI: open AP, captive DNS, bounded one-request-at-a-time server,
// optional home Wi-Fi saved in NVS. Target-only (Arduino). Passwords are never logged or returned.
#include <Arduino.h>
#include <WiFi.h>
#include <DNSServer.h>
#include <Preferences.h>
#include <esp_mac.h>
#include "phone.h"
#include "page.h"
namespace tank {
class WifiNet:public NetIface {
  WiFiServer server{80};DNSServer dns;WiFiClient client;Preferences prefs;
  char req[HTTP_MAX+1]{};size_t used=0;uint32_t since=0,joinAt=0,retryAt=0,scanAt=0;
  enum class J:uint8_t{None,Joining,Online,Failed} state=J::None;
  char cand[33]{},candPass[64]{},saved[33]{},savedPass[64]{},lastError[64]{};
  bool haveSaved=false,scanning=false;
public:
  char apName[20]{};
  void begin() {
    uint8_t mac[6]{};esp_efuse_mac_get_default(mac);snprintf(apName,sizeof(apName),"XeTang-%02X%02X",mac[4],mac[5]);
    WiFi.persistent(false);WiFi.mode(WIFI_AP_STA);WiFi.setSleep(false);
    WiFi.softAPConfig(IPAddress(192,168,4,1),IPAddress(192,168,4,1),IPAddress(255,255,255,0));
    WiFi.softAP(apName,nullptr,1,0,4);   // open network, max 4 clients
    dns.start(53,"*",IPAddress(192,168,4,1));server.begin();server.setNoDelay(true);
    if(prefs.begin("tank-wifi",true)){
      if(prefs.getString("ssid",saved,sizeof(saved))>0&&prefs.getString("pass",savedPass,sizeof(savedPass))>=0&&saved[0]){haveSaved=true;}
      prefs.end();
    }
    if(haveSaved){WiFi.begin(saved,savedPass);state=J::Joining;joinAt=millis();strcpy(cand,saved);strcpy(candPass,savedPass);}
  }
  bool online()const{return WiFi.status()==WL_CONNECTED;}
  unsigned clients()override{return unsigned(WiFi.softAPgetStationNum());}
  void url(char* out,size_t n){if(online()){snprintf(out,n,"%s",WiFi.localIP().toString().c_str());}else snprintf(out,n,"192.168.4.1");}
  int scan(char* json,size_t n)override {
    int k=WiFi.scanComplete();
    if(k==WIFI_SCAN_FAILED&&!scanning){WiFi.scanNetworks(true);scanning=true;scanAt=millis();return 0;}
    if(k==WIFI_SCAN_RUNNING||(k==WIFI_SCAN_FAILED&&scanning&&millis()-scanAt<10000))return 0;
    scanning=false;if(k<0)return -1;
    size_t o=snprintf(json,n,"{\"busy\":false,\"networks\":[");int cnt=0;
    for(int i=0;i<k&&cnt<12;i++){
      String s=WiFi.SSID(i);if(!s.length()||s.length()>32)continue;
      bool bad=false;for(size_t j=0;j<s.length();j++)if(s[j]=='"'||s[j]=='\\'||uint8_t(s[j])<32)bad=true;if(bad)continue;
      bool dup=false;for(int j=0;j<i;j++)if(WiFi.SSID(j)==s)dup=true;if(dup)continue;
      if(o+s.length()+8>=n)break;o+=snprintf(json+o,n-o,"%s\"%s\"",cnt?",":"",s.c_str());cnt++;
    }
    snprintf(json+o,n-o,"]}");WiFi.scanDelete();return 1;
  }
  bool join(const char* ssid,const char* pass,const char*& err)override {
    if(state==J::Joining&&millis()-joinAt<18000){err="Đang kết nối, vui lòng đợi";return false;}
    strncpy(cand,ssid,sizeof(cand)-1);strncpy(candPass,pass,sizeof(candPass)-1);lastError[0]=0;
    WiFi.scanDelete();scanning=false;WiFi.disconnect(false,false);WiFi.begin(cand,candPass);state=J::Joining;joinAt=millis();return true;
  }
  void describe(char* out,size_t n)override {
    char u[20];url(u,sizeof(u));const char* home=state==J::Joining?"đang kết nối":online()?"đã kết nối":state==J::Failed?lastError:"chưa dùng";
    snprintf(out,n,"Mạng xe: %s\\nĐịa chỉ: %s\\nWi-Fi nhà: %s",apName,u,home);
  }
  // Called every loop. Never blocks longer than one small request.
  void service(Phone& phone,uint32_t now) {
    dns.processNextRequest();
    if(state==J::Joining) {
      if(WiFi.status()==WL_CONNECTED){
        state=J::Online;
        if(strcmp(cand,saved)||strcmp(candPass,savedPass)){
          if(prefs.begin("tank-wifi",false)){prefs.putString("ssid",cand);prefs.putString("pass",candPass);prefs.end();}
          strcpy(saved,cand);strcpy(savedPass,candPass);haveSaved=true;
        }
        memset(candPass,0,sizeof(candPass));
      } else if(now-joinAt>=18000||WiFi.status()==WL_CONNECT_FAILED||WiFi.status()==WL_NO_SSID_AVAIL){
        snprintf(lastError,sizeof(lastError),"%s",WiFi.status()==WL_NO_SSID_AVAIL?"Không thấy mạng này":WiFi.status()==WL_CONNECT_FAILED?"Sai mật khẩu":"Hết thời gian kết nối");
        state=J::Failed;WiFi.disconnect(false,false);memset(candPass,0,sizeof(candPass));retryAt=now;
      }
    } else if(state==J::Online&&!online()){state=J::Failed;snprintf(lastError,sizeof(lastError),"Mất kết nối Wi-Fi nhà");retryAt=now;}
    else if(state==J::Failed&&haveSaved&&now-retryAt>=30000&&clients()==0){
      strcpy(cand,saved);strcpy(candPass,savedPass);WiFi.begin(saved,savedPass);state=J::Joining;joinAt=now;
    }
    if(!client||!client.connected()){
      WiFiClient c=server.available();
      if(c){client=c;client.setTimeout(1);used=0;since=now;}
      return;
    }
    while(client.available()&&used<sizeof(req)-1)req[used++]=char(client.read());
    HttpRequest r;HttpState st=used?parseHttp(req,used,r):HttpState::Need;
    if(st==HttpState::Need&&now-since<1500&&used<HTTP_MAX)return;
    HttpReply o;
    if(st==HttpState::Ready)phone.handle(r,now,o);else o.err(st==HttpState::Bad?400:408,"Yêu cầu không hợp lệ");
    reply(o,st==HttpState::Ready&&!strcmp(r.method,"HEAD"));
    client.stop();used=0;
  }
  void reply(const HttpReply& o,bool head) {
    size_t len=o.page?strlen(PAGE):strlen(o.body);
    client.printf("HTTP/1.1 %d X\r\nContent-Type: %s\r\nContent-Length: %u\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n",o.code,o.type,unsigned(len));
    if(head)return;
    if(o.page){for(size_t i=0;i<len;i+=1024){size_t k=len-i<1024?len-i:1024;client.write(reinterpret_cast<const uint8_t*>(PAGE)+i,k);}}
    else client.write(reinterpret_cast<const uint8_t*>(o.body),len);
  }
};
}
