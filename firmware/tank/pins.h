#pragma once
namespace tank {
// ESP32 DevKit (30-pin ASSUMED) V0 map. Avoids strapping 2/5/12/15 and flash 6-11; 34/35 are input-only.
// Matches engineering/esp32-pinmap.json (board-published, release note 8); reconcile.py compares.
constexpr int SDA_PIN=21, SCL_PIN=22, OE_PIN=25, ACT_PIN=26;
constexpr int TRIG_PINS[2]={32,33}, ECHO_PINS[2]={34,35};
constexpr int STOP_PIN=27, BOOT_PIN=0;  // BOOT_PIN is the DevKit BOOT button (strapping only at reset)
constexpr int LCD_SCK=18,LCD_MOSI=23,LCD_CS=16,LCD_DC=17,LCD_RST=4,LCD_BL=13;
constexpr unsigned LCD_HZ=40000000;
constexpr unsigned PCA_ADDRESS=0x40, PCA_PRESCALE=121;
constexpr unsigned LINK_MS=750, POWER_SETTLE_MS=50, NEUTRAL_MS=40, FRESH_MS=250;
constexpr unsigned TURRET_SETTLE_MS=300, CLEAR_MM=350;
constexpr char CONTRACT_SHA[]="a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810";
}
