soi con cua crab-robot-v17g á, tham khảo cái ui trên Phone của nó đi fen. Rồi làm tao 1 cái UI điều khiển như vậy đi.

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- "con cua crab-robot-v17g" = the user's crab robot at /Users/macbookpro/harnesses/crab-robot-v17g. Its phone UI is
  served by the ESP32 itself over a direct Wi-Fi AP (open network "CuaRobot-XXXX", page http://192.168.4.1/,
  captive-portal probes serve the same page; optional home Wi-Fi setup). Hash-checked copies:
  /Users/macbookpro/harnesses/pet-tank/prompts/assets/crab-phone-ui/ui.html (the page), /Users/macbookpro/harnesses/pet-tank/prompts/assets/crab-phone-ui/network_http.h (HTTP API), /Users/macbookpro/harnesses/pet-tank/prompts/assets/crab-phone-ui/DIRECT-AP.md (behaviour).
- Crab page sections: "Lái" (8-direction hold-to-drive pad ↖↑↗←DỪNG→↙↓↘, light on/off, speed 0.4/0.65/1),
  "Wi-Fi" (scan + join home network, optional), "Ráp" (assembly/centre trim), test pages.
  API: POST /api/session (token), /api/move (token, seq, dir 0..8, fresh; 500 ms command lease stops stale motion),
  /api/light, /api/speed, GET /api/status.
- This answers the earlier open point: the tank firmware currently has only the USB host link; the lead
  noted WiFi/joystick from the cadsmith chat was not requested. The user is now requesting a phone control UI
  like the crab's for the tank (6 wheels, turret, 2 sonars, LEDs). Interfaces specific to the tank
  (turret, sonar readout, auto-scan) are not named by the user.
