#pragma once
#include <stdint.h>
#include <math.h>
namespace pet {
struct IdlePose {
  int gaze=0,lift=0,mouthOpen=0;
  bool lids=false,sleepy=false;
};
inline IdlePose idlePose(uint32_t elapsed,uint32_t now,bool petting) {
  IdlePose pose;
  if(petting) {
    pose.gaze=int(sinf(now*.008f)*4);
    pose.lift=int(sinf(now*.012f)*3);
    pose.lids=true;return pose;
  }
  if(elapsed>=600000) {pose.lids=pose.sleepy=true;return pose;}
  uint32_t phase=elapsed%24000;
  if(phase>=4000 && phase<7000)
    pose.gaze=int(sinf((phase-4000)*.0020943951f)*9);
  else if(phase>=12000 && phase<14000)
    pose.lift=-int(sinf((phase-12000)*.0015707963f)*5);
  else if(phase>=19000 && phase<21000) {
    pose.mouthOpen=int(sinf((phase-19000)*.0015707963f)*10);
    pose.lids=pose.mouthOpen>1;
  }
  return pose;
}
} // namespace pet
