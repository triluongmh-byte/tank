#include <assert.h>
#include <iostream>
#include "esp_hardware.h"
int levels[64]{};uint32_t fakeMicros=0;MockWire Wire;
int main(){
 using namespace tank;levels[STOP_PIN]=levels[BOOT_PIN]=HIGH;EspHardware hw;
 assert(hw.initialize());hw.power(true);hw.gate(false);assert(levels[ACT_PIN]==HIGH&&levels[OE_PIN]==LOW&&safetyActive);
 fakeMicros=100000;guard(nullptr);assert(safetyTrip&&levels[ACT_PIN]==LOW&&levels[OE_PIN]==HIGH);
 hw.power(true);hw.gate(false);assert(levels[ACT_PIN]==LOW&&levels[OE_PIN]==HIGH);
 assert(hw.initialize());hw.power(true);hw.gate(false);levels[STOP_PIN]=LOW;guard(nullptr);assert(levels[ACT_PIN]==LOW&&levels[OE_PIN]==HIGH);
 assert(hw.initialize());hw.power(true);hw.gate(false);assert(levels[ACT_PIN]==LOW&&levels[OE_PIN]==HIGH); // held cannot reset latch
 levels[STOP_PIN]=HIGH;hw.power(true);assert(levels[ACT_PIN]==LOW); // release does not rearm
 assert(hw.initialize());fakeMicros=0xFFFFFFF0u;hw.power(true);hw.gate(false);fakeMicros+=99999;guard(nullptr);assert(!safetyTrip);fakeMicros++;guard(nullptr);assert(safetyTrip);
 assert(hw.initialize());hw.power(true);hw.gate(false);levels[BOOT_PIN]=LOW;guard(nullptr);assert(safetyTrip&&levels[ACT_PIN]==LOW);
 levels[BOOT_PIN]=HIGH;prerequisitesReady=false;assert(!hw.initialize());hw.power(true);hw.gate(false);assert(levels[ACT_PIN]==LOW);
 std::cout<<"PASS production guard mock\n";
}
