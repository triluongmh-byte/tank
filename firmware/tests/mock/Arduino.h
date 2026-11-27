#pragma once
#include <stdint.h>
#include <stddef.h>
#define HIGH 1
#define LOW 0
#define OUTPUT 1
#define INPUT 0
#define CHANGE 3
#define IRAM_ATTR
struct portMUX_TYPE {int unused;};
#define portMUX_INITIALIZER_UNLOCKED {0}
#define portENTER_CRITICAL(x) (void)(x)
#define portEXIT_CRITICAL(x) (void)(x)
#define portENTER_CRITICAL_ISR(x) (void)(x)
#define portEXIT_CRITICAL_ISR(x) (void)(x)
extern int levels[64];extern uint32_t fakeMicros;
inline void digitalWrite(int pin,int value){levels[pin]=value;}
inline int digitalRead(int pin){return levels[pin];}
inline void pinMode(int,int){}
inline uint32_t micros(){return fakeMicros;}
inline void delayMicroseconds(unsigned){}
inline void attachInterruptArg(int,void(*)(void*),void*,int){}
