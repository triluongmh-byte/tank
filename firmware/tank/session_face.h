#pragma once
#include <stdio.h>
#include "face.h"
#include "session_list.h"
namespace pet {
constexpr int TASK_BASELINE=211;
// GIẢ ĐỊNH from IMG_2281: the installed bezel hides about17 canvas rows at top.
// This calibrates footer spacing only; never changes the panel window or clock.
constexpr int VISIBLE_TOP_CROP_ESTIMATE_PX=17;
inline const char* sessionStateLabel(char state){return state=='A'?"WAIT":state=='P'?"WORK":state=='T'?"THINK":"IDLE";}
inline uint16_t sessionStateColor(char state){return state=='A'?rgb(255,80,70):state=='P'?rgb(255,210,50):state=='T'?rgb(210,100,255):rgb(80,220,220);}
constexpr int TASK_TEXT_BOTTOM=214; // +5 frame shift => last glyph row219,20px from panel bottom.
inline void clipSessionTitle(const char* text,int maxWidth,char (&clipped)[164]){
  unsigned n=0;clipped[0]=0;const char* p=text;
  while(*p){const char* next=p;utf8Next(next);unsigned bytes=unsigned(next-p);if(n+bytes>160)break;memcpy(clipped+n,p,bytes);clipped[n+bytes]=0;
    if(textWidth(clipped,actionFont)>maxWidth){clipped[n]=0;while(n && textWidth(clipped,actionFont)+textWidth("...",actionFont)>maxWidth){unsigned start=n-1;while(start && (uint8_t(clipped[start])&0xC0)==0x80)--start;n=start;clipped[n]=0;}strcat(clipped,"...");break;}n+=bytes;p=next;}
}
inline int textInkBottom(const char* text,const Font& font){
  int bottom=-1000;
  while(*text){const Glyph& g=glyphFor(font,utf8Next(text));
    for(int y=g.h-1;y>=0;y--){bool ink=false;for(int x=0;x<g.w;x++){
      unsigned n=unsigned(y)*g.w+x;uint8_t packed=font.pixels[g.offset+n/2];if((n%2?packed&15:packed>>4)){ink=true;break;}
    }if(ink){if(g.y+y>bottom)bottom=g.y+y;break;}}
  }
  return bottom;
}
inline void renderSingleTask(Canvas& c,const SessionList& list,TaskView& view,uint32_t now,State fallback=State::Idle,const DisplayText* text=nullptr){
  c.rect(0,155,W,85,0);int index=view.selected(list,now);
  const char* title=index>=0?list.rows[index].title:text && text->title[0]?text->title:"Codex";
  if(!title[0])title="Codex";
  char state=index>=0?list.rows[index].state:fallback==State::Processing?'P':fallback==State::Thinking?'T':fallback==State::Ask?'A':'I';
  const char* reply=index>=0?list.rows[index].reply:"";
  char counter[24]{},status[12]{},body[328]{};int end=226,counterX=226;
  if(list.valid && list.count>1){snprintf(counter,sizeof(counter),"%u/%u%s",unsigned(index)+1,list.count,list.total>list.count?"+":"");counterX-=textWidth(counter,actionFont);end=counterX-8;}
  snprintf(status,sizeof(status),"[%s]",sessionStateLabel(state));
  snprintf(body,sizeof(body),"%s%s%s",title,reply[0]?" .. ":"",reply);
  int start=12+textWidth(status,actionFont)+8;
  int bottom=textInkBottom(body,actionFont),statusBottom=textInkBottom(status,actionFont),counterBottom=textInkBottom(counter,actionFont);
  if(statusBottom>bottom)bottom=statusBottom;if(counterBottom>bottom)bottom=counterBottom;
  int baseline=TASK_TEXT_BOTTOM-(bottom>-1000?bottom:0);
  // Reset on this session's actual content/state only, never on heartbeat/reorder.
  uint32_t hash=2166136261u;
  const char* parts[]={index>=0?list.rows[index].id:"",status,body};
  for(const char* part:parts)for(const char* p=part;*p;p++)hash=(hash^uint8_t(*p))*16777619u;
  if(!view.tickerSet || view.tickerHash!=hash){view.tickerHash=hash;view.tickerAt=now;view.tickerSet=true;}
  int width=textWidth(body,actionFont),available=end-start,offset=0;
  if(width>available){uint32_t phase=uint32_t(now-view.tickerAt)%(1200+uint32_t(width+32)*40);if(phase>1200)offset=int((phase-1200)/40);}
  drawText(c,body,actionFont,start-offset,baseline,rgb(242,244,247),186,225,start,end);
  if(width>available && offset>width+32-available)drawText(c,body,actionFont,start+width+32-offset,baseline,rgb(242,244,247),186,225,start,end);
  drawText(c,status,actionFont,12,baseline,sessionStateColor(state),186,225);
  if(counter[0])drawText(c,counter,actionFont,counterX,baseline,rgb(150,155,165),186,225);
}
// Kept for existing framebuffer previews; device loop uses persistent TaskView.
inline void renderSessionList(Canvas& c,const SessionList& list,uint32_t now){TaskView view;renderSingleTask(c,list,view,now);}
} // namespace pet
