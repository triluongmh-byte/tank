http://127.0.0.1:8420/p/robot-tank/ soi cái này fen. Tao in hết rồi. giờ soi xem. Ăn cắp cái case của nó luôn. Mình khỏi làm.

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- The URL is the user's local cadsmith studio project "robot-tank"; its folder is /Users/macbookpro/cad-models/robot-tank
  (the user named it, so that one path is readable as the reference). It is a CadQuery 6-wheel tank with a ">" nose,
  45° glacis with a window for the 1.54" screen, per-wheel lever suspension (arm pivots on an M3 through a chassis lug;
  SG90-360 servo + wheel on one end, rubber-band tab on the other end), turret SG90 180° carrying 2 back-to-back
  HC-SR04 sonars, front LED bar bracket, 2× 18650 cells. Build v1 passed all its checks (2026-11-25).
- "Tao in hết rồi" = the user has PRINTED all of robot-tank build v1 (chassis, hull, lid, turret_head, led_bracket,
  6 arms, 6 wheels). So the tank's case is now a physical, already-printed part set.
- "Ăn cắp cái case của nó luôn. Mình khỏi làm." = adopt robot-tank v1 as this project's case; stop designing a new
  case here. Earlier case notes (">" nose, remove wheel tubes, half-height hull, wider wheels, lever suspension,
  APC style) are satisfied by / superseded by this printed case — the entry agent's reading.
- Hash-checked copies of v1 sources are in /Users/macbookpro/harnesses/pet-tank/prompts/assets/robot-tank-cadsmith-v1/
  (model.py, report.json with all part sizes, STEP of chassis/hull/lid/turret_head/led_bracket/one arm/one wheel,
  drawing.svg, SHA256SUMS). The full STEP set is in /Users/macbookpro/cad-models/robot-tank/builds/v1/.
  Note: /Users/macbookpro/cad-models/robot-tank/model.py is being edited right now by another session (a board stack);
  it differs from builds/v1/model.py. The printed parts are v1. Do not edit that folder.
- Hardware the user said they now own, from that project's chat (2026-11-25) and order screenshots copied beside it:
  an ESP32 (the cadsmith chat assumed a 30-pin ESP32 DevKit), the 1.54" ST7789 screen from the first request,
  PCA9685 16-ch module ×1, 1S 18650 charge+boost "5V 2A Type-C" modules ×4, 2× WS2812 8-LED sticks,
  2× HC-SR04P, 6 servos 360° + SG90 turret, 18650 cells. The cadsmith chat also proposed a firmware
  (WiFi AP phone UI, 8-direction joystick, speed, LED on/off + colour, autonomous sonar-scan mode) and a pin map;
  it is saved as firmware-chat-2026-11-25.md in the same assets folder, untested on hardware.
