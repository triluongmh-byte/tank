#pragma once
// Bounded minimal HTTP/1.x request parser for the phone UI. Pure C++, host-testable; no allocation.
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <stdio.h>
namespace tank {
constexpr size_t HTTP_MAX=1800;      // whole request incl. headers + body; larger is rejected
enum class HttpState:uint8_t {Need,Ready,Bad};
struct HttpRequest {
  char method[8]{};char path[64]{};char query[160]{};char body[260]{};size_t bodyLen=0;
  // Parameter lookup across query then urlencoded body; decodes %XX and '+'. false if absent/too long.
  static bool find(const char* src,const char* name,char* out,size_t cap) {
    size_t n=strlen(name);const char* p=src;
    while(*p) {
      const char* e=strchr(p,'&');size_t len=e?size_t(e-p):strlen(p);
      if(len>n&&!strncmp(p,name,n)&&p[n]=='=') {
        size_t o=0;
        for(size_t i=n+1;i<len;i++) {
          char c=p[i];
          if(c=='+')c=' ';
          else if(c=='%'){
            auto hv=[](char h)->int{return h>='0'&&h<='9'?h-'0':h>='a'&&h<='f'?h-'a'+10:h>='A'&&h<='F'?h-'A'+10:-1;};
            if(i+2>=len)return false;int a=hv(p[i+1]),b=hv(p[i+2]);if(a<0||b<0)return false;c=char(a*16+b);i+=2;
          }
          if(o+1>=cap||c==0)return false;out[o++]=c;
        }
        out[o]=0;return true;
      }
      if(!e)break;p=e+1;
    }
    return false;
  }
  bool param(const char* name,char* out,size_t cap)const{return find(query,name,out,cap)||find(body,name,out,cap);}
  // Unsigned decimal, at most 10 digits, fits uint32.
  bool uintParam(const char* name,uint32_t& v)const {
    char s[16];if(!param(name,s,sizeof(s))||!*s||strlen(s)>10)return false;
    uint64_t x=0;for(const char* p=s;*p;p++){if(*p<'0'||*p>'9')return false;x=x*10+uint64_t(*p-'0');if(x>0xffffffffULL)return false;}
    v=uint32_t(x);return true;
  }
};
// Parses buf[0..n). Need = incomplete (read more). Bad = malformed/oversize/unsupported (reply 400 and close).
inline HttpState parseHttp(const char* buf,size_t n,HttpRequest& r) {
  r=HttpRequest{};
  if(n>HTTP_MAX)return HttpState::Bad;
  const char* end=nullptr;for(size_t i=0;i+3<n;i++)if(!memcmp(buf+i,"\r\n\r\n",4)){end=buf+i;break;}
  {size_t scan=end?size_t(end-buf):n;for(size_t i=0;i<scan;i++){uint8_t ch=uint8_t(buf[i]);if(ch!='\r'&&ch!='\n'&&(ch<32||ch>126))return HttpState::Bad;}}
  if(!end){
    return n>=1024?HttpState::Bad:HttpState::Need;
  }
  size_t head=size_t(end-buf);
  const char* sp1=(const char*)memchr(buf,' ',head);if(!sp1)return HttpState::Bad;
  size_t ml=size_t(sp1-buf);if(ml==0||ml>=sizeof(r.method))return HttpState::Bad;
  memcpy(r.method,buf,ml);
  if(strcmp(r.method,"GET")&&strcmp(r.method,"POST")&&strcmp(r.method,"HEAD"))return HttpState::Bad;
  const char* t=sp1+1;const char* sp2=(const char*)memchr(t,' ',size_t(buf+head-t));if(!sp2)return HttpState::Bad;
  if(sp2-t<1||*t!='/')return HttpState::Bad;
  if(buf+head-sp2<9||memcmp(sp2+1,"HTTP/1.",7))return HttpState::Bad;
  const char* q=(const char*)memchr(t,'?',size_t(sp2-t));
  size_t pl=size_t((q?q:sp2)-t);if(pl>=sizeof(r.path))return HttpState::Bad;
  memcpy(r.path,t,pl);
  if(q){size_t ql=size_t(sp2-q-1);if(ql>=sizeof(r.query))return HttpState::Bad;memcpy(r.query,q+1,ql);}
  // Headers: only Content-Length matters; chunked bodies are refused.
  size_t len=0;bool haveLen=false;
  const char* line=(const char*)memchr(buf,'\n',head);
  while(line&&line<buf+head) {
    line++;const char* e=(const char*)memchr(line,'\r',size_t(buf+head+2-line));if(!e)e=buf+head;
    size_t ll=size_t(e-line);
    if(ll>=15&&!strncasecmp(line,"content-length:",15)){
      const char* p=line+15;while(p<e&&*p==' ')p++;if(p==e||haveLen)return HttpState::Bad;
      size_t v=0;for(;p<e;p++){if(*p<'0'||*p>'9')return HttpState::Bad;v=v*10+size_t(*p-'0');if(v>sizeof(r.body))return HttpState::Bad;}
      len=v;haveLen=true;
    } else if(ll>=18&&!strncasecmp(line,"transfer-encoding:",18))return HttpState::Bad;
    line=(const char*)memchr(line,'\n',size_t(buf+head+2-line));
  }
  size_t have=n-(head+4);
  if(have<len)return HttpState::Need;
  if(have>len)return HttpState::Bad;          // pipelining/extra bytes: refuse
  if(len>=sizeof(r.body))return HttpState::Bad;
  memcpy(r.body,end+4,len);r.body[len]=0;r.bodyLen=len;
  return HttpState::Ready;
}
}
