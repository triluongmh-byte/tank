#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "text_protocol.h"
namespace pet {
constexpr unsigned MAX_SESSION_ROWS=12;
struct SessionRow {char id[9]{},state='I',title[81]{},reply[161]{};};
struct SessionList {
  SessionRow rows[MAX_SESSION_ROWS]{};
  unsigned count=0,total=0;uint16_t generation=0;
  uint32_t receivedAt=0,pageEpoch=0;bool valid=false;
  void expire(uint32_t now){if(valid && uint32_t(now-receivedAt)>=30000){valid=false;count=0;}}
  unsigned page(uint32_t now)const{return count?uint32_t(now-pageEpoch)/5000%((count+2)/3):0;}
};
// One visible task; manual browsing is bound to the session ID, never to a reorderable row.
struct TaskView {
  char selectedId[9]{};bool browsing=false;uint32_t browsedAt=0;
  uint32_t tickerHash=0,tickerAt=0;bool tickerSet=false;
  static unsigned rank(char state){return state=='P'?0:state=='T'?1:state=='A'?2:3;}
  int selected(const SessionList& list,uint32_t now) {
    if(!list.valid || !list.count){browsing=false;selectedId[0]=0;return -1;}
    if(browsing && uint32_t(now-browsedAt)<10000) {
      for(unsigned i=0;i<list.count;i++)if(!strcmp(selectedId,list.rows[i].id))return int(i);
    }
    browsing=false;
    unsigned best=0;for(unsigned i=1;i<list.count;i++)if(rank(list.rows[i].state)<rank(list.rows[best].state))best=i;
    strcpy(selectedId,list.rows[best].id);return int(best);
  }
  bool update(const SessionList& list,Press press,uint32_t now) {
    int current=selected(list,now);
    if(current<0 || list.count<2 || press==Press::None)return false;
    strcpy(selectedId,list.rows[(unsigned(current)+1)%list.count].id);
    browsing=true;browsedAt=now;return true;
  }
};
// Read-only diagnostic; it cannot synthesize a press or drive an output.
struct TaskQuery {
  char line[8]{};unsigned used=0;bool invalid=false;
  bool feed(char c){
    if(c!='\n'){if(used>=sizeof(line)-1 || (uint8_t(c)<32 && c!='\r'))invalid=true;else line[used++]=c;return false;}
    if(used && line[used-1]=='\r')--used;line[used]=0;
    bool hit=!invalid && !strcmp(line,"tasks");used=0;invalid=false;return hit;
  }
};
// LIST/ROW/END is transactional: incomplete/malformed frames never replace the screen.
struct SessionListParser {
  char line[560]{};unsigned used=0;bool invalid=false,staging=false;
  SessionRow pending[MAX_SESSION_ROWS]{};unsigned count=0,total=0;uint16_t generation=0,seen=0;
  static bool number(const char* p,unsigned limit,unsigned& out){
    if(!p || !*p)return false;out=0;
    for(;*p;p++){if(*p<'0'||*p>'9'||out>limit/10)return false;out=out*10+unsigned(*p-'0');if(out>limit)return false;}
    return true;
  }
  static bool identifier(const char* p){
    if(strlen(p)!=8)return false;
    for(;*p;p++)if(!(*p>='0'&&*p<='9')&&!(*p>='a'&&*p<='f'))return false;
    return true;
  }
  static bool text(const char* hex,char* out,unsigned maxBytes){
    size_t n=strlen(hex);if(!n || n>maxBytes*2 || n%2)return false;
    for(size_t i=0;i<n;i+=2){int a=TextParser::hex(hex[i]),b=TextParser::hex(hex[i+1]);if(a<0||b<0)return false;unsigned c=unsigned(a*16+b);if(c<32||c==127)return false;out[i/2]=char(c);}
    out[n/2]=0;const char* p=out;
    while(*p){uint32_t c=utf8Next(p);if(c==0xFFFFFFFF||(c>=127&&c<160))return false;}
    return true;
  }
  bool feed(char ch,SessionList& list,uint32_t now){
    if(ch!='\n'){
      if(used>=sizeof(line)-1 || (uint8_t(ch)<32 && ch!='\r') || uint8_t(ch)>126)invalid=true;
      else line[used++]=ch;
      return false;
    }
    if(used && line[used-1]=='\r')--used;line[used]=0;used=0;
    bool listCommand=!strncmp(line,"LIST ",5)||!strncmp(line,"ROW ",4)||!strncmp(line,"END ",4);
    if(invalid){invalid=false;if(listCommand)staging=false;return false;}
    char* parts[7]{};unsigned n=0;char* save=nullptr;
    for(char* p=strtok_r(line," ",&save);p;p=strtok_r(nullptr," ",&save)){if(n==7){staging=false;return false;}parts[n++]=p;}
    if(!n)return false;
    unsigned gen=0,index=0,size=0,all=0;
    if(!strcmp(parts[0],"LIST")){
      staging=false;
      if(n!=4 || !number(parts[1],65535,gen)||!number(parts[2],MAX_SESSION_ROWS,size)||!number(parts[3],9999,all)||size>all)return false;
      generation=uint16_t(gen);count=size;total=all;seen=0;staging=true;memset(pending,0,sizeof(pending));return false;
    }
    if(!strcmp(parts[0],"ROW")){
      if(!staging)return false;
      if((n!=6 && n!=7) || !number(parts[1],65535,gen)||gen!=generation||!number(parts[2],MAX_SESSION_ROWS-1,index)||index>=count||strlen(parts[3])!=1||!strchr("IATP",parts[3][0])||!identifier(parts[4])||(seen&(1u<<index))){staging=false;return false;}
      for(unsigned i=0;i<count;i++)if((seen&(1u<<i))&&!strcmp(pending[i].id,parts[4])){staging=false;return false;}
      if(!text(parts[5],pending[index].title,80) || (n==7 && !text(parts[6],pending[index].reply,160))){staging=false;return false;}
      strcpy(pending[index].id,parts[4]);pending[index].state=parts[3][0];seen|=uint16_t(1u<<index);return false;
    }
    if(!strcmp(parts[0],"END")){
      if(!staging)return false;
      staging=false;
      if(n!=2||!number(parts[1],65535,gen)||gen!=generation||seen!=uint16_t((1u<<count)-1))return false;
      if(!list.valid || list.count!=count)list.pageEpoch=now;
      memcpy(list.rows,pending,sizeof(pending));list.count=count;list.total=total;list.generation=generation;list.receivedAt=now;list.valid=true;return true;
    }
    return false;
  }
};
} // namespace pet
