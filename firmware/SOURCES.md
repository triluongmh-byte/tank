# Sources and derivation — 2026-11-20

Permitted user-named repositories, read only:

- `/Users/macbookpro/harnesses/claude-pet-case/firmware/claude_pet/`: pet renderer, UTF-8 hex text protocol, session/usage/status/activity parsers. Actual main sketch and motor driver/parser were read to preserve wire behavior. Copied visual/parser headers are listed with original hashes in `reference/manifest.json`. Historical SPI GPIOs, two-servo LEDC driver, old MAC and old hardware receipts are not reused as target evidence.
- `/Users/macbookpro/harnesses/claude-pet-case/host/motion_transport.py` and `tools/pet_bridge.py`: read the real send/lines transport, cue scheduling, CAPS/OFF validation and ACK formats before writing `host/tank_transport.py`. This is the reference path explicitly allowed in PILOT_BRIEF, not a second board design source. No changes made there.
- `/Users/macbookpro/harnesses/crab-robot-v17g/BOM.md`: permitted surplus inventory reference. Does not verify the exact present module or turn SG90 positional servos into continuous wheel servos.

Manufacturer sources inspected:

- [LILYGO factory pin configuration](https://raw.githubusercontent.com/Xinyuan-LilyGO/T-Display-S3/main/examples/factory/pin_config.h): GPIO and 320×170 geometry.
- [LILYGO display setup](https://raw.githubusercontent.com/Xinyuan-LilyGO/T-Display-S3/main/lib/TFT_eSPI/User_Setups/Setup206_LilyGo_T_Display_S3.h): confirms 8-bit parallel ST7789 and inversion/RGB setup.
- [LILYGO factory example](https://raw.githubusercontent.com/Xinyuan-LilyGO/T-Display-S3/main/examples/factory/factory.ino): esp_lcd i80 bus, clock 16MHz, swap-XY, mirror(false,true) with USB left, gap (0,35). Firmware implements that setup without LVGL dependency. DMA storage stays immutable until completion; display failure inhibits motion.
- [NXP PCA9685 datasheet, revision 4](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf), sections 7.3.1–7.4: sleep before prescale, wait after oscillator start, AI, push-pull/disabled-low configuration and per-channel full-off. ALL_LED writes propagate into the channel registers, so init never clears a broadcast after individually setting full-off. Nominal 25MHz/(4096×122)=50.0288Hz; a 1500µs pulse rounds to 307 counts. Oscillator and pulse accuracy require measurement.

Local installed SDK headers and compiler were used to verify API availability: Arduino ESP32 core 2.0.14 in `ARDUINO_DIRECTORIES_DATA`, built-in Wire/Preferences and ESP-IDF esp_lcd i80/ST7789. No framework/library install was needed.

Sealed contract supplies sonar reference, external GPIOs, connector rails, PCA address and channel meaning. Sonar speed-of-sound conversion 343m/s, clearance/timing thresholds, wheel span and turret mapping are engineering estimates, not calibrated distance/speed/angle. See DEVIATIONS.md for targets and WIRING.md for required bench observations.

- Release note 8: ST7789 init (SWRESET, SLPOUT, COLMOD 0x55, MADCTL 0, INVON, NORON, DISPON) is the common 240×240 sequence written from the ST7789 command set; **not verified on the owned 1.54" module** (inversion/offset/RGB order may need a bench tweak in display.h). Pin map is firmware-chosen, not from firmware-chat-2026-11-25.md (reference only, untested, lacks OE/ACT_EN).
