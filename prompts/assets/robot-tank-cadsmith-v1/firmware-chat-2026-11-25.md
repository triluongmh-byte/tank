Mấy món mày mua tao xem rồi: PCA9685, mạch sạc 1S boost 5V, 2 thanh WS2812 8 bóng, 2 HC-SR04P. Tao chỉ sửa được `model.py` thôi nên không tạo file firmware cho mày được. Code tao dán hết ở dưới, mày lưu thành `robot_tank/robot_tank.ino` rồi nạp bằng Arduino IDE. `model.py` lần này tao không đụng tới. Tao cũng chưa nạp chạy thử code này trên mạch thật lần nào, nên phải canh chỉnh ở bước 2 rồi mới cho chạy 🔧

## 🔌 Sơ đồ nối dây

| Linh kiện | Chân ESP32 |
|---|---|
| PCA9685 SDA / SCL | 21 / 22 |
| Servo bánh trái trước, giữa, sau | PCA kênh 0, 1, 2 |
| Servo bánh phải trước, giữa, sau | PCA kênh 3, 4, 5 |
| Servo turret (SG90 thường) | PCA kênh 8 |
| Sonar trước TRIG / ECHO | 32 / 34 |
| Sonar sau TRIG / ECHO | 33 / 35 |
| 2 thanh LED nối tiếp (DIN), 16 bóng | 27 (nên gắn thêm điện trở 330 Ω nối tiếp) |
| 2 LED đèn hậu 5 mm (mỗi con 1 điện trở 220 Ω) | 13 |
| Màn ST7789 SDA / SCL / CS / DC / RES / BL | 23 / 18 / 5 / 26 / 25 / 4 |

⚠️ **Nguồn, đọc kỹ chỗ này kẻo cháy mạch:**
- Một mạch sạc chỉ cho ra 5V 2A. 6 servo chạy cùng lúc cộng WiFi cộng 16 bóng LED là quá tải, ESP32 sẽ reset liên tục.
- Mày mua 4 mạch sạc rồi nên tách làm 2 nguồn: **pin 1 + mạch sạc 1 → chân V+ của PCA9685** (chỉ nuôi servo). **Pin 2 + mạch sạc 2 → chân 5V của ESP32, LED và màn hình.**
- Nối chung GND hai nguồn với nhau. Gắn thêm 1 tụ 1000 µF ở chân V+ của PCA.
- HC-SR04P cấp 3.3V thì chân ECHO cắm thẳng vào ESP32 được, khỏi cần cầu phân áp.
- Màn hình: tao giả định là ST7789 1.54" 240×240 SPI. Nếu là loại không có chân CS thì đổi `tft.init(240, 240)` thành `tft.init(240, 240, SPI_MODE3)`.

## 📦 Thư viện (cài bằng Library Manager)
`Adafruit PWM Servo Driver Library`, `Adafruit NeoPixel`, `Adafruit GFX Library`, `Adafruit ST7735 and ST7789 Library`, `WebSockets` (của Markus Sattler).

## 💻 Code

```cpp
/* ROBOT TANK - ESP32 firmware
   WiFi AP "RobotTank" / pass 12345678 -> mo http://192.168.4.1
   Joystick 8 huong, toc do, den on/off + doi mau, che do tu di quet sonar 360 */
#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PWMServoDriver.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>

// ---------------- CAU HINH ----------------
const char* AP_SSID = "RobotTank";
const char* AP_PASS = "12345678";

#define PIN_PIXELS 27
#define NUM_PIXELS 16
#define LED_BRIGHT 80          // 0-255, dung de cao qua -> sap nguon
#define PIN_TAIL   13
#define TRIG_F 32
#define ECHO_F 34
#define TRIG_R 33
#define ECHO_R 35
#define TFT_CS  5
#define TFT_DC  26
#define TFT_RST 25
#define TFT_BL  4

// Servo banh: 0-2 trai (truoc, giua, sau), 3-5 phai
const uint8_t CH_WHEEL[6]  = {0, 1, 2, 3, 4, 5};
const int8_t  DIR_WHEEL[6] = {+1, +1, +1, -1, -1, -1};  // banh nao quay nguoc thi doi dau
int STOP_US[6] = {1500, 1500, 1500, 1500, 1500, 1500};  // trim cho banh dung yen
const int SPAN_US = 400;                                 // +-400us = full speed

#define CH_TURRET 8
const int TURRET_MIN_US = 500, TURRET_MAX_US = 2500;
const int TURRET_DIR = +1;     // neu quet trai/phai bi nguoc thi doi -1

// Tu di
const float STOP_CM  = 30;     // vat can gan hon -> dung lai quet
const float CLEAR_CM = 40;     // huong nao trong hon muc nay moi chon
const float TURN_SPEED = 0.6;
float MS_PER_DEG = 6.0;        // CAN CHINH: so ms quay tai cho 1 do o TURN_SPEED

// ---------------- DOI TUONG ----------------
WebServer server(80);
WebSocketsServer ws(81);
Adafruit_PWMServoDriver pwm;
Adafruit_NeoPixel pixels(NUM_PIXELS, PIN_PIXELS, NEO_GRB + NEO_KHZ800);
Adafruit_ST7789 tft(TFT_CS, TFT_DC, TFT_RST);

float tgtL = 0, tgtR = 0, curL = 0, curR = 0;
int speedPct = 60;
bool autoMode = false, lightsOn = false;
uint32_t lightColor = 0xFFFFFF;
float frontCm = 400, rearCm = 400;
unsigned long lastCmd = 0, lastRamp = 0, lastTx = 0, lastSonar = 0, lastText = 0, nextBlink = 3000;

// ---------------- WEB UI ----------------
const char INDEX_HTML[] = R"HTML(<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<style>
body{margin:0;background:#111;color:#eee;font-family:sans-serif;text-align:center;touch-action:none;user-select:none}
#pad{width:260px;height:260px;border-radius:50%;background:#222;box-shadow:0 0 0 3px #444;margin:16px auto;position:relative}
#knob{width:90px;height:90px;border-radius:50%;background:#0af;position:absolute;left:85px;top:85px}
.row{margin:12px}
button{font-size:18px;padding:10px 18px;margin:4px;border-radius:10px;border:0;background:#333;color:#eee}
button.on{background:#0a6}
input[type=range]{width:80%}
input[type=color]{width:50px;height:40px;border:0;vertical-align:middle}
</style></head><body>
<h3>ROBOT TANK</h3><div id=st>Dang ket noi...</div>
<div id=pad><div id=knob></div></div>
<div class=row>Toc do: <b id=sv>60</b>%<br><input id=sp type=range min=10 max=100 value=60></div>
<div class=row><button id=lt>Den: TAT</button> <input id=cl type=color value="#ffffff"></div>
<div class=row><button id=md>Tu di: TAT</button></div>
<div id=dist>Truoc: - cm | Sau: - cm</div>
<script>
let ws,jx=0,jy=0,lo=false,au=false;
function con(){ws=new WebSocket('ws://'+location.hostname+':81/');
ws.onopen=()=>{st.textContent='Da ket noi';send('S,'+sp.value)};
ws.onclose=()=>{st.textContent='Mat ket noi...';setTimeout(con,1000)};
ws.onmessage=e=>{let p=e.data.split(',');if(p[0]=='D')dist.textContent='Truoc: '+p[1]+' cm | Sau: '+p[2]+' cm'}}
con();
function send(m){if(ws&&ws.readyState==1)ws.send(m)}
const R=130,K=45,M=R-K;let drag=false;
function mv(e){let r=pad.getBoundingClientRect();let x=e.clientX-r.left-R,y=e.clientY-r.top-R;
let d=Math.hypot(x,y);if(d>M){x=x*M/d;y=y*M/d}
knob.style.left=(x+R-K)+'px';knob.style.top=(y+R-K)+'px';jx=Math.round(x/M*100);jy=Math.round(-y/M*100)}
function rel(){drag=false;jx=jy=0;knob.style.left=knob.style.top=(R-K)+'px';send('J,0,0')}
pad.onpointerdown=e=>{drag=true;pad.setPointerCapture(e.pointerId);mv(e)};
pad.onpointermove=e=>{if(drag)mv(e)};
pad.onpointerup=rel;pad.onpointercancel=rel;
setInterval(()=>send('J,'+jx+','+jy),100);
sp.oninput=()=>{sv.textContent=sp.value;send('S,'+sp.value)};
lt.onclick=()=>{lo=!lo;lt.textContent='Den: '+(lo?'BAT':'TAT');lt.className=lo?'on':'';send('L,'+(lo?1:0))};
cl.oninput=()=>send('C,'+cl.value.slice(1));
md.onclick=()=>{au=!au;md.textContent='Tu di: '+(au?'BAT':'TAT');md.className=au?'on':'';send('M,'+(au?1:0))};
</script></body></html>)HTML";

// ---------------- SERVO ----------------
void setWheel(int i, float v) {
  v = constrain(v, -1.0f, 1.0f);
  if (fabs(v) < 0.02) { pwm.setPWM(CH_WHEEL[i], 0, 4096); return; }  // tat xung -> dung han
  pwm.writeMicroseconds(CH_WHEEL[i], STOP_US[i] + (int)(DIR_WHEEL[i] * v * SPAN_US));
}
void drive(float l, float r) {
  for (int i = 0; i < 3; i++) setWheel(i, l);
  for (int i = 3; i < 6; i++) setWheel(i, r);
}
void setTurret(int deg) {
  deg = constrain(deg, 0, 180);
  pwm.writeMicroseconds(CH_TURRET, map(deg, 0, 180, TURRET_MIN_US, TURRET_MAX_US));
}
void rampStep(unsigned long now) {
  if (now - lastRamp < 20) return;
  lastRamp = now;
  const float st = 0.08;
  curL += constrain(tgtL - curL, -st, st);
  curR += constrain(tgtR - curR, -st, st);
  drive(curL, curR);
}

// ---------------- SONAR ----------------
float readCm(int trig, int echo) {
  digitalWrite(trig, LOW);  delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  unsigned long t = pulseIn(echo, HIGH, 25000);
  return t ? t * 0.0343f / 2 : 400;
}

// ---------------- DEN ----------------
void updateLights() {
  uint32_t c = lightsOn ? pixels.Color((lightColor >> 16) & 255, (lightColor >> 8) & 255, lightColor & 255) : 0;
  for (int i = 0; i < NUM_PIXELS; i++) pixels.setPixelColor(i, c);
  pixels.show();
  digitalWrite(PIN_TAIL, lightsOn);
}

// ---------------- JOYSTICK 8 HUONG ----------------
void onJoy(int x, int y) {
  float mag = sqrtf(x * x + y * y) / 100.0f;
  if (mag < 0.15) { tgtL = tgtR = 0; return; }
  mag = min(mag, 1.0f);
  float ang = atan2f(x, y) * 180 / PI;                 // 0 = len, 90 = phai
  int s = (((int)lroundf(ang / 45.0f)) % 8 + 8) % 8;   // 0 N,1 NE,2 E,3 SE,4 S,5 SW,6 W,7 NW
  static const float L[8] = {1, 1, 1, -1, -1, -0.3, -1, 0.3};
  static const float R[8] = {1, 0.3, -1, -0.3, -1, -1, 1, 1};
  float k = mag * speedPct / 100.0f;
  tgtL = L[s] * k; tgtR = R[s] * k;
}

// ---------------- TU DI ----------------
enum AState { A_FWD, A_SCAN, A_TURN, A_BACK };
AState aState = A_SCAN;
unsigned long aT = 0;
int scanA = 90, scanDir = 1;
float distMap[24];   // 24 o x 15 do, o 0 = phia truoc, duong = ben trai

int binOf(float h) { int b = (int)lroundf(h / 15.0f); return (b % 24 + 24) % 24; }
float hOf(int b) { return b <= 12 ? b * 15 : (b - 24) * 15; }

void enterFwd() { aState = A_FWD; scanA = 90; setTurret(90); aT = millis() + 150; }
void startScan() {
  aState = A_SCAN; tgtL = tgtR = 0; scanA = 0; setTurret(0);
  for (int i = 0; i < 24; i++) distMap[i] = 0;
  aT = millis() + 400;
}
void decide() {
  int best = -1; float bestScore = -1e9;
  for (int b = 0; b < 24; b++) {
    float d = min(distMap[b], min(distMap[(b + 23) % 24], distMap[(b + 1) % 24]));  // tinh ca be ngang xe
    float sc = d - 0.15f * fabs(hOf(b));  // uu tien huong it phai quay
    if (d > CLEAR_CM && sc > bestScore) { bestScore = sc; best = b; }
  }
  setTurret(90);
  if (best < 0) {
    if (distMap[12] > 20) { aState = A_BACK; tgtL = tgtR = -TURN_SPEED; aT = millis() + 700; }
    else { aState = A_TURN; tgtL = -TURN_SPEED; tgtR = TURN_SPEED; aT = millis() + 90 * MS_PER_DEG; }
    return;
  }
  float h = hOf(best);
  if (fabs(h) <= 15) { enterFwd(); return; }
  float s = h > 0 ? 1 : -1;   // duong = quay trai
  aState = A_TURN; tgtL = -s * TURN_SPEED; tgtR = s * TURN_SPEED;
  aT = millis() + (unsigned long)(fabs(h) * MS_PER_DEG);
}
void autoStep(unsigned long now) {
  switch (aState) {
    case A_FWD:
      tgtL = tgtR = speedPct / 100.0f;
      if (now >= aT) {
        frontCm = readCm(TRIG_F, ECHO_F);
        if (frontCm < STOP_CM) { startScan(); break; }
        scanA += scanDir * 10;
        if (scanA >= 120 || scanA <= 60) scanDir = -scanDir;
        setTurret(scanA);
        aT = now + 80;
      }
      break;
    case A_SCAN:
      if (now >= aT) {
        float h = (scanA - 90) * TURRET_DIR;
        frontCm = readCm(TRIG_F, ECHO_F); delay(5);
        rearCm = readCm(TRIG_R, ECHO_R);
        distMap[binOf(h)] = frontCm;
        distMap[binOf(h + 180)] = rearCm;
        if (scanA >= 180) decide();
        else { scanA += 15; setTurret(scanA); aT = now + 120; }
      }
      break;
    case A_TURN:
      if (now >= aT) enterFwd();
      break;
    case A_BACK:
      if (now >= aT) startScan();
      break;
  }
}
void setAuto(bool on) {
  autoMode = on;
  tgtL = tgtR = 0;
  if (on) startScan(); else setTurret(90);
}

// ---------------- MAN HINH (mat robot) ----------------
void drawEyes(int off, bool closed) {
  uint16_t c = autoMode ? ST77XX_ORANGE : ST77XX_CYAN;
  tft.fillRect(0, 30, 240, 130, ST77XX_BLACK);
  for (int i = 0; i < 2; i++) {
    int x = 70 + i * 100;
    if (closed) tft.fillRoundRect(x - 30, 90, 60, 10, 5, c);
    else { tft.fillRoundRect(x - 30, 50, 60, 90, 18, c); tft.fillCircle(x + off, 100, 12, ST77XX_BLACK); }
  }
}
void faceStep(unsigned long now) {
  static int lastOff = 99; static bool lastClosed = false, lastAuto = false;
  bool closed = now >= nextBlink && now < nextBlink + 150;
  if (now >= nextBlink + 150) nextBlink = now + 2500 + random(3000);
  int off = constrain((int)lroundf((curL - curR) * 2) * 7, -14, 14);
  if (off != lastOff || closed != lastClosed || autoMode != lastAuto) {
    drawEyes(off, closed); lastOff = off; lastClosed = closed; lastAuto = autoMode;
  }
  if (now - lastText > 500) {
    lastText = now;
    tft.fillRect(0, 180, 240, 60, ST77XX_BLACK);
    tft.setTextSize(2); tft.setTextColor(ST77XX_WHITE);
    tft.setCursor(10, 185); tft.printf("%s  %d%%", autoMode ? "AUTO" : "MANUAL", speedPct);
    tft.setCursor(10, 210); tft.printf("F:%3dcm R:%3dcm", (int)frontCm, (int)rearCm);
  }
}

// ---------------- WEBSOCKET ----------------
void onWs(uint8_t num, WStype_t type, uint8_t* payload, size_t len) {
  if (type == WStype_DISCONNECTED) { setAuto(false); tgtL = tgtR = 0; return; }
  if (type != WStype_TEXT) return;
  String m((char*)payload);
  lastCmd = millis();
  int x, y;
  switch (m[0]) {
    case 'J': if (!autoMode && sscanf(m.c_str(), "J,%d,%d", &x, &y) == 2) onJoy(x, y); break;
    case 'S': speedPct = constrain(m.substring(2).toInt(), 10, 100); break;
    case 'L': lightsOn = (m[2] == '1'); updateLights(); break;
    case 'C': lightColor = strtoul(m.c_str() + 2, NULL, 16); updateLights(); break;
    case 'M': setAuto(m[2] == '1'); break;
  }
}

// ---------------- SETUP / LOOP ----------------
void setup() {
  Serial.begin(115200);
  pinMode(TRIG_F, OUTPUT); pinMode(ECHO_F, INPUT);
  pinMode(TRIG_R, OUTPUT); pinMode(ECHO_R, INPUT);
  pinMode(PIN_TAIL, OUTPUT); pinMode(TFT_BL, OUTPUT); digitalWrite(TFT_BL, HIGH);

  Wire.begin(21, 22);
  pwm.begin(); pwm.setOscillatorFrequency(27000000); pwm.setPWMFreq(50);
  drive(0, 0); setTurret(90);

  pixels.begin(); pixels.setBrightness(LED_BRIGHT); updateLights();

  tft.init(240, 240); tft.setRotation(0); tft.fillScreen(ST77XX_BLACK);

  WiFi.softAP(AP_SSID, AP_PASS);
  Serial.println(WiFi.softAPIP());
  server.on("/", []() { server.send(200, "text/html", INDEX_HTML); });
  server.begin();
  ws.begin(); ws.onEvent(onWs);
}

void loop() {
  server.handleClient();
  ws.loop();
  unsigned long now = millis();

  if (autoMode) autoStep(now);
  else {
    if (now - lastCmd > 600) tgtL = tgtR = 0;            // mat song -> dung
    if (now - lastSonar > 150) {
      lastSonar = now;
      static bool flip = false; flip = !flip;
      if (flip) frontCm = readCm(TRIG_F, ECHO_F); else rearCm = readCm(TRIG_R, ECHO_R);
    }
    if (tgtL > 0 && tgtR > 0 && frontCm < 15) tgtL = tgtR = 0;   // chong dam dau
    if (tgtL < 0 && tgtR < 0 && rearCm < 15) tgtL = tgtR = 0;    // chong de dit
  }
  rampStep(now);
  faceStep(now);

  if (now - lastTx > 300) {
    lastTx = now;
    char buf[32]; snprintf(buf, sizeof(buf), "D,%d,%d", (int)frontCm, (int)rearCm);
    ws.broadcastTXT(buf);
  }
}
```

## 🛠️ Chạy lần đầu
1. Nạp code xong, điện thoại vào WiFi **RobotTank** (pass `12345678`) rồi mở **192.168.4.1**.
2. **Canh chỉnh trước khi cho xe chạy:**
   - Bánh nào đứng yên mà vẫn rề rề thì vặn biến trở trên con FS90R, hoặc sửa `STOP_US` của bánh đó.
   - Bánh nào quay ngược chiều thì đổi dấu `DIR_WHEEL` của bánh đó.
   - Turret quét bị ngược hướng thì đổi `TURRET_DIR` thành `-1`.
   - Cho xe quay tại chỗ 360° ở chế độ tự đi, bấm giờ rồi chỉnh `MS_PER_DEG` tới khi xe quay đúng góc.
3. **Chế độ tự đi:** xe đứng lại, turret quét 0→180°. Vì 2 sonar quay lưng nhau nên quét nửa vòng là đo đủ 360°. Xe chọn hướng trống mà ít phải quay nhất, quay sang hướng đó rồi chạy thẳng, vừa chạy vừa lắc turret ±30° để dò phía trước. Bị kẹt cả bốn phía thì lùi rồi quét lại.
4. Lỡ mất kết nối WiFi thì xe tự dừng và tắt chế độ tự đi.

Lưu ý 🧱: model hiện vẫn có 4 cột đỡ Arduino Nano dưới nắp. ESP32 DevKit (~55×28 mm), PCA9685 (62×25 mm) và 2 mạch sạc chưa có chỗ gắn. Muốn thì tao sửa `model.py` để thêm gá cho mấy món đó, chừa cả lỗ cho cổng Type-C ra ngoài để sạc 😎