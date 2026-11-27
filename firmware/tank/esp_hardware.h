#pragma once
#include <Arduino.h>
#include <Wire.h>
#include <Preferences.h>
#include <esp_timer.h>
#include "controller.h"
#include "pca9685.h"
#include "calibration_store.h"
namespace tank {
// Timer and loop share a lock: a deadline trip latches until a fresh safe ARM initialization.
static portMUX_TYPE safetyMux=portMUX_INITIALIZER_UNLOCKED;
static volatile bool safetyTrip=false,safetyActive=false;
static bool prerequisitesReady=true;
static volatile uint32_t safetyDue=0;
inline void inhibitPins(){digitalWrite(OE_PIN,HIGH);digitalWrite(ACT_PIN,LOW);}
inline void guard(void*) {
  portENTER_CRITICAL(&safetyMux);
  if(digitalRead(STOP_PIN)==LOW || digitalRead(BOOT_PIN)==LOW || (safetyActive&&int32_t(micros()-safetyDue)>=0)) {
    inhibitPins();safetyTrip=true;safetyActive=false;
  }
  portEXIT_CRITICAL(&safetyMux);
}
struct I2cBus {
  bool write(uint8_t reg,const uint8_t* bytes,unsigned n) {
    Wire.beginTransmission(uint8_t(PCA_ADDRESS));Wire.write(reg);if(Wire.write(bytes,n)!=n){Wire.endTransmission();return false;}return Wire.endTransmission()==0;
  }
  bool read(uint8_t reg,uint8_t* bytes,unsigned n) {
    Wire.beginTransmission(uint8_t(PCA_ADDRESS));Wire.write(reg);if(Wire.endTransmission(false)!=0)return false;
    if(Wire.requestFrom(uint8_t(PCA_ADDRESS),uint8_t(n))!=n)return false;
    for(unsigned i=0;i<n;i++)bytes[i]=Wire.read();return true;
  }
  void waitUs(unsigned us){delayMicroseconds(us);}
};
class EspHardware:public Hardware {
  I2cBus bus;Pca9685<I2cBus> pca{bus};Preferences prefs;
public:
  void gate(bool off) override {
    portENTER_CRITICAL(&safetyMux);
    digitalWrite(OE_PIN,(off||safetyTrip)?HIGH:LOW);
    portEXIT_CRITICAL(&safetyMux);
  }
  void power(bool on)override {
    portENTER_CRITICAL(&safetyMux);
    digitalWrite(ACT_PIN,(on&&!safetyTrip&&prerequisitesReady)?HIGH:LOW);
    if(on&&!safetyTrip&&prerequisitesReady){safetyDue=micros()+100000u;safetyActive=true;}else safetyActive=false;
    portEXIT_CRITICAL(&safetyMux);
  }
  bool initialize()override {
    inhibitPins();if(!prerequisitesReady)return false;bool ok=pca.begin();
    if(ok){portENTER_CRITICAL(&safetyMux);if(digitalRead(STOP_PIN)&&digitalRead(BOOT_PIN)){safetyTrip=false;safetyActive=false;}portEXIT_CRITICAL(&safetyMux);}return ok;
  }
  bool frame(const uint16_t (&us)[16])override{return pca.frame(us);}
  bool healthy()override{return pca.healthy();}
  bool save(const Calibration& cal)override {
    if(!cal.valid()||!prefs.begin("pet-tank",false))return false;
    uint8_t b[CAL_SIZE];encode(cal,b);bool ok=prefs.putBytes("cal-v1",b,sizeof(b))==sizeof(b);prefs.end();return ok;
  }
  void load(Calibration& cal){if(!prefs.begin("pet-tank",true))return;uint8_t b[CAL_SIZE]{};if(prefs.getBytesLength("cal-v1")==sizeof(b)&&prefs.getBytes("cal-v1",b,sizeof(b))==sizeof(b))decode(b,cal);prefs.end();}
};
struct EchoIO {
  volatile uint32_t rise[2]{},width[2]{};volatile bool armed[2]{},ready[2]{};
  portMUX_TYPE mux=portMUX_INITIALIZER_UNLOCKED;
  struct Arg{EchoIO* self;unsigned n;} args[2]={{this,0},{this,1}};
  static void IRAM_ATTR edge(void* ptr);
  void begin(){for(unsigned i=0;i<2;i++){digitalWrite(TRIG_PINS[i],LOW);pinMode(TRIG_PINS[i],OUTPUT);pinMode(ECHO_PINS[i],INPUT);attachInterruptArg(ECHO_PINS[i],edge,&args[i],CHANGE);}}
  void trigger(unsigned i,bool high){digitalWrite(TRIG_PINS[i],high);}
  bool echo(unsigned i){return digitalRead(ECHO_PINS[i]);}
  void clear(unsigned i){portENTER_CRITICAL(&mux);armed[i]=ready[i]=false;portEXIT_CRITICAL(&mux);}
  bool takePulse(unsigned i,uint32_t& out){portENTER_CRITICAL(&mux);bool hit=ready[i];if(hit){out=width[i];ready[i]=false;}portEXIT_CRITICAL(&mux);return hit;}
};
}
