#include <Arduino.h>
#include <esp_system.h>
#include <esp_task_wdt.h>
#include <esp_mac.h>
#include <esp_heap_caps.h>
#include "esp_hardware.h"
#include "display.h"
#include "sonar.h"
#include "face.h"
#include "session_face.h"
#include "status_bar.h"
#include "usage_face.h"
#include "wifi_net.h"
#include "net_screen.h"
static tank::EspHardware hardware;
static tank::Controller control(hardware);
static tank::MotionParser motion;
static tank::EchoIO echoIO;
static tank::Sonars<tank::EchoIO> sonars(echoIO);
static tank::Display display;
static uint32_t rnd32(){return esp_random();}
static tank::WifiNet wifi;
static tank::Phone phone(control,wifi,rnd32);
static tank::Qr qrWifi,qrUrl;
// Half-height (240x120, 57.6 KB) static buffer: classic ESP32 has no single 115 KB block.
// Each frame is rendered twice with a row window (top half, then bottom half) and streamed in bands.
static uint16_t framebuffer[pet::W*pet::H/2];
static pet::Canvas canvas{framebuffer,0,pet::H/2};
static bool bottomPending=false;
static pet::LineParser parser;
static pet::TextParser textParser;
static pet::DisplayText text;
static pet::HostStatus host;
static pet::HostStatusParser hostParser;
static pet::SessionList list;
static pet::SessionListParser listParser;
static pet::TaskView taskView;
static pet::TaskQuery taskQuery;
static pet::UsageParser usageParser;
static pet::UsageData usage;
static pet::UsageView usageView;
static pet::Activity activity;
static pet::ActivityParser activityParser;
static pet::Fun fun;
static pet::FunParser funParser;
static pet::StateMachine states;
static pet::Blink blink;
static pet::Button browse;
static bool wasConnected=false,displayReady=false;
static uint32_t lastFrame=0,visualSince=0,frameNow=0;
static pet::State visual=pet::State::Idle;
static esp_timer_handle_t safetyTimer=nullptr;
static void say(const char* s){if(Serial)Serial.println(s);}
static void identity(){say("HELLO tank v1 pet");}
static void resetParsers(){parser={};textParser={};hostParser={};listParser={};usageParser={};activityParser={};funParser={};taskQuery={};motion={};}
static void feed(char ch,uint32_t now) {
  char reply[240]{};
  if(motion.feed(ch,control,now,reply,sizeof(reply))) {
    // Identity from this target only, no inherited pet receipt or hard-coded MAC.
    if(!strncmp(reply,"MOTOR CAPS tank-v1",18)){
      uint8_t mac[6]{};if(esp_efuse_mac_get_default(mac)==ESP_OK){size_t used=strlen(reply);snprintf(reply+used,sizeof(reply)-used," MAC=%02x:%02x:%02x:%02x:%02x:%02x",mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]);}
    }
    say(reply);
  }
  if(taskQuery.feed(ch)){int i=taskView.selected(list,now);snprintf(reply,sizeof(reply),"TASK %s %c %u/%u",i>=0?list.rows[i].id:"none",i>=0?list.rows[i].state:'I',i>=0?unsigned(i)+1:0,list.valid?list.count:0);say(reply);}
  if(hostParser.feed(ch,host,now))say("ACK host");
  if(listParser.feed(ch,list,now)){snprintf(reply,sizeof(reply),"ACK list %u",list.generation);say(reply);}
  auto event=funParser.feed(ch,fun,now);
  if(event!=pet::FunEvent::None){if(event==pet::FunEvent::Power)control.sleep(fun.sleeping);say(event==pet::FunEvent::Power?"ACK power":"ACK mood");}
  auto a=activityParser.feed(ch,activity,now);if(a!=pet::ActivityEvent::None)say(a==pet::ActivityEvent::Sessions?"ACK sessions":"ACK celebrate");
  usageParser.feed(ch,usage,now);if(usageParser.providerCommand)say("ACK provider");
  auto t=textParser.feed(ch,text,now);if(t!=pet::TextEvent::None)say(t==pet::TextEvent::Title?"ACK title":"ACK action");
  auto cmd=parser.feed(ch);
  if(cmd==pet::Command::Ping)say("PONG tank v1 pet");
  else if(cmd==pet::Command::Layout)say("LAYOUT width=240 height=240 bus=spi format=status-ticker eyes=lcd");
  else if(cmd!=pet::Command::None){states.receive(static_cast<pet::State>(cmd),now);if(cmd==pet::Command::Ask||cmd==pet::Command::Cancelled)control.stop("host-state");if(cmd!=pet::Command::Idle)activity.active=false;}
}
void setup() {
  // Inhibit before USB, I2C, LCD or NVS. Resistor-defined safe states remain board responsibility.
  digitalWrite(tank::OE_PIN,HIGH);pinMode(tank::OE_PIN,OUTPUT);
  digitalWrite(tank::ACT_PIN,LOW);pinMode(tank::ACT_PIN,OUTPUT);
  pinMode(tank::STOP_PIN,INPUT_PULLUP);pinMode(tank::BOOT_PIN,INPUT_PULLUP);
  esp_timer_create_args_t args{};args.callback=tank::guard;args.name="tank-deadman";args.dispatch_method=ESP_TIMER_TASK;
  bool timerOK=esp_timer_create(&args,&safetyTimer)==ESP_OK&&esp_timer_start_periodic(safetyTimer,5000)==ESP_OK;
  Serial.setRxBufferSize(8192);Serial.begin(115200);
  Wire.begin(tank::SDA_PIN,tank::SCL_PIN,100000);Wire.setTimeOut(10);
  hardware.load(control.cal);control.begin(millis());echoIO.begin();
  displayReady=display.begin();
  if(!timerOK||!displayReady){tank::prerequisitesReady=false;tank::safetyTrip=true;control.stop(!timerOK?"timer":"display");}
  // IDF task watchdog resets a stuck loop; startup/reset hardware is required to inhibit loads.
  if(esp_task_wdt_init(2,true)!=ESP_OK||esp_task_wdt_add(nullptr)!=ESP_OK){tank::prerequisitesReady=false;tank::safetyTrip=true;control.stop("watchdog-init");}
  wifi.begin();{char w[48];snprintf(w,sizeof(w),"WIFI:T:nopass;S:%s;;",wifi.apName);qrWifi.encode(w);qrUrl.encode("http://192.168.4.1/");}
  blink.begin(millis(),esp_random());browse.begin(digitalRead(tank::BOOT_PIN)==LOW,millis());
  usageView.begin(millis());identity();
}
void loop() {
  const uint32_t now=millis();bool connected=bool(Serial);
  // Either held button dominates every command and every enable path; release never auto-arms.
  bool down=digitalRead(tank::STOP_PIN)==LOW||digitalRead(tank::BOOT_PIN)==LOW;
  control.button(down);
  if(tank::safetyTrip&&control.active())control.stop("deadman");
  if(connected!=wasConnected){control.link(connected,now);resetParsers();if(connected){list.valid=host.valid=false;identity();}wasConnected=connected;}
  for(unsigned budget=0;budget<64&&Serial.available();budget++){feed(char(Serial.read()),now);control.button(digitalRead(tank::STOP_PIN)==LOW||digitalRead(tank::BOOT_PIN)==LOW);}
  sonars.tick(micros(),millis(),control.heading(),control);
  if(sonars.triggering()){delayMicroseconds(12);sonars.tick(micros(),millis(),control.heading(),control);}
  wifi.service(phone,millis());phone.tick(millis());
  control.tick(millis());
  // Refresh only after the control loop completed, never from a display callback or a heartbeat ISR.
  portENTER_CRITICAL(&tank::safetyMux);
  if(control.active()&&!tank::safetyTrip){unsigned budget=control.watchdogBudget(millis());tank::safetyDue=micros()+(budget<100?budget:100)*1000u;tank::safetyActive=true;}
  else tank::safetyActive=false;
  portEXIT_CRITICAL(&tank::safetyMux);
  list.expire(now);auto press=browse.update(digitalRead(tank::BOOT_PIN)==LOW,now);
  if(press!=pet::Press::None)say(press==pet::Press::Short?"BTN boot short":"BTN boot long");
  pet::State state=states.effective(now);bool browsing=taskView.update(list,press,now);
  bool showUsage=usageView.update(state,browsing?pet::Press::None:press,now,false);
  fun.update(state,now,false,0,pet::Press::None,showUsage);activity.update(state,now,showUsage||fun.sleeping);
  if(state!=visual){visual=state;visualSince=now;}
  if(displayReady&&display.busy()){if(!display.step()){displayReady=false;tank::prerequisitesReady=false;control.stop("display");}}
  else if(displayReady&&(bottomPending||uint32_t(now-lastFrame)>=80)){
    if(!bottomPending){lastFrame=now;frameNow=now;}
    canvas.y0=bottomPending?pet::H/2:0;canvas.h=pet::H/2;
    if(wifi.clients()==0)pet::renderNet(canvas,wifi.apName,"192.168.4.1",qrWifi,qrUrl,(frameNow/6000)&1);
    else{
    if(showUsage)pet::renderUsage(canvas,usage,state,frameNow);
    else{pet::render(canvas,state,frameNow,blink.height(frameNow),pet::Press::None,false,connected,frameNow-visualSince,&text,0,&activity,&fun);pet::renderSingleTask(canvas,list,taskView,frameNow,state,&text);}
    pet::renderStatusBar(canvas,host,frameNow,fun.sleeping);}
    if(!display.start(framebuffer,canvas.y0,pet::H/2)){displayReady=false;tank::prerequisitesReady=false;control.stop("display");}
    bottomPending=!bottomPending;
  }
  esp_task_wdt_reset();delay(1);
}
