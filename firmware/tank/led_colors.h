#pragma once
#include "pet_logic.h"
namespace pet {
// Hand-wired optional pixels; these GPIOs have no load on the carrier copper.
constexpr int LED_DATA_1=5, LED_DATA_2=10;
struct LedColor { uint8_t r,g,b; };
constexpr uint8_t LED_BRIGHTNESS=32;
// One palette for the physical LEDs and the eyes; brightness is independent.
inline LedColor stateHue(State state,uint8_t brightness=255) {
  switch(state) {
    case State::Idle:return {0,uint8_t(brightness*3/4),brightness};
    case State::Thinking:return {brightness,0,brightness};
    case State::Processing:return {brightness,uint8_t(brightness*2/3),0};
    case State::Ask:case State::Cancelled:return {brightness,0,0};
    case State::Accepted:return {0,brightness,0};
  }
  return {0,0,0};
}
inline uint8_t breath(uint32_t elapsed,uint32_t period,uint8_t brightness) {
  uint32_t phase=elapsed%period;
  uint32_t triangle=phase<period/2?phase:period-phase;
  return uint8_t(triangle*brightness/(period/2));
}
// Palette and timing adapted read-only from claude-macropad/firmware/deck/deck.ino
// paintLed(). Brightness is separate: LEDs 32, screen 255; both share state phase.
inline LedColor stateColor(State state,uint32_t elapsed,Press poke,
                          bool held=false,uint8_t brightness=LED_BRIGHTNESS) {
  if(poke!=Press::None || held) return {brightness,brightness,brightness};
  switch(state) {
    case State::Idle: {
      uint8_t value=breath(elapsed,2000,brightness);
      return stateHue(state,value);
    }
    case State::Thinking: {
      uint8_t value=breath(elapsed,1500,brightness);
      return stateHue(state,value);
    }
    case State::Processing: {
      uint8_t value=elapsed%1000<500?brightness:brightness/4;
      return stateHue(state,value);
    }
    case State::Ask:case State::Accepted:return stateHue(state,brightness);
    case State::Cancelled:return stateHue(state,uint8_t(elapsed%300<150?brightness:0));
  }
  return {0,0,0};
}
} // namespace pet
