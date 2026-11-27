#include <assert.h>
#include <string>
#include <iostream>
#include "face.h"
#include "session_face.h"
#include "status_bar.h"
#include "usage_face.h"
template<class Parser,class Target> auto send(Parser& parser,Target& target,const std::string& s,uint32_t at=0)->decltype(parser.feed('\n',target,at)){decltype(parser.feed('\n',target,at)) out{};for(char c:s)out=parser.feed(c,target,at);return out;}
int main(){
 pet::TextParser textParser;pet::DisplayText text;
 assert(send(textParser,text,"TITLE 436C617564652054616E6B\n")==pet::TextEvent::Title);assert(std::string(text.title)=="Claude Tank");
 assert(send(textParser,text,"ACTION 576F726B696E67\n")==pet::TextEvent::Action);assert(std::string(text.action)=="Working");
 assert(send(textParser,text,"TITLE C080\n")==pet::TextEvent::None);assert(std::string(text.title)=="Claude Tank");
 pet::SessionList list;pet::SessionListParser parser;
 send(parser,list,"LIST 42 1 1\n");send(parser,list,"ROW 42 0 P 1234abcd 54657374 4F4B\n");assert(send(parser,list,"END 42\n"));assert(list.count==1&&list.rows[0].state=='P');
 send(parser,list,"LIST 43 2 2\n");assert(!send(parser,list,"END 43\n"));assert(list.generation==42);
 pet::HostStatus host;pet::HostStatusParser hp;assert(send(hp,host,"HOST 43200 3 84 0\n"));assert(host.battery==84);
 pet::Activity activity;pet::ActivityParser ap;assert(send(ap,activity,"SESSIONS 2\n")==pet::ActivityEvent::Sessions);assert(activity.sessions==2);
 pet::Fun fun;pet::FunParser fp;assert(send(fp,fun,"POWER sleep\n")==pet::FunEvent::Power);assert(fun.sleeping);
 pet::UsageData usage;pet::UsageParser up;assert(send(up,usage,"USAGE 25 3600 40 600\n"));assert(usage.percent[0]==25);
 static uint16_t fb[pet::W*pet::H];pet::Canvas c{fb};pet::TaskView view;pet::Blink blink;
 for(unsigned state=0;state<6;state++){pet::render(c,pet::State(state),12345,blink.height(12345),pet::Press::None,false,true,1000,&text,0,&activity,&fun);pet::renderSingleTask(c,list,view,12345,pet::State(state),&text);pet::renderStatusBar(c,host,12345);}
 // Half-height windowed rendering (used on the no-PSRAM ESP32) must equal the full frame.
 for(unsigned state=0;state<6;state++){
  pet::TaskView v1,v2;pet::Canvas full{fb};full.clear();
  pet::render(full,pet::State(state),999,blink.height(999),pet::Press::None,false,true,1000,&text,0,&activity,&fun);pet::renderSingleTask(full,list,v1,999,pet::State(state),&text);pet::renderStatusBar(full,host,999);
  static uint16_t half[pet::W*pet::H/2];
  for(int part=0;part<2;part++){
   pet::Canvas h{half,part*pet::H/2,pet::H/2};h.clear();
   pet::render(h,pet::State(state),999,blink.height(999),pet::Press::None,false,true,1000,&text,0,&activity,&fun);pet::renderSingleTask(h,list,v2,999,pet::State(state),&text);pet::renderStatusBar(h,host,999);
   assert(!memcmp(half,fb+part*pet::W*pet::H/2,sizeof(half)));
  }
 }
 std::cout<<"PASS reference protocol + framebuffer\n";
}
