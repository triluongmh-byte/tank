#include "esp_hardware.h"
namespace tank {
void IRAM_ATTR EchoIO::edge(void* ptr) {
    auto* a=static_cast<Arg*>(ptr);auto& io=*a->self;unsigned i=a->n;uint32_t now=micros();
    portENTER_CRITICAL_ISR(&io.mux);
    if(digitalRead(ECHO_PINS[i])){io.rise[i]=now;io.armed[i]=true;}
    else if(io.armed[i]){io.width[i]=now-io.rise[i];io.ready[i]=true;io.armed[i]=false;}
    portEXIT_CRITICAL_ISR(&io.mux);
  }
}
