#pragma once
#include <stdint.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "pet_logic.h"
#include "led_colors.h"
#include "text_protocol.h"
#include "font_rasters.h"
#include "personality.h"
#include "activity.h"
#include "fun.h"
namespace pet {
constexpr int W=240,H=240;
inline uint16_t rgb(uint8_t r,uint8_t g,uint8_t b) { return uint16_t((r>>3)<<11 | (g>>2)<<5 | (b>>3)); }
inline uint16_t swap16(uint16_t a) { return uint16_t(a<<8 | a>>8); }
constexpr uint16_t ORANGE=uint16_t((0xD9>>3)<<11 | (0x77>>2)<<5 | (0x57>>3));
struct Canvas {
  uint16_t* fb;
  int y0,h;
  Canvas(uint16_t* f,int top=0,int rows=H):fb(f),y0(top),h(rows){}
  // window: rows [y0,y0+h) of the 240-row frame map to fb rows 0..h-1 (half-height RAM budget)
  void clear() { memset(fb,0,W*h*sizeof(uint16_t)); }
  void pixel(int x,int y,uint16_t c) { if(x>=0 && y>=y0 && x<W && y<y0+h) fb[(y-y0)*W+x]=swap16(c); }
  void rect(int x,int y,int w,int h,uint16_t c) {
    for(int j=y;j<y+h;j++) for(int i=x;i<x+w;i++) pixel(i,j,c);
  }
  void circle(int x,int y,int r,uint16_t c) {
    for(int j=-r;j<=r;j++) for(int i=-r;i<=r;i++) if(i*i+j*j<=r*r) pixel(x+i,y+j,c);
  }
  void roundRect(int x,int y,int w,int h,int r,uint16_t c) {
    if(w<=0 || h<=0) return;
    r=r<w/2?r:w/2; r=r<h/2?r:h/2;
    rect(x+r,y,w-2*r,h,c); rect(x,y+r,r,h-2*r,c); rect(x+w-r,y+r,r,h-2*r,c);
    circle(x+r,y+r,r,c); circle(x+w-r-1,y+r,r,c);
    circle(x+r,y+h-r-1,r,c); circle(x+w-r-1,y+h-r-1,r,c);
  }
  void line(int x0,int y0,int x1,int y1,int thickness,uint16_t c) {
    int dx=abs(x1-x0), sx=x0<x1?1:-1,dy=-abs(y1-y0),sy=y0<y1?1:-1,e=dx+dy;
    for(;;) { circle(x0,y0,thickness/2,c); if(x0==x1 && y0==y1) break; int t=2*e; if(t>=dy) {e+=dy;x0+=sx;} if(t<=dx) {e+=dx;y0+=sy;} }
  }
  void softCapsule(int cx,int cy,int width,int height,int tiltDegrees,uint16_t color) {
    if(width<=0 || height<=0) return;
    // A filled pill with round ends, a one-pixel soft edge and a small glow.
    // Rotate once per eye; all per-pixel distances use fixed-point arithmetic.
    int minor=width<height?width:height,major=width>height?width:height;
    int radius256=minor*128,segment256=(major-minor)*128;
    float angle=tiltDegrees*.0174532925f;
    int co=int(cosf(angle)*256),si=int(sinf(angle)*256);
    int radius2=radius256*radius256/256;
    int edge2=(radius256+256)*(radius256+256)/256;
    int halo2=(radius256+4*256)*(radius256+4*256)/256;
    int bound=major/2+5;
    for(int y=cy-bound;y<=cy+bound;y++) for(int x=cx-bound;x<=cx+bound;x++) {
      int dx=x-cx,dy=y-cy;
      int u=dx*co-dy*si,v=dx*si+dy*co;
      int along=height>=width?v:u,across=height>=width?u:v;
      int excess=abs(along)-segment256;if(excess<0) excess=0;
      int distance2=(across*across+excess*excess)/256;
      if(distance2>=halo2) continue;
      int alpha=(halo2-distance2)*22/(halo2-radius2);
      if(distance2<=radius2) alpha=255;
      else if(distance2<edge2) {
        int edge=(edge2-distance2)*255/(edge2-radius2);
        if(edge>alpha) alpha=edge;
      }
      uint16_t shaded=uint16_t((((color>>11)&31)*alpha/255)<<11 |
                               (((color>>5)&63)*alpha/255)<<5 |
                               (color&31)*alpha/255);
      pixel(x,y,shaded);
    }
  }
  void text(const char* word,int x,int y,int scale,uint16_t c) {
    // Original compact 5x7 block alphabet, bits run left-to-right.
    static const uint8_t font[26][7]={
      {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
      {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
      {14,17,16,23,17,17,14},{17,17,17,31,17,17,17},{31,4,4,4,4,4,31},
      {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
      {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
      {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
      {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
      {17,17,17,17,17,10,4},{17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
      {17,17,10,4,4,4,4},{31,1,2,4,8,16,31}};
    for(;*word;word++,x+=6*scale) if(*word>='A' && *word<='Z') {
      for(int j=0;j<7;j++) for(int i=0;i<5;i++) if(font[*word-'A'][j]&(16>>i)) rect(x+i*scale,y+j*scale,scale,scale,c);
    }
  }
  void centered(const char* s,int y,int scale,uint16_t c) { text(s,(W-int(strlen(s))*6*scale+scale)/2,y,scale,c); }
};
inline const Glyph& glyphFor(const Font& font,uint32_t code) {
  unsigned low=0,high=font.count;
  while(low<high) {unsigned mid=(low+high)/2;if(font.glyphs[mid].code<code) low=mid+1;else high=mid;}
  if(low<font.count && font.glyphs[low].code==code) return font.glyphs[low];
  return font.glyphs['?'-32];
}
inline int textWidth(const char* text,const Font& font) {
  int width=0;while(*text) width+=glyphFor(font,utf8Next(text)).advance;return width;
}
inline void drawText(Canvas& c,const char* text,const Font& font,int x,int baseline,uint16_t color,int clipTop=145,int clipBottom=234,int clipLeft=12,int clipRight=228) {
  while(*text) {
    const Glyph& g=glyphFor(font,utf8Next(text));
    int gx=x+g.x,gy=baseline+g.y;
    if(gx+g.w>=clipLeft && gx<clipRight) for(int j=0;j<g.h;j++) for(int i=0;i<g.w;i++) {
      int px=gx+i,py=gy+j;if(px<clipLeft || px>=clipRight || py<clipTop || py>=clipBottom) continue;
      unsigned n=unsigned(j)*g.w+i;uint8_t packed=font.pixels[g.offset+n/2];
      unsigned alpha=n%2?packed&15:packed>>4;if(!alpha) continue;
      uint16_t shade=uint16_t((((color>>11)&31)*alpha/15)<<11 | (((color>>5)&63)*alpha/15)<<5 | (color&31)*alpha/15);
      c.pixel(px,py,shade);
    }
    x+=g.advance;
  }
}
inline void scrollingText(Canvas& c,const char* text,const Font& font,int baseline,uint16_t color,uint32_t elapsed) {
  int width=textWidth(text,font),offset=0;
  if(width>216) {
    uint32_t phase=elapsed%(1500+uint32_t(width+32)*35);
    if(phase>1500) offset=int((phase-1500)/35);
  }
  drawText(c,text,font,12-offset,baseline,color);
  if(width>216 && offset>width+32-216) drawText(c,text,font,12+width+32-offset,baseline,color);
}
inline void curvedStroke(Canvas& c,int cx,int cy,int halfWidth,int arch,int thickness,uint16_t color) {
  int previous=cy+arch;
  for(int x=-halfWidth+1;x<=halfWidth;x++) {
    int y=cy+arch*x*x/(halfWidth*halfWidth);
    c.line(cx+x-1,previous,cx+x,y,thickness,color);previous=y;
  }
}
inline void mouthOval(Canvas& c,int cx,int cy,int width,int height,uint16_t color) {
  c.softCapsule(cx,cy,width,height,0,color);
  if(width>4 && height>4) c.roundRect(cx-(width-4)/2,cy-(height-4)/2,width-4,height-4,1,0);
}
inline void heartIcon(Canvas& c,int x,int y,uint16_t color) {
  c.circle(x-4,y,4,color);c.circle(x+4,y,4,color);
  for(int row=0;row<10;row++) c.rect(x-(9-row),y+row,2*(9-row)+1,1,color);
}
inline void dreamBubble(Canvas& c,int kind,uint32_t elapsed) {
  int cx=213,cy=65-int((elapsed%40000-30000)/1000);
  uint16_t edge=rgb(90,170,200),ink=rgb(140,220,255);
  c.circle(cx,cy,12,edge);c.circle(cx,cy,10,0);
  c.circle(cx-9,cy+17,3,edge);c.circle(cx-15,cy+23,2,edge);
  if(kind==0) {
    c.softCapsule(cx-2,cy,15,8,0,ink);
    c.line(cx+4,cy,cx+10,cy-5,2,ink);c.line(cx+4,cy,cx+10,cy+5,2,ink);
    c.pixel(cx-6,cy-1,0);
  } else if(kind==1) {
    c.rect(cx-7,cy-2,11,9,ink);c.rect(cx-5,cy,7,5,0);
    c.line(cx+4,cy-1,cx+8,cy+1,1,ink);c.line(cx+8,cy+1,cx+4,cy+5,1,ink);
    c.line(cx-3,cy-8,cx-5,cy-4,1,ink);c.line(cx+2,cy-9,cx,cy-5,1,ink);
  } else {
    c.line(cx-8,cy-5,cx-3,cy,2,ink);c.line(cx-3,cy,cx-8,cy+5,2,ink);
    c.line(cx+1,cy+5,cx+8,cy+5,2,ink);
  }
}
inline void dimFrame(Canvas& c) {
  for(int i=0;i<W*c.h;i++) {
    uint16_t v=swap16(c.fb[i]);
    c.fb[i]=swap16(uint16_t((((v>>11)&31)/12)<<11 | (((v>>5)&63)/12)<<5 | (v&31)/12));
  }
}
// Original raster geometry inspired by the user's twelve-expression reference.
// Screen brightness is independent from the LED pulse; open eyes never fade to zero.
enum class EyeStyle:uint8_t {Neutral,Sceptic,Sad,Broken,Tired,Crazy,Wink,Surprised,Angry,Love,Happy,Denying};
inline uint16_t eyeInk(State state) {
  LedColor hue=stateHue(state);return rgb(hue.r,hue.g,hue.b);
}
inline void glowLine(Canvas& c,int x0,int y0,int x1,int y1,int width,uint16_t color) {
  uint16_t halo=uint16_t((((color>>11)&31)/5)<<11 | (((color>>5)&63)/5)<<5 | (color&31)/5);
  c.line(x0,y0,x1,y1,width+4,halo);c.line(x0,y0,x1,y1,width,color);
}
inline void robotBox(Canvas& c,int cx,int cy,int width,int height,int radius,int tilt,uint16_t color) {
  if(width<1||height<1)return;
  radius=radius<width/2?radius:width/2;radius=radius<height/2?radius:height/2;
  float angle=tilt*.0174532925f;int co=int(cosf(angle)*256),si=int(sinf(angle)*256);
  int rx=(width/2-radius)*256,ry=(height/2-radius)*256;
  int r=radius*256,r2=r*r/256,edge2=(r+256)*(r+256)/256,halo2=(r+3*256)*(r+3*256)/256;
  int bound=tilt?(width+height)/2+4:(width>height?width:height)/2+4;
  for(int y=cy-bound;y<=cy+bound;y++)for(int x=cx-bound;x<=cx+bound;x++) {
    int dx=x-cx,dy=y-cy,u=abs(dx*co-dy*si)-rx,v=abs(dx*si+dy*co)-ry;
    if(u<0)u=0;if(v<0)v=0;int d2=(u*u+v*v)/256;if(d2>=halo2)continue;
    int alpha=d2<=r2?255:(halo2-d2)*25/(halo2-r2);
    if(d2>r2&&d2<edge2){int edge=(edge2-d2)*255/(edge2-r2);if(edge>alpha)alpha=edge;}
    uint16_t shade=uint16_t((((color>>11)&31)*alpha/255)<<11 | (((color>>5)&63)*alpha/255)<<5 | (color&31)*alpha/255);
    c.pixel(x,y,shade);
  }
}
inline void robotRing(Canvas& c,int cx,int cy,int w,int h,uint16_t color) {
  int inset=10;robotBox(c,cx,cy,w,h,w/2,0,color);
  c.roundRect(cx-w/2+inset,cy-h/2+inset,w-2*inset+1,h-2*inset+1,(w-2*inset+1)/2,0);
}
inline void robotHeart(Canvas& c,int cx,int cy,uint16_t color) {
  c.circle(cx-14,cy-11,16,color);c.circle(cx+14,cy-11,16,color);
  for(int y=0;y<=32;y++){int half=32-y;c.rect(cx-half,cy-1+y,half*2+1,1,color);}
}
inline void robotEyes(Canvas& c,EyeStyle style,int gaze,int cy,int openness,uint16_t color=eyeInk(State::Idle)) {
  int x0=74+gaze,x1=166+gaze;
  if(openness<55 && style!=EyeStyle::Tired) {
    int h=openness*60/65;if(h<4)h=4;
    c.softCapsule(x0,cy,60,h,0,color);c.softCapsule(x1,cy,60,h,0,color);return;
  }
  switch(style) {
    case EyeStyle::Neutral:
      robotBox(c,x0,cy,60,80,14,0,color);robotBox(c,x1,cy,60,80,14,0,color);break;
    case EyeStyle::Sceptic:
      robotBox(c,x0,cy,62,24,8,-3,color);robotBox(c,x1,cy-1,60,34,10,3,color);break;
    case EyeStyle::Sad:
      robotBox(c,x0,cy,54,28,8,28,color);robotBox(c,x1,cy,54,28,8,-28,color);break;
    case EyeStyle::Broken:
      for(int x:{x0,x1}){glowLine(c,x-24,cy-24,x+24,cy+24,10,color);glowLine(c,x-24,cy+24,x+24,cy-24,10,color);}break;
    case EyeStyle::Tired:
      curvedStroke(c,x0,cy,28,-14,8,color);curvedStroke(c,x1,cy,28,-14,8,color);break;
    case EyeStyle::Crazy:
      robotRing(c,x0,cy+8,50,62,color);robotRing(c,x1,cy-4,66,84,color);break;
    case EyeStyle::Wink:
      curvedStroke(c,x0,cy-8,28,18,10,color);robotBox(c,x1,cy,60,80,14,0,color);break;
    case EyeStyle::Surprised:
      robotRing(c,x0,cy,60,80,color);robotRing(c,x1,cy,60,80,color);break;
    case EyeStyle::Angry:
      robotBox(c,x0,cy,62,24,8,-20,color);robotBox(c,x1,cy,62,24,8,20,color);break;
    case EyeStyle::Love:
      robotHeart(c,x0,cy,color);robotHeart(c,x1,cy,color);break;
    case EyeStyle::Happy:
      curvedStroke(c,x0,cy-10,28,20,10,color);curvedStroke(c,x1,cy-10,28,20,10,color);break;
    case EyeStyle::Denying:
      glowLine(c,x0-20,cy-24,x0+18,cy,10,color);glowLine(c,x0+18,cy,x0-20,cy+24,10,color);
      glowLine(c,x1+20,cy-24,x1-18,cy,10,color);glowLine(c,x1-18,cy,x1+20,cy+24,10,color);break;
  }
}
inline EyeStyle expression(State state,uint32_t elapsed,bool sleepy,bool waking,bool combo,bool celebrating,bool petting,const Fun* fun) {
  if(state==State::Idle) {
    if(sleepy)return EyeStyle::Tired;
    if(waking)return EyeStyle::Surprised;
    if(combo)return EyeStyle::Love;
    if(celebrating)return elapsed%1000<600?EyeStyle::Happy:EyeStyle::Love;
    if(petting)return EyeStyle::Happy;
    return elapsed%24000>=16000&&elapsed%24000<17400?EyeStyle::Wink:EyeStyle::Neutral;
  }
  if(state==State::Thinking)return elapsed%3600<1800?EyeStyle::Sceptic:EyeStyle::Wink;
  if(state==State::Processing) {
    if(fun&&fun->mood==ToolMood::Test)return EyeStyle::Crazy;
    if(fun&&fun->mood==ToolMood::Edit)return EyeStyle::Angry;
    return EyeStyle::Sceptic;
  }
  if(state==State::Ask)return EyeStyle::Surprised;
  if(state==State::Accepted)return EyeStyle::Happy;
  return elapsed<300?EyeStyle::Sad:elapsed<600?EyeStyle::Denying:EyeStyle::Broken;
}
inline void render(Canvas& c,State state,uint32_t now,int blinkHeight,Press poke,bool held,bool connected,uint32_t stateElapsed,const DisplayText* display=nullptr,uint32_t heldElapsed=0,const Activity* activity=nullptr,const Fun* fun=nullptr) {
  (void)connected; // USB status remains in the protocol, not on the clean face.
  c.clear();
  // Touch feedback is decoration for Idle; it never masks a busy/approval face.
  bool sleeping=fun && fun->sleeping;
  bool waking=fun && fun->waking && state==State::Idle && uint32_t(now-fun->wakeAt)<1200;
  bool combo=fun && fun->heart && state==State::Idle && uint32_t(now-fun->heartAt)<1800 && !sleeping;
  bool petting=state==State::Idle && !sleeping && ((held && heldElapsed>=800) || poke==Press::Long);
  Press reaction=state==State::Idle && !sleeping?poke:Press::None;
  bool celebrating=activity && activity->active && !activity->sessions && state==State::Idle && uint32_t(now-activity->started)<1000 && !petting && reaction==Press::None && !sleeping && !combo && !waking;
  State wireState=state;
  IdlePose pose=state==State::Idle?idlePose(stateElapsed,now,petting):IdlePose{};
  int gaze=wireState==State::Idle?pose.gaze:wireState==State::Thinking?int(sinf(now*.002f)*7):0;
  int y=111+(wireState==State::Idle?pose.lift:0);
  if(wireState==State::Processing && fun && fun->mood==ToolMood::Read){y+=6;gaze=int(sinf(now*.003f)*8);}
  bool sleepy=sleeping || (wireState==State::Idle && (pose.sleepy || pose.lids));
  EyeStyle style=expression(wireState,celebrating?uint32_t(now-activity->started):stateElapsed,sleepy,waking,combo,celebrating,petting || reaction!=Press::None,fun);
  bool ledCelebration=activity && activity->active && wireState==State::Idle;
  robotEyes(c,style,gaze,y,blinkHeight,eyeInk(ledCelebration?State::Accepted:wireState));
  // Face consists only of eyes; multi-session count lives on the task row.
  // Love is carried by both eyes; no icon competes with the inset clock.
  int dream=dreamKind(stateElapsed);
  if(wireState==State::Idle && dream>=0 && !sleeping && !waking && !combo && !celebrating && !petting && reaction==Press::None && (!activity || !activity->sessions)) dreamBubble(c,dream,stateElapsed);
  const char* title=display && display->title[0]?display->title:"Codex";
  const char* action=display && display->action[0]?display->action:defaultAction(wireState);
  scrollingText(c,title,titleFont,204,rgb(255,255,255),display?uint32_t(now-display->titleAt):0);
  scrollingText(c,action,actionFont,230,rgb(160,164,172),display?uint32_t(now-display->actionAt):0);
  if(sleeping) dimFrame(c);
}
} // namespace pet
