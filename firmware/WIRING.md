# Nối dây Pet Tank V0 — ESP32 DevKit (release note 8)

> **Release note 8 thay LILYGO bằng ESP32 DevKit + màn ST7789 1,54" 240×240 SPI; case là robot-tank v1 đã in (chassis rộng 68 mm), carrier 100×70 không còn vừa.** Bảng GPIO bên dưới **khớp bảng board công bố** (engineering/esp32-pinmap.json), `reconcile.py` so sánh tự động; chưa thử phần cứng. DevKit 30 chân là GIẢ ĐỊNH — đối chiếu chữ in trên module thật. Mọi chỗ ở dưới ghi "LILYGO" nay đọc là "ESP32 DevKit"; số IO trong cột LILYGO của bảng J_CTRL cũ bị thay bằng bảng này. Kiểm tra xe chưa chạy phần cứng.

| Chức năng | GPIO DevKit | Ghi chú |
|---|---|---|
| I2C_SDA / I2C_SCL | 21 / 22 | PCA9685 0x40; pull-up trên board/module |
| PCA_OE_N | 25 | HIGH tắt PWM; board giữ bias khi reset |
| ACT_EN | 26 | LOW tắt nguồn servo |
| Sonar trước Trig / Echo | 32 / 34 | Echo qua chuyển mức, 34 chỉ vào |
| Sonar sau Trig / Echo | 33 / 35 | Echo qua chuyển mức, 35 chỉ vào |
| STOP cục bộ | 27 | nút giữa J_CTRL 12 và GND, tích cực thấp, pull-up R44 trên carrier; GPIO0 (BOOT DevKit) cũng dừng |
| Host link | TX0=1, RX0=3 | cầu USB-UART của DevKit; không nối gì khác vào |
| ST7789 SCK / MOSI / CS / DC | 18 / 23 / 16 / 17 | SPI chỉ ghi, VCC 3V3, GND |
| ST7789 RST / BL | 4 / 13 | BL = mức cao bật; xác nhận nhãn module (có thể tên SDA=MOSI, SCL=SCK) |

Tránh strapping 0 (chỉ là nút BOOT), 2, 5, 12, 15 và flash 6–11. Nguồn logic: LOGIC_3V3 lấy từ LDO của DevKit; tổng tải 3V3 (PCA, màn, buffer) board tính lại. Cấp DevKit qua USB host, hoặc 5 V logic riêng vào chân VIN theo tài liệu board; không cấp hai nguồn cùng lúc.

---

*Phần dưới là bản carrier gốc; MCU là ESP32 DevKit, số IO theo bảng trên, và nguồn theo chuỗi hai đảo đã chốt bên dưới.*

# Nối dây carrier (bản gốc)

**GIẢ ĐỊNH:** ESP32 DevKit (thay LILYGO T-Display-S3 theo note 8), PCA9685 0x40, sáu servo quay liên tục FS90R/SG90-360, một SG90 180° cho turret. Servo SG90 180° không thay được servo bánh. Release note 1–2 xác định tham chiếu sonar là **HC-SR04P ×2**, dòng đặt hàng quảng cáo 3–5,5 V; ảnh đơn hàng chưa xác nhận module thực nhận, pinout, kích thước hoặc mức Echo. Người dùng xác nhận pin **18650 mắc song song**, 140 g, hai dây ra: dùng tham chiếu **1S danh nghĩa khoảng 3,7 V**. Số cell, model, dung lượng, dòng cho phép, kích thước, bảo vệ/sạc và cực tính vẫn chưa xác minh; chưa nối pin đó. Không suy ra hai cell từ khối lượng, không còn dùng giả định power bank USB hai cổng.

Bảng dưới lấy từ hợp đồng niêm phong, release note 1–2, [hằng số trong firmware](tank/pins.h) và pad net của `design/main.kicad_pcb`. [Báo cáo tích hợp](reports/integration.json) xác nhận GPIO, chân connector và bảy đường buffer U1 khớp chức năng; case còn pending. Hình dạng/vị trí đầu cắm thực khác hợp đồng gốc theo [ghi chú của board](../engineering/DEVIATIONS.md), mục 3; lead/case còn phải đối chiếu cơ khí. Đây là hướng dẫn cho bản dùng carrier, không nối thẳng Echo 5 V vào ESP32.

Nhìn từ trên xe, linh kiện PCB hướng lên: mũi xe là -Y, phải xe là +X. Chân 1 là pad vuông/dấu số 1. **J_CTRL và J_PCA thực là 2×6**, không phải hàng 1×12 của hợp đồng gốc: cột trái số lẻ, cột phải số chẵn, tăng hàng về đuôi (+Y). J_CTRL pad 1 tại (10;5,2) mm; J_PCA pad 1 tại (30;5,2) mm tính từ góc trái trước PCB. Sơ đồ nhìn từ trên, mũi ở phía trên:

```text
  1  2
  3  4
  5  6
  7  8
  9 10
 11 12   → đuôi ở phía dưới
```

J_S0–6 và J_SONAR là hàng một cột, số tăng về đuôi (+Y). J_PWR và J_FAN tăng số về phải (+X). Đầu cắm tín hiệu vào từ phía trên (+Z); dây nguồn vào đúng miệng terminal J_PWR/J_FAN, siết theo hướng dẫn đầu nối. Dùng số chân trên PCB cùng **chữ in trên module**, không đoán thứ tự từ màu dây hoặc trái/phải của ảnh. J_CTRL/J_PCA là hàng chuyển tiếp riêng, không phải thứ tự chân vật lý của module. Xem [pinout đo trên board](../engineering/pinout.md) để biết tọa độ từng pad.

## ESP32 DevKit đến J_CTRL

| Chữ trên DevKit | Chân carrier | Net / vai trò |
|---|---|---|
| GND | J_CTRL 1 và 11 | Mass chung |
| 3V3 | J_CTRL 2 | LOGIC_3V3, LDO của DevKit (carrier là tải) |
| GPIO21 / D21 | J_CTRL 3 | I2C_SDA |
| GPIO22 / D22 | J_CTRL 4 | I2C_SCL |
| GPIO25 / D25 | J_CTRL 5 | PCA_OE_N: cao tắt PWM (R5 kéo lên) |
| GPIO26 / D26 | J_CTRL 6 | ACT_EN: thấp tắt nguồn servo (R4 kéo xuống) |
| GPIO32 / D32 | J_CTRL 7 | Trig sonar trước, 3.3 V |
| GPIO34 / D34 | J_CTRL 8 | Echo sonar trước sau hạ mức (chỉ vào) |
| GPIO33 / D33 | J_CTRL 9 | Trig sonar sau, 3.3 V |
| GPIO35 / D35 | J_CTRL 10 | Echo sonar sau sau hạ mức (chỉ vào) |
| GPIO27 / D27 | J_CTRL 12 | STOP_N: nút tới J_CTRL 11 (GND), tích cực thấp; không bao giờ cấu hình làm output |

Cổng USB của DevKit (cầu USB-UART, UART0 GPIO1/3) nối host; không nối servo vào GPIO1/3. Màn ST7789 nối trực tiếp bằng dây SPI (bảng trên: SCK18 MOSI23 CS16 DC17 RST4 BL13, VCC 3V3, GND; nếu module không có CS thì nối CS xuống GND); GPIO19 dành cho WS2812 tùy chọn, chưa nối. GPIO27 là nút STOP tại chỗ, GPIO0 cũng dừng khi giữ và duyệt phiên khi nhả; giữ GPIO0 lúc reset sẽ vào bootloader.

## PCA9685 đến J_PCA

| Chữ trên PCA9685 | Chân carrier |
|---|---|
| VCC | J_PCA 1, LOGIC_3V3 |
| GND | J_PCA 2 |
| SDA | J_PCA 3 |
| SCL | J_PCA 4 |
| OE | J_PCA 5 |
| CH0 signal | J_PCA 6 |
| CH1 signal | J_PCA 7 |
| CH2 signal | J_PCA 8 |
| CH3 signal | J_PCA 9 |
| CH4 signal | J_PCA 10 |
| CH5 signal | J_PCA 11 |
| CH6 signal | J_PCA 12 |

Địa chỉ 7-bit là **0x40**: strap A0–A5 theo module tham chiếu, không tùy ý hàn đổi địa chỉ. Chân **V+**, terminal nguồn servo và toàn bộ hàng V+ trên PCA để hở. Chỉ nối các chân **signal** CH0–6 vào carrier. Không cấp dòng servo qua PCA, chân 5V DevKit hay USB máy tính. Kênh 7–15 không nối, firmware giữ full-off.

Trên copper, J_PCA 6–12 mang tên `PWM_*_RAW`, đi qua buffer SN74LVC244A U1 thành `PWM_*` ở J_S0–6. Buffer không đảo mức hoặc đổi kênh; nguồn buffer thuộc miền tải được tắt cùng servo. Không nối tắt đường buffer. GPIO25 điều khiển OE của cả PCA và U1.

## Servo, sonar và nguồn tải

| Thiết bị | Cổng carrier / kênh | Nguồn V+ |
|---|---|---|
| Bánh trái trước / giữa / sau | J_S0 / J_S1 / J_S2 = CH0 / CH1 / CH2 | đảo A: chân 2 SERVO_5V của J_Sx |
| SG90 turret | J_S6 = CH6 | đảo A: chân 2 SERVO_5V |
| Bánh phải trước / giữa / sau | J_S3 / J_S4 / J_S5 = CH3 / CH4 / CH5 | **đảo B: dây đỏ nối thẳng converter B, không qua carrier** |

Mỗi J_Sx: **1 GND → GND servo; 3 PWM → signal servo**. Chân 2 SERVO_5V → dây + servo **chỉ với J_S0–J_S2 và J_S6 (đảo A)**. Với J_S3–J_S5 **rút chân V+ (giữa) khỏi vỏ phích servo** (không hàn, không cắt carrier), để chân V+ của header carrier trống. Xác minh nhãn servo trước khi nối; màu dây chỉ là phụ. Chiều quay được hiệu chuẩn riêng từng bánh, không đảo cực.

## Chuỗi nguồn đã chốt (board deviation 8, POWER_SYSTEM.md "DECIDED"): hai đảo, đầu ra không bao giờ nối chung

```text
bộ pin 1S 18650 kín (140 g, chưa xác minh) + PCB-Li-1S15A + F_PACK 0287015.U (0FHA0002XP)
   P+ / P-  (>=14 AWG, đầu nối >=15 A, loại XT60; không Dupont)
        |-- U3V70F5 #1 (A) VIN/GND -> VOUT -> J_PWR.1 EXT_5V_IN / .2 GND
        |      carrier F1 -> Q1 -> LOAD_5V -> quạt J_FAN, J_SONAR, Q2/Q3(ACT_EN) -> SERVO_5V -> J_S0-2, J_S6
        '-- U3V70F5 #2 (B) VIN/GND -> VOUT -> cầu chì lưỡi 5 A -> mối nối 3 dây đỏ servo CH3-5
               ENABLE: 4.7 kΩ xuống GND, và dây nhánh từ J_CTRL.6 (GPIO26 ACT_EN)
ESP32 DevKit: nhánh USB 5 V riêng (cáp host hoặc bộ 5 V logic); LOGIC_3V3 chỉ từ LDO DevKit
GND chung tại cực âm pin / J_PWR.2 / GND converter B / GND carrier
```

1. **Pack:** pin 1S 18650 song song, hai dây ra (số cell, model, dòng, bảo vệ chưa biết). Bảo vệ PCB-Li-1S15A và cầu chì F_PACK 15 A (0287015.U trong đế 0FHA0002XP) do bên lắp pack kín gắn ở cực dương; không tự mở hay hàn cell. Không nối thẳng pin 1S vào J_PWR, PCA V+ hay chân DevKit.
2. **Dây pack và đầu vào converter:** ≥14 AWG, tổng vòng ≤0,4 m, mọi phích/mối nối ≥15 A liên tục (loại XT60), không Dupont. Hai đầu vào converter A và B song song tại pack; **hai đầu ra không bao giờ nối với nhau**. Mỗi converter ≤7 A vào kéo dài; tổng đỉnh khoảng 10,6 A ở 3,3 V (chưa đo).
3. **Đảo A (đỉnh ≈3,56 A, ≤4,0 A):** converter A VOUT/GND → J_PWR.1/.2 (18 AWG). J_PWR cấp CH0–2, turret CH6, quạt 5 V, hai sonar HC-SR04P và buffer; qua F1 7 A, Q1 chống ngược, công tắc ACT_EN Q2/Q3 (mặc định tắt). Quạt (J_FAN 1 +5V, 2 GND) nằm trên LOAD_5V, không có GPIO.
4. **Đảo B (đỉnh ≈2,4 A):** converter B VOUT → cầu chì lưỡi 5 A → mối nối ba dây đỏ của servo J_S3–J_S5; GND và signal của ba servo vẫn đi qua J_S3–J_S5; GND converter B nối cực âm pin. **ENABLE:** hàn/đấu điện trở 4,7 kΩ ENABLE→GND (≈0,17 V, tắt mặc định) và kéo dây nhánh từ J_CTRL chân 6 (GPIO26 ACT_EN) vào ENABLE. Việc 3,3 V bật được ENABLE là GIẢ ĐỊNH; nếu bench không bật, dùng 2N7002 kéo ENABLE xuống từ /ACT_EN theo POWER_SYSTEM.md.
5. **Mặc định tắt:** khi reset/boot GPIO26 ở trạng thái high-Z; R4 và 4,7 kΩ giữ cả hai đảo servo tắt tới khi firmware đưa ACT_EN lên. PCA_OE_N vẫn kéo lên nên không có xung PWM. **Rủi ro mở:** nếu U3V70F5 khi disable vẫn lọt xấp xỉ Vin qua cuộn cảm/diode, CH3–5 có thể nhận ≈3,7 V khi ACT_EN thấp — bắt buộc đo "ACT_EN tắt = 0 V ở cả hai đảo"; không đạt thì thêm công tắc tải (chưa thực hiện).
6. **DevKit:** nhánh USB 5 V riêng, không nối dây 5 V carrier–DevKit. Không nối hai nguồn USB; không dùng cáp Y.
7. **Sạc:** phích RUN và phích CHARGE loại trừ nhau; không chạy khi sạc; F_PACK vẫn nằm trong mạch. Chỉ một module "5V 2A" của người dùng không đủ cho đảo A (3,56 A), không dùng làm đường tải chính.
8. Pack 140 g của người dùng chưa chứng minh được ≈11 A cho trường hợp cả bảy servo kẹt cùng lúc; vận hành thường ≈2,1 A. Chỉ chấp nhận cấp tải sau khi bên có chuyên môn xác minh pack và bench: converter không tải 4,8–5,2 V, bước tải A 0,5→3,5 A / B 2,4 A, xung ≤5,5 V khi phanh.

J_SONAR_F → HC-SR04P hướng về mũi khi turret ở tâm. J_SONAR_R → HC-SR04P hướng về đuôi. Trên cả hai: **1 LOAD_5V → VCC; 2 TRIG_5V → Trig; 3 ECHO_5V → Echo; 4 GND → GND**, đối chiếu chữ trên module thực. Carrier nâng Trig và hạ Echo; Echo có thể lên 5 V. Không nối Echo trực tiếp vào GPIO34/35. Trig/Echo: 32/34 trước, 33/35 sau, kích tuần tự, hành vi đo không đổi.

Quạt **30×30 mm, 5 V, hai dây**: **J_FAN 1 LOAD_5V → cực +; J_FAN 2 GND → cực −**; kiểm cực theo nhãn quạt. Pad 1 tại (45,5;52) mm, pad 2 tại (50,58;52) mm. Quạt nhận nguồn khi J_PWR có điện và **không có GPIO điều khiển**; STOP, OE, ACT_EN không tắt quạt. Dòng quạt dự trù 0,30 A (chưa đo); gá và fit chưa xác nhận.

Carrier có bảo vệ, tụ, chuyển mức sonar, công tắc tải mặc định tắt, buffer cách ly và bias OE. Lắp đúng [BOM carrier](../parts.json). Xem [bring-up](../engineering/bringup.md) và [POWER_SYSTEM.md](../engineering/POWER_SYSTEM.md); các phép đo reset, dòng, backfeed, nhiệt chưa thực hiện.

## Thứ tự ráp và kiểm tra khi được phép thử thực

1. Ngắt mọi nguồn. Đọc chữ trên từng module; nếu module không đúng nhãn nêu trên, dừng nối dây đó và báo khác biệt.
2. Nối mass và dây logic trước, đối chiếu từng hàng bảng. Kiểm tra pad 1 bằng dấu PCB; không cắm nguyên một hàng cáp nếu nhãn hai đầu không khớp.
3. Dùng đồng hồ ở chế độ thông mạch khi chưa cấp nguồn: mọi GND phải thông; kiểm tra không chập 3V3–GND, 5V–GND và không có đường nối trực tiếp EXT_5V_IN–USB VBUS. Tụ có thể làm đồng hồ kêu thoáng qua; tiếng kêu liên tục cần kiểm tra.
4. Chưa cắm servo. Sau khi có phép flash/thử thực, chỉ cấp USB logic: màn hiện mặt pet, `ping` trả `PONG tank v1 pet`, `MOTOR STATUS` báo OFF, `MOTOR CAPS` có tank-v1 và MAC thật. Không tự chạy sau reset.
5. Theo bring-up board, đo ACT_EN thấp/OE cao, SERVO_5V (đảo A) và VOUT converter B đều 0 V ở boot/reset, kể cả PCA clone có pull-down. Kiểm tra tải không nhận nguồn ngược qua signal. Đây là phép đo phần cứng chưa thực hiện.
6. Chỉ sau khi nguồn tải, cực tính và các phép đo trên đạt, được phép thử chuyển động riêng: kê xe để bánh không chạm bàn, tháo horn turret nếu chưa rõ tâm, kiểm tra từng kênh bằng lệnh giới hạn thời gian và nút STOP. Hiệu chuẩn theo [README](README.md), chưa bật AUTO.

Dây bánh cần vòng chùng cho toàn hành trình nhún, tránh lốp/pivot. Dây turret cần chống tuột và vòng chùng qua ổ xoay; quay tay khi **không cấp nguồn**, kiểm tra giới hạn case trước. Sonar ngang không phát hiện mép bàn; không thử xe trên bàn không có chắn.

Tài liệu này không cấp phép flash, cấp tải hoặc chạy động cơ. Chưa có xác nhận fit, dòng tải hay chuyển động thực.
