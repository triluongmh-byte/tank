# Pilot release notes

Base contract SHA-256: `a3ef67fc11d668fdbe01fd2d5a06c6fef5fed069868d7fb6fb4b3995edd55810`

The base contract is immutable. New requirements are additive. Later numbered notes supersede earlier notes only for the named fields; all other base fields remain in force.

## 1. board, firmware, case

Note SHA-256: `925a86e2870b7771a6384cfc1df26373c453eb6b1641875672edac24955a0f9b`

Changed contract fields: modules, powerRails, pins, assumptions

User message (verbatim):

```text
quajt 5v, pin zì 27... zì đó nó quấn song song chìa ra 2 cái dây, tao đã lắp lên con cua rồi cũng oke lắm. sonar đúng loại của con cua luôn

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- This answers the entry agent's three questions: fan voltage, battery type, sonar type.
- "quajt 5v" = the 30×30 mm fan is 5 V.
- Battery: the user says it is the same pack already fitted on crab-robot-v17g and it worked well.
  /Users/macbookpro/harnesses/crab-robot-v17g/README.md records that robot's power as a 2-port USB 5 V
  power bank (slim ~5000 mAh, assumed ≤100×65×15 mm, ≤120 g, port 1 → USB-C to LILYGO, port 2 →
  USB-to-screw-terminal adapter → PCA9685 V+ and LEDs). The user's description ("zì 27...", "quấn song
  song chìa ra 2 cái dây" = bundled side by side with 2 leads/cables coming out) is not fully legible;
  the exact model/dimensions are unknown. Weight 140 g per the first message. Treat as GIẢ ĐỊNH.
- "sonar đúng loại của con cua": the user says the sonar is the same type as the crab's. The entry agent
  found no sonar named in crab-robot-v17g's BOM.md/README.md, so the exact module is unverified;
  the common reference is HC-SR04 (GIẢ ĐỊNH).

```

Lead routing note:

Cập nhật quạt 30×30 mm là loại 5 V. Board bổ sung đầu cấp quạt hai cực có nhãn +5V/GND từ LOAD_5V sau bảo vệ, tính thêm tải quạt; không thêm GPIO điều khiển. Case bổ sung gá quạt và đường dây phía sau turret; chiều dày, khoảng lỗ vít và dòng quạt vẫn chưa xác định, không coi CAD là đã khớp thực tế.

Pin 140 g: người dùng xác nhận cùng bộ đã dùng trên con cua và cho biết chạy ổn. Chưa xác định được model, hóa học, cấu hình cell, điện áp đầu ra, bảo vệ, kích thước hoặc dòng tối đa từ câu “zì 27…”. Power bank USB 5 V hai cổng trong ghi chú entry chỉ là GIẢ ĐỊNH; không áp kích thước hoặc khối lượng ≤120 g của tài liệu cũ lên bộ 140 g này. Giữ khoang dự trù và đai điều chỉnh; board kiểm chứng nguồn trước khi chấp nhận cấp tải xe mới. Lời kể chạy ổn trên cua không chứng minh đủ dòng cho bảy servo và quạt.

Sonar: ảnh đã đọc tại prompts/assets/2026-11-20-sonar-order-hc-sr04p.png ghi HC-SR04P ×2, quảng cáo 3–5.5 V. Dùng HC-SR04P làm tham chiếu thay HC-SR04 chung trong hợp đồng; thông tin này cụ thể hơn giả định của entry. Ảnh đơn hàng chưa xác nhận module thực nhận, kích thước, pinout hoặc mức logic. Board xác minh giao diện/chuyển mức; case cập nhật gá theo tham chiếu có kiểm chứng, giữ hai sonar lưng đối lưng. Giữ ánh xạ GPIO và hành vi đo hiện tại.

Firmware chỉ cập nhật firmware/WIRING.md về quạt và tên sonar; không cần rebuild mã chạy vì ghi chú này không đổi GPIO hay hành vi. Không giao print: chưa có yêu cầu in hoặc xác nhận chi tiết đã in. Các yêu cầu khác giữ nguyên; chưa tuyên bố thử phần cứng hay hoàn thành CAD.

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/IMAGES.md`: SHA-256 `79ba966afbb4d45230c8ef8af6039c4365fdd19fc3daf9bd63b05f3b25753718`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

## 2. board, firmware, case

Note SHA-256: `970ada06549758588b018766ef373dfc419cde2300bb9706493bc9685ee53bda`

Changed contract fields: modules, powerRails, assumptions

User message (verbatim):

```text
[Image #1], pin là 18650 song song

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- [Image #1] is saved at /Users/macbookpro/harnesses/pet-tank/prompts/assets/2026-11-20-sonar-order-hc-sr04p.png
  (original: /private/tmp/claude-501/-Users-macbookpro-harnesses-pet-tank/b9deee89-4ff0-4c8c-b6fa-97952635f127/images/1.png).
  It is a shop order line: "015 Mô Đun Cảm Biến Hc-Sr04P Hc-Sr04-P Cho Arduino 3v-5.5v", quantity x2, 31.757đ.
  The thumbnail shows a blue 2-transducer ultrasonic board with a 4-pin header. So the sonar is
  HC-SR04P (3–5.5 V variant of HC-SR04), and the user has 2 of them. This supersedes the earlier HC-SR04 assumption.
- "pin là 18650 song song" = the battery is 18650 cells wired in parallel (1S, nominal 3.7 V, 2 leads out),
  total 140 g per the first message (≈2 cells, cell count not confirmed). This supersedes the entry agent's
  earlier assumption of a 2-port USB 5 V power bank. The user says this same pack already runs their crab robot.

```

Lead routing note:

Pin 140 g được người dùng xác nhận là các cell 18650 mắc song song, hai dây ra; dùng cấu hình 1S danh nghĩa khoảng 3,7 V làm tham chiếu, bỏ giả định power bank USB 5 V hai cổng. Chưa xác nhận số cell, model, kích thước, dung lượng, dòng tối đa hoặc mạch bảo vệ/sạc; không chốt 2 cell từ khối lượng. Việc đã chạy trên robot cua không chứng minh đủ tải xe mới.

Board cập nhật hồ sơ nguồn và thiết kế đường cấp từ bộ pin kín qua module bảo vệ/sạc đã xác minh và bộ nâng áp 5 V đủ tải; tính cả bảy servo, sonar và quạt. Giữ J_PWR nhận 5 V đã điều chỉnh, không nối trực tiếp pin 1S vào đó; giữ chống cấp ngược USB và trạng thái servo mặc định tắt. Case cập nhật khay/đai pin, chỗ cho module nguồn và đường dây theo tham chiếu có kiểm chứng; kích thước khoang hiện tại vẫn chỉ là dự trù.

Ảnh prompts/assets/2026-11-20-sonar-order-hc-sr04p.png xác nhận dòng đặt hàng HC-SR04P ×2, quảng cáo 3–5,5 V, củng cố ghi chú trước thay HC-SR04 chung. Không suy ra kích thước, pinout hay mức Echo từ ảnh; board kiểm chứng giao diện, case dùng gá phù hợp cho hai sonar lưng đối lưng.

Firmware cập nhật firmware/WIRING.md về pin 1S → bảo vệ/chuyển đổi → nguồn 5 V và tên HC-SR04P; không cần rebuild mã chạy vì giữ GPIO và hành vi. Không giao print: không có yêu cầu in hoặc xác nhận đã in. Giữ yêu cầu quạt 5 V và mọi yêu cầu không liên quan; chưa khẳng định CAD hoàn tất hay phần cứng đã được thử.

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/IMAGES.md`: SHA-256 `79ba966afbb4d45230c8ef8af6039c4365fdd19fc3daf9bd63b05f3b25753718`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

## 3. case, print

Note SHA-256: `7e7f4c02aacd7022041e5024e73ea9147258d8258d998e0ca41ff001d1ca0658`

Changed contract fields: modules, assumptions, tasks

User message (verbatim):

```text
nói lead clone cái bánh xe của con claude-pet qua 2 cái nữa, tao 
  có 4 cái rồi

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- The user already owns 4 printed claude-pet wheels and wants the tank to use that same wheel design,
  with 2 more cloned so there are 6.
- Source of the claude-pet wheels: user's repo https://gitlab.com/triluongmh/claude-pet.git, commit
  3c5e9457995933f800be0044858d026ef6001d83, folder pet-case/case/wheels (recorded as the pet's source in
  /Users/macbookpro/harnesses/claude-pet-case/host/recovery.json). Hash-checked copies (SHA256SUMS) are in
  /Users/macbookpro/harnesses/pet-tank/prompts/assets/claude-pet-wheels-3c5e945/ : STEP+STL of
  07_drive_wheel L/R, 08_drive_guide L/R, 09_horn_cap L/R, 10_idler_wheel L/R, 11_idler_guide L/R,
  ref_servo_L, ref_horn_L, plus drive-assembly.md/.png, hardware-list.md, hardware.json, axle-detail.png.
- Measured from the STLs: wheels 07/10 are Ø54 × 25 mm wide (spiked tread); guides 08/11 Ø46.4 × 8.4 mm;
  horn cap 09 Ø46.4 × 2.8 mm; reference SG90-class horn Ø35 × 5.1 mm.
- In the pet, the 4 wheels are 2 servo-driven fronts (07 + 08 horn slot + 09 nut cap, clamped by 2× M3×16
  around the stock servo horn, servo centre screw through the middle — see drive-assembly.md) and 2 rear
  idlers (10 + 11) on an axle. The tank needs all 6 wheels on 360° servos, so the 2 owned idler wheels may
  lack the servo-horn interface. Which owned wheel is which is not confirmed by the user; treat as GIẢ ĐỊNH.

```

Lead routing note:

Case: dùng đúng mẫu bánh claude-pet tại prompts/assets/claude-pet-wheels-3c5e945/ từ commit 3c5e9457995933f800be0044858d026ef6001d83. Thay mục tiêu bánh Ø52×20 bằng hình học nguồn Ø54×25 mm; giữ gai và thiết kế bánh, tận dụng 4 bánh đã có, clone thêm 2 để đủ 6. Chuẩn bị cặp trái/phải theo kiểm kê, cập nhật CAD, danh sách chi tiết và plate phần cần bổ sung; kiểm khoảng hở toàn hành trình nhún trong envelope hiện hành.

Cả 6 bánh vẫn phải được servo 360° dẫn động. GIẢ ĐỊNH: 4 bánh đang có gồm 2 bánh drive và 2 idler như pet; người dùng chưa xác nhận từng loại. Đối chiếu 07/08/09 với 10/11 và drive-assembly.md; kiểm khả năng dùng adapter/hub để tái sử dụng idler, không mặc nhiên coi idler lắp được horn. Cụm drive dùng 07+08+09 kẹp horn gốc bằng 2 M3×16 và vít tâm servo riêng. Ghi riêng phụ kiện thiếu; không tự tính lại thành 6 bánh phải in mới. Kích thước horn và độ khớp thực còn chưa xác minh.

Print: ghi nhận lời người dùng xác nhận đã có 4 bánh in; loại, revision và mesh hash của các bánh thực chưa xác định, không gán chúng thành bản in đã kiểm chứng của bộ nguồn. Theo dõi phần còn thiếu là 2 bánh cùng phụ kiện được case xác định; chưa gửi job hoặc ghi nhận 2 bánh mới đã in.

Không giao board hoặc firmware: yêu cầu này không đổi pins, rails, hành vi hay firmware/WIRING.md; firmware không cần rebuild. Giữ các yêu cầu khác và các cập nhật trước về pin, sonar, quạt. Đây là chỉ đạo công việc, chưa xác nhận CAD hoàn tất hoặc đã thử lắp thực tế.

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `references/IMAGES.md`: SHA-256 `79ba966afbb4d45230c8ef8af6039c4365fdd19fc3daf9bd63b05f3b25753718`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

## 4. case

Note SHA-256: `5e3e69efc2a1b5450f8f38dafd38ded6cb9a7cebb127978f45f186f9a5437f59`

Changed contract fields: modules, tasks

User message (verbatim):

```text
[Image #2] ngon!!! nhưng mà nói team làm cái mỏ cái xe tank phần màu vàng xéo như cái màu xanh á, bỏ cái màu xanh đi. [Image #3] như tao vẻ là xong.

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- [Image #2] = /Users/macbookpro/harnesses/pet-tank/prompts/assets/2026-11-20-nose-current-blue-wedge.png
  (original /private/tmp/claude-501/-Users-macbookpro-harnesses-pet-tank/b9deee89-4ff0-4c8c-b6fa-97952635f127/images/2.png).
  Screenshot of the current draft case in the viewer, looking into the front of the hull: the yellow hull front is a
  plain vertical box; inside it a separate blue sloped wedge/plate (the display mount) stands up at an angle.
- [Image #3] = /Users/macbookpro/harnesses/pet-tank/prompts/assets/2026-11-20-nose-sketch-chevron.png
  (original .../images/3.png). Side view of the current draft (yellow hull, 3 red wheels visible, turret on top)
  with the user's dark-red lines drawn over the front: one line across the front face at about mid-height,
  ending at a vertex; from that vertex one line runs up and back to the top edge of the hull (near the slot
  where the blue wedge shows), and one line runs down and back to the bottom edge ahead of the first wheel.
  Together they make a ">" chevron nose seen from the side, apex pointing forward at about mid-height.
- Meaning (entry agent's reading): the yellow hull itself should become the ">" nose — the upper sloped face
  (where the screen mounts, per the original request) and the lower sloped face are part of the yellow hull;
  the separate blue wedge part is removed. Positions are read from a sketch, not measured.

```

Lead routing note:

Case: sửa chính vỏ vàng thành mũi dạng > theo prompts/assets/2026-11-20-nose-sketch-chevron.png; ảnh hiện trạng là prompts/assets/2026-11-20-nose-current-blue-wedge.png. Hai mặt nghiêng trên/dưới thuộc vỏ vàng, gặp nhau ở sống mũi hướng về phía trước (-Y), khoảng giữa chiều cao. Màn LILYGO gắn trên mặt nghiêng trên; bỏ riêng cụm nêm/gá màn màu xanh hiện tại, tích hợp chức năng giữ màn vào vỏ. Không xóa các chi tiết xanh khác. Đây là thay hình học, không chỉ đổi màu. Nét vẽ chỉ xác định dáng, không cung cấp kích thước hay góc đo.

Cập nhật CAD, STEP/STL, danh sách chi tiết, hướng dẫn ráp và plate/3MF liên quan; kiểm khoảng hở màn, USB, nút, anten, dây và bánh trước trong toàn hành trình nhún. Giữ envelope và các giao diện hiện hành. Phạm vi thay đổi modules chỉ là cách gá MCU_DISPLAY; tasks chỉ bổ sung việc case. Các yêu cầu khác, gồm pin, sonar, quạt và bánh từ ghi chú trước, tiếp tục có hiệu lực.

Chỉ giao case. Không đổi pins, rails, hành vi hoặc bảng dây firmware/WIRING.md; firmware không cần rebuild. Không giao print vì không yêu cầu vận hành hay xác nhận bản in. Chưa xác nhận CAD hoàn tất hoặc đã thử lắp thực tế.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `references/IMAGES.md`: SHA-256 `bfc16f8e94e1d653c3e9a617fbaa360436732f08fe04315ff7cd71cb4848eadf`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

## 5. case

Note SHA-256: `61110a56fd6d5d758af828f49e2f9aab51934283a2ccada702e3091f2c4b1a1d`

Changed contract fields: modules, tasks

User message (verbatim):

```text
[Image #4] nói team bỏ luôn mấy cây dài dài của cái bánh nhe

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- [Image #4] = /Users/macbookpro/harnesses/pet-tank/prompts/assets/2026-11-20-wheel-hub-tubes.png
  (original /private/tmp/claude-501/-Users-macbookpro-harnesses-pet-tank/b9deee89-4ff0-4c8c-b6fa-97952635f127/images/4.png).
  Rear-quarter view of the current draft: on one side three wheels each have a long cylindrical tube/boss sticking
  straight out from the outer face of the wheel (red/pink/red). The user drew a red line across the outer faces of
  the three wheels, at the wheel face, i.e. cut there.
- Entry agent's reading: "mấy cây dài dài của cái bánh" = these long outer hub tubes. In the claude-pet source they
  are the long axle tube on the outer face of drive wheel 07 / idler wheel 10 (see
  prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md: "Mặt có ống trục dài ... là mặt NGOÀI").
  Remove them on the tank's wheels so the wheel ends flush at the red line. The rest of the wheel clone stays.
  The 4 wheels the user already printed still have these tubes; how to handle those is for the case team.

```

Lead routing note:

Case: bỏ toàn bộ ống trục dài nhô khỏi mặt ngoài của cả sáu bánh, kết thúc ngang mặt bánh theo nét đỏ trong prompts/assets/2026-11-20-wheel-hub-tubes.png. Đây là phần ống ngoài của bánh nguồn 07/10; giữ phần còn lại của mẫu bánh claude-pet, gai bánh và sáu servo dẫn động. Ghi chú này thay yêu cầu giữ nguyên mẫu bánh chỉ ở phần ống bị bỏ.

Cập nhật CAD, STEP/STL, danh sách chi tiết, hướng dẫn ráp và plate/3MF liên quan. Kiểm lại giữ bánh, liên kết horn, đường vào vít tâm và khoảng hở khi nhún; không suy kích thước cắt từ ảnh. Với bốn bánh đã in, case đánh giá khả năng sửa và hướng dẫn xử lý hoặc nêu chi tiết cần thay; không mặc định phải in lại cả sáu, không coi bánh thật đã được cắt hay thử lắp.

Chỉ giao case. Không đổi pins, rails, hành vi hoặc firmware/WIRING.md; firmware không cần rebuild. Không có yêu cầu in hay xác nhận bản in mới để giao print. Phạm vi modules chỉ là cụm bánh hai bên, tasks chỉ bổ sung việc case; envelope và các yêu cầu khác tiếp tục có hiệu lực. Chưa xác nhận CAD hoàn tất hoặc kiểm thử thực tế.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `references/IMAGES.md`: SHA-256 `959dfec7c1b0f0f1a9b92daffa27cfae9a572b5b895de89849781fed872cf69c`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

## 6. case

Note SHA-256: `ca7142776fae60db65c89f0489123b917473823be1e9f228a7f46567e1f92f24`

Changed contract fields: modules, assumptions, tasks

User message (verbatim):

```text
hộp cao quá fen hạ xuống 1/2 đi, chưa có cái mỏ xe tank >. Bề ngang bánh hẹp quá tăng lên khoảng 1/3 size đi. 
Với khung gầm xe hơi thấp so với đất, chạy dễ cạ lắm. Nói team làm cái hệ thống treo đòn bẩy như tao nói á. 1 bên là nối với servor 1 bên tao nối dây thun cho nó nhún, tính chiều cao chổ này lại dùm tao.

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- The user is looking at the draft case in the viewer (latest screenshot they sent:
  /private/tmp/claude-501/-Users-macbookpro-harnesses-pet-tank/b9deee89-4ff0-4c8c-b6fa-97952635f127/images/5.png,
  copied to prompts/assets/2026-11-23-case-r002-overview.png — yellow open box hull, 6 wheels, turret on posts).
- "hộp cao quá ... hạ xuống 1/2" = make the yellow hull box about half its current height.
- "chưa có cái mỏ xe tank >" = the ">" chevron nose requested in note 2026-11-20T1600-05-nose-chevron.md is still
  not visible in the viewer; it is still required.
- "Bề ngang bánh hẹp quá tăng lên khoảng 1/3" = make each wheel's width (tread width along the axle, currently
  25 mm in the claude-pet clone) about one third wider (≈ 33 mm). Entry agent's reading; exact value is the case team's call.
- "khung gầm xe hơi thấp so với đất" = ground clearance under the hull is too low; it scrapes.
- Suspension: build the per-wheel lever (bell-crank) suspension from the original request — each lever pivots on
  the hull, the servo/wheel on one end, a rubber band on the other end pulling it so the wheel can spring up/down.
  The user asks the team to recompute the heights here (pivot height, lever arm lengths, travel, resulting
  ground clearance) so the hull does not scrape.

```

Lead routing note:

Case: giảm chiều cao hộp thân vàng còn khoảng 1/2 bản nháp trong prompts/assets/2026-11-23-case-r002-overview.png; đo chiều cao từ CAD để ghi rõ trước/sau, không suy mm từ ảnh hoặc thu nhỏ toàn xe. Hoàn thiện chính vỏ vàng thành mũi > theo prompts/assets/2026-11-20-nose-sketch-chevron.png: hai mặt nghiêng gặp nhau ở sống mũi, màn gắn mặt trên, bỏ riêng nêm xanh gá màn như ghi chú trước.

Tăng bề rộng dọc trục của cả sáu bánh khoảng 1/3: từ tham chiếu 25 mm lên khoảng 33,3 mm, case chốt kích thước phù hợp. Giữ đường kính 54 mm, gai bánh, sáu servo dẫn động và yêu cầu bỏ ống ngoài nhô dài. Yêu cầu rộng hơn thay phần giữ nguyên bề rộng bánh trước đây. Đánh giá adapter hoặc chi tiết thay cho bốn bánh người dùng đã in; không mặc định chúng đã phù hợp hoặc cần in lại cả sáu.

Dựng đúng sáu hệ treo đòn bẩy độc lập: pivot trên thân, servo cùng bánh ở một đầu, đầu đối diện có móc dây thun kéo về thân. Tính lại cao độ pivot, chiều dài/tỉ số hai tay đòn, vị trí nghỉ có tải, hành trình lên/xuống, chặn hành trình và khoảng sáng gầm. Công bố khoảng sáng tại nghỉ và khi nén hết, kiểm cả đáy thân/mũi, bánh, servo và dây trong toàn hành trình. Khối lượng tải, lực thun và độ võng chưa đo phải ghi là giả định; không khẳng định đã hết cạ ngoài thực tế.

Cập nhật CAD, STEP/STL, danh sách chi tiết, hướng dẫn ráp, overview và plate/3MF liên quan; kiểm đủ chỗ cho PCB, pin, module nguồn, màn, quạt và turret sau khi hạ thân. Phạm vi modules là bố trí cơ khí chịu ảnh hưởng; assumptions thay mục tiêu bề rộng và nhún cần tính lại; tasks bổ sung việc case. Giữ hệ tọa độ, envelope hiện hành và các yêu cầu không liên quan.

Chỉ giao case. Không đổi pins, rails, hành vi hoặc bảng dây firmware/WIRING.md; firmware không cần rebuild. Không giao board hoặc print vì không có yêu cầu sửa điện, vận hành máy in hay xác nhận bản in mới. Đây là chỉ đạo sửa thiết kế, chưa xác nhận CAD hoàn tất hoặc thử nghiệm thực tế.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `references/IMAGES.md`: SHA-256 `742c8c097b02b57ba56d9ec146dade74ced6e3d8deb68641f610a23c151a1811`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `references/user-images/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

## 7. case

Note SHA-256: `c9c1cf62d566157bd29fc611f1df50212f58369204cda92531a46a19a08ef8bd`

Changed contract fields: modules, assumptions, tasks

User message (verbatim):

```text
[Image #6] đó ý tưởng đó fen

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- [Image #6] = /Users/macbookpro/harnesses/pet-tank/prompts/assets/2026-11-23-style-apc-references.png
  (original /private/tmp/claude-501/-Users-macbookpro-harnesses-pet-tank/b9deee89-4ff0-4c8c-b6fa-97952635f127/images/6.png).
  A mood board of three renders of 8-wheel armoured personnel carriers (internet images, not the user's CAD):
  1) dark green APC with a sharp wedge/boat-shaped nose (">" seen from the side: upper glacis sloping back, lower
     plate sloping under), faceted hull whose upper side plates lean inward above the wheels, small turret on top;
  2) grey untextured model, separate turret lifted off, low faceted hull with angled nose and a round turret ring;
  3) tan camo APC with a tall boxy hull, flat sides and a remote weapon station.
- Entry agent's reading: "ý tưởng đó" = this is the look the user wants — mainly images 1–2: a LOW hull, wedge ">"
  nose, angled/faceted upper side plates sloping inward over the wheels, wheels exposed under the hull with real
  ground clearance, turret on a ring on top. It is style direction for the requested changes (half-height hull,
  ">" nose, suspension), not a request to copy any specific real vehicle or to add 8 wheels; the tank stays 6 wheels.
  No dimensions are taken from these images.

```

Lead routing note:

Case: dùng prompts/assets/2026-11-23-style-apc-references.png làm định hướng dáng xe, ưu tiên hình trên và hình dưới trái: thân thấp, mũi > gồm hai mặt nghiêng gặp nhau, các mặt hông trên nghiêng vào trong, bánh lộ dưới thân có khoảng sáng gầm, turret trên vòng đỡ sát nóc. Giữ màn trên mặt nghiêng của chính mũi vỏ và turret hai sonar; không thêm vũ khí hoặc đổi thành tám bánh.

Tiếp tục yêu cầu ghi chú 6: thân cao khoảng một nửa bản nháp, sáu bánh rộng thêm khoảng 1/3, sáu hệ treo đòn bẩy với servo/bánh một đầu và thun đầu đối diện; tính và kiểm khoảng sáng cùng va chạm toàn hành trình. Ảnh chỉ xác định phong cách, không cung cấp kích thước, góc hay bằng chứng lắp vừa. Cập nhật CAD, STEP/STL, overview, hướng dẫn và plate/3MF chịu ảnh hưởng.

Phạm vi modules là hình học/gá cơ khí liên quan; assumptions bổ sung nguồn tham khảo phong cách; tasks bổ sung việc case. Giữ envelope, hệ tọa độ và mọi yêu cầu không liên quan từ các ghi chú trước. Không đổi pins, rails, hành vi hoặc firmware/WIRING.md; firmware không cần rebuild. Chỉ giao case, không có yêu cầu điện hay in thực tế mới. Chưa xác nhận CAD hoàn tất, đã in hoặc thử thực tế.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `prompts/assets/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `references/IMAGES.md`: SHA-256 `93ac22eae5f50c54d84e5cfb292685e2b9f264b463f168e92f0c7e9b6e35e13a`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `references/user-images/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `references/user-images/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

## 8. board, firmware, case, print

Note SHA-256: `52b5a7b49794e2797ccff9a78a6298a64ab29bf400afcb34fb6cdfe213e4fa72`

Changed contract fields: coordinateFrame, board, powerRails, pins, modules, mechanicalEnvelopeMm, firmwareBehavior, assumptions, tasks

User message (verbatim):

```text
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

```

Lead routing note:

Người dùng báo đã in hết robot-tank build v1 (cadsmith, check pass 25/11/2026) và chọn bộ này làm case của dự án: "Mình khỏi làm". Bản gốc nằm ở prompts/assets/robot-tank-cadsmith-v1/ (model.py, report.json, STEP, SHA256SUMS). Bộ STEP đầy đủ ở /Users/macbookpro/cad-models/robot-tank/builds/v1/, chỉ được đọc. Không đọc hay sửa model.py ở gốc thư mục đó vì một phiên khác đang sửa file này, và nó không còn khớp với bản đã in.

Case: dừng thiết kế vỏ mới. Không tái tạo hay sửa các chi tiết v1 đã in: chassis, hull, lid, turret_head, led_bracket, 6 arm, 6 bánh Ø42×18,7 mm. Bộ v1 này thay cho các yêu cầu trước về mũi ">", bỏ ống bánh, thân thấp, bánh clone claude-pet Ø54 rộng ~33 mm, hệ treo đòn bẩy và dáng APC.
Việc của case:
- Nhập bộ STEP v1 kèm checksum làm case chính thức. Lập parts.json và hướng dẫn ráp.
- "Soi" bộ v1 và báo cáo. Phải đo lòng thân, cửa sổ màn 29 mm trên mặt nghiêng 45°, khoang 2×18650, 4 cột Nano không dùng, turret SG90 gắn thẳng không có ổ đỡ, hành trình nhún, khoảng sáng gầm và lối vào USB/Type-C.
- Chỉ ra những gì còn thiếu: gá ESP32, PCA9685, module nguồn, board/carrier và quạt 30×30. Cửa sổ sau v1 chỉ là lỗ vuông 16 mm.
- Thiếu gì thì chỉ đề xuất chi tiết in bổ sung kẹp hoặc bắt vít vào phần đã in. Plate/3MF chỉ dành cho chi tiết bổ sung, không gửi job in.
- Công bố hộp module đo được cho board và firmware. Chưa coi việc lắp vừa là đã kiểm chứng.

Khung tọa độ: giữ quy ước trục +X phải, +Y đuôi, +Z lên, mũi về -Y. Gốc đổi sang gốc của model v1, ở mặt đất tâm xe. Ánh xạ: X = −Y_v1, Y = −X_v1, Z = Z_v1. Envelope theo report v1 là khoảng 108,4×166,4×118,3 mm (X×Y×Z); case xác nhận lại.

Board: carrier 100×70 không còn vừa, vì chassis v1 rộng ngoài chỉ 68 mm. Board chọn lại outline, lỗ bắt và cách lắp theo số đo case (carrier nhỏ hơn hoặc nối dây giữa các module).
- MCU và màn tham chiếu đổi từ LILYGO T-Display-S3 sang ESP32 DevKit và màn ST7789 1,54" 240×240 SPI. Lý do: cửa sổ màn đã in làm cho màn 1,54", và người dùng có sẵn hai món này. Loại DevKit 30 chân chỉ là GIẢ ĐỊNH, cần đối chiếu module thật.
- Board công bố bảng chân mới. Tránh chân strapping. Giữ PCA9685 0x40, CH0–5 cho bánh, CH6 cho turret, cùng PCA_OE_N, ACT_EN và chuyển mức/kiểm mức Echo cho HC-SR04P theo điện áp cấp.
- Bảng chân trong firmware-chat-2026-11-25.md chỉ là tham khảo, chưa thử, và không có OE/ACT_EN.
- Nguồn: 18650 nằm trong khoang v1, đi qua các module sạc/boost 1S "5V 2A" người dùng có (×4). Dòng, mạch bảo vệ và cách nối cell chưa xác minh. Một module không đủ cho 7 servo cộng quạt. Tách nhánh servo và nhánh logic, GND chung, không nối song song đầu ra boost khi chưa kiểm chứng.
- LOGIC_3V3 lấy từ LDO của DevKit; board tính lại tải.

Firmware: phải rebuild. Đích đổi sang ESP32 (không phải S3), driver ST7789 SPI 240×240, mặt pet chuyển sang 240×240. Liên kết host qua cầu USB-UART của DevKit. Nút dừng cục bộ do board chỉ định thay cho nút của LILYGO. Cập nhật firmware/WIRING.md theo bảng chân board công bố. Giữ mọi đường dừng, phân xử chế độ, mặc định đứng yên và giao thức MOTOR/CUE. Firmware WiFi/joystick trong file chat chưa được người dùng yêu cầu cho dự án này, chỉ là tham khảo chưa thử.

LED: v1 có giá thanh WS2812 và lỗ đèn hậu 5 mm. Phần điện cho LED vẫn là câu hỏi mở, chưa bắt buộc.

Print: ghi nhận theo lời người dùng là đã in đủ bộ v1 (chassis, hull, lid, turret_head, led_bracket, 6 arm, 6 bánh). Máy, vật liệu, ngày in và việc file in có khớp hash v1 hay không chưa xác minh. Không còn theo dõi 2 bánh claude-pet cần in thêm. Không gửi job mới.

Các yêu cầu không liên quan vẫn giữ. Chưa tuyên bố CAD hoàn tất, chưa thử lắp hay chạy phần cứng.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `prompts/assets/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `prompts/assets/robot-tank-cadsmith-v1/SHA256SUMS`: SHA-256 `fd36ec06531bd98559bd57699e7c4ae1f27d2d3465595212dc66fce67982622f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-53-33-PM.png`: SHA-256 `d324a2660e3081f5a89dd5be99491015ac7b980a243e6fe8732f97c7ee578199`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-54-41-PM.png`: SHA-256 `b29dbf3aaf5913d13fcc298cd43b70d6db0f5033632dd308f08cf127ab876b60`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-11-PM.png`: SHA-256 `8b83dc3d4efa4be511065ca42dd6e4b82a9055542731824dc392dfc95900281f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-25-PM.png`: SHA-256 `a1ffd4756e4a5f066c85068d00c5381cb19f6ee922ae66f53dc2eb8d6714f2f3`

Reference `prompts/assets/robot-tank-cadsmith-v1/arm_front_left.step`: SHA-256 `b4dd773ca028ee345abd00851feb53026f53e84a3cdafe051fb5683e56458d24`

Reference `prompts/assets/robot-tank-cadsmith-v1/chassis.step`: SHA-256 `e6afd37a840523a3783d34da000b88e1229cc5095279c4e7815be06e532cddd3`

Reference `prompts/assets/robot-tank-cadsmith-v1/drawing.svg`: SHA-256 `7b1abe4cfb992d018b632e4d73547a2f7a0b8a9ff4c2bee61b31b661a27e8e3d`

Reference `prompts/assets/robot-tank-cadsmith-v1/firmware-chat-2026-11-25.md`: SHA-256 `7a095130f80f2379d2aac29e43f1d15d96e8b35275bb9deb3f12420dde6d5f48`

Reference `prompts/assets/robot-tank-cadsmith-v1/hull.step`: SHA-256 `3900b637ffd4bb657ede788ea70c96d86ba885747979970047afd5cc850e108a`

Reference `prompts/assets/robot-tank-cadsmith-v1/led_bracket.step`: SHA-256 `fe4e6526d0ae8038e4f87133edaf4b38cfdc89f511f7a915c33bc4e628cb7197`

Reference `prompts/assets/robot-tank-cadsmith-v1/lid.step`: SHA-256 `1915dffb799332f7871ce96f913d083839c2e8a479c60d0018ed125a1db3f07f`

Reference `prompts/assets/robot-tank-cadsmith-v1/model.py`: SHA-256 `0500d9de5b6c818b41381bce4887e64baa84474537012df9d71f80a20418808d`

Reference `prompts/assets/robot-tank-cadsmith-v1/report.json`: SHA-256 `6cd8df6d9dbc13c06e217fccea82c53eccb55df330fa69659488cb520edf00bc`

Reference `prompts/assets/robot-tank-cadsmith-v1/turret_head.step`: SHA-256 `14bda38c48e4c48fd481487016ef6267d05754bf07f060570ccfd8e8fa9aaf77`

Reference `prompts/assets/robot-tank-cadsmith-v1/wheel_front_left.step`: SHA-256 `136028340aedc346d6aaba9db250e0a106f3b080e0661ad1da7b39ddf9c76ae1`

Reference `references/IMAGES.md`: SHA-256 `93ac22eae5f50c54d84e5cfb292685e2b9f264b463f168e92f0c7e9b6e35e13a`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `references/user-images/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `references/user-images/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

## 9. board, case

Note SHA-256: `26b0ea5e6ba885938587576b25c07a5a0217e2237f58721f65e2086d49971af1`

Changed contract fields: board, modules, mechanicalEnvelopeMm, assumptions, tasks

User message (verbatim):

```text
đi ăn cắp tiếp fen ơi, bên này tụi tao mới vẽ lại nữa

---
Entry-agent note (clearly labelled facts to interpret the message; not the user's words):
- "bên này tụi tao mới vẽ lại nữa" = the cadsmith robot-tank project (/Users/macbookpro/cad-models/robot-tank) has new
  builds since v1. Latest is build v5 (all checks passed, 2026-11-27). "đi ăn cắp tiếp" = adopt v5 as the case too.
- v5 keeps every v1 part unchanged in size (chassis, hull, lid, turret_head, led_bracket, 6 arms, 6 wheels — the
  parts the user already printed) and ADDS a board stack (from the cadsmith chat):
  stack_base 92×43×6 (bolts with M3), stack_tier_1 and stack_tier_2 74×43×29 each (identical plug-stack tiers,
  tier 1 holds the PCA9685, tier 2 holds the ESP32; print more tiers to add boards), and stack_turret_mount
  109×43×35 (top cap of the stack: SG90 turret pocket + a 45° front face with a 29×29 mm window for the 1.54"
  screen). So the turret and the screen each have two mounting options: on the hull lid/nose as in v1, or on top of
  the stack. The cadsmith chat says the user leaves the lid off and the stack stands on the chassis.
  Reference models in v5: pca9685, esp32 (cadsmith assumed PCA9685 62.2×25.4 and ESP32 DevKit 30-pin 51.5×28.3).
- Whether the user has printed the v5 stack parts is not stated (v1 parts are printed per the previous message).
- Hash-checked copies: /Users/macbookpro/harnesses/pet-tank/prompts/assets/robot-tank-cadsmith-v5/ (model.py,
  report.json, STEP of chassis/hull/lid/stack_base/stack_tier_1/stack_turret_mount/pca9685/esp32/screen_stack,
  drawing.svg, SHA256SUMS). Full set: /Users/macbookpro/cad-models/robot-tank/builds/v5/. Do not edit that folder.

```

Lead routing note:

Người dùng: "đi ăn cắp tiếp fen ơi, bên này tụi tao mới vẽ lại nữa". Nghĩa là lấy luôn build v5 của cadsmith robot-tank (check pass 27/11/2026) làm case. Bản sao đã kiểm hash nằm ở prompts/assets/robot-tank-cadsmith-v5/. Bộ đầy đủ ở /Users/macbookpro/cad-models/robot-tank/builds/v5/, chỉ đọc, không sửa thư mục đó.

v5 giữ nguyên kích thước mọi chi tiết v1 đã in và thêm một cụm board stack:
- stack_base 92×43×6: 4 lỗ M3, bước 82×20.
- stack_tier_1 và stack_tier_2, mỗi cái 74×43×29: hai tầng giống nhau, cắm chồng bằng chốt 4,4 vào lỗ 5,0, mỗi tầng cao 26 mm. Tầng 1 giữ PCA9685 trên 4 trụ M2.5 bước 55,9×19,05. Tầng 2 giữ ESP32 DevKit bằng 2 ray. Mỗi tầng có 4 khe dây rút cho module không có lỗ. Muốn thêm board thì in thêm tầng.
- stack_turret_mount 109×43×35: nắp trên cùng, có ổ SG90 cho turret và mặt nghiêng 45° phía trước với cửa sổ 29×29 cho màn 1,54".

Theo chat cadsmith, người dùng bỏ lid và dựng stack lên chassis. Riêng model v5 lại đặt stack đứng rời cạnh xe (stack_xy 0,−112), nên envelope trong report v5 (166,4×187,68×118,3) không phải envelope khi lắp lên xe. Chưa rõ người dùng đã in phần stack hay chưa, nên không coi là đã in.

Case:
- Nhập các STEP stack của v5 kèm checksum: stack_base, stack_tier (×2, hoặc nhiều hơn), stack_turret_mount. Thêm chúng vào parts.json và hướng dẫn ráp. Không tái tạo hay sửa các chi tiết v1 đã in.
- Hash STEP của chassis, hull và lid ở v5 khác v1. Phải so hình học. Nếu lệch thì bản v1 đã in là chuẩn.
- Kiểm tra cấu hình bỏ lid và stack đứng trên chassis:
  - Bước lỗ M3 82×20 của stack_base có khớp lỗ nào trên chassis/hull đã in không.
  - Khe hở giữa stack và hull, khoang 2×18650, các servo bánh và dây.
  - Envelope Z mới khi có turret trên stack, và trọng tâm.
  - Lối cáp từ ESP32 lên màn trên mặt stack và từ PCA9685 xuống 7 servo.
  - Lối vào USB của DevKit và cổng Type-C của module sạc.
- Nếu không khớp thì chỉ đề xuất adapter in thêm, bắt vít hoặc kẹp vào phần đã in, không khoan hay sửa phần đã in.
- Ghi rõ hai phương án cho turret và màn: (a) turret trên lid, màn sau glacis của hull như v1; (b) cả hai lên stack. Nếu bỏ lid thì ổ turret và cột Nano trên lid không còn dùng. Lead chưa chốt phương án nào, case báo ưu nhược điểm.
- Quạt 30×30 và module nguồn vẫn chưa có chỗ gắn. Xem chúng có vào được một tầng thêm hoặc vào khe dây rút không.
- Plate/3MF chỉ để chuẩn bị, không gửi job in. Công bố hộp module đo được và vị trí từng tầng cho board.

Board:
- Mounting mặc định giờ là module rời gắn trên stack, nối dây giữa các module: PCA9685 ở tầng 1, ESP32 DevKit ở tầng 2. Tạm bỏ carrier riêng.
- Nếu vẫn muốn carrier thì nó phải lọt tầng 74×43 (cửa sổ giữa 46×26), dùng lỗ 55,9×19,05 M2.5 hoặc ray DevKit, và để chừa chỗ cho đầu dây servo cắm vào.
- Cập nhật chiều dài và đường dây giữa các tầng, tới màn và turret cho cả hai phương án, cùng module nguồn có thể đặt trên tầng thêm.
- Kích thước PCA9685 62,2×25,4 và ESP32 DevKit 30 chân 51,5×28,3 là GIẢ ĐỊNH của cadsmith. Đo module thật trước khi chốt.
- Không đổi bảng chân, rail, PCA9685 0x40 (CH0–5 bánh, CH6 turret), PCA_OE_N, ACT_EN, kiểm mức Echo và cách tách nhánh servo/logic.

Firmware: tin này không đổi chân, rail, hành vi hay bảng dây trong firmware/WIRING.md, nên firmware không cần rebuild vì tin này. Việc rebuild cho ESP32 + ST7789 240×240 từ note trước vẫn giữ nguyên.

Print: không có yêu cầu in. Không gửi job.

Các yêu cầu không liên quan vẫn giữ. Chưa có thử lắp, đo thực tế hay CAD hoàn tất nào được xác nhận.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `prompts/assets/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `prompts/assets/robot-tank-cadsmith-v1/SHA256SUMS`: SHA-256 `fd36ec06531bd98559bd57699e7c4ae1f27d2d3465595212dc66fce67982622f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-53-33-PM.png`: SHA-256 `d324a2660e3081f5a89dd5be99491015ac7b980a243e6fe8732f97c7ee578199`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-54-41-PM.png`: SHA-256 `b29dbf3aaf5913d13fcc298cd43b70d6db0f5033632dd308f08cf127ab876b60`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-11-PM.png`: SHA-256 `8b83dc3d4efa4be511065ca42dd6e4b82a9055542731824dc392dfc95900281f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-25-PM.png`: SHA-256 `a1ffd4756e4a5f066c85068d00c5381cb19f6ee922ae66f53dc2eb8d6714f2f3`

Reference `prompts/assets/robot-tank-cadsmith-v1/arm_front_left.step`: SHA-256 `b4dd773ca028ee345abd00851feb53026f53e84a3cdafe051fb5683e56458d24`

Reference `prompts/assets/robot-tank-cadsmith-v1/chassis.step`: SHA-256 `e6afd37a840523a3783d34da000b88e1229cc5095279c4e7815be06e532cddd3`

Reference `prompts/assets/robot-tank-cadsmith-v1/drawing.svg`: SHA-256 `7b1abe4cfb992d018b632e4d73547a2f7a0b8a9ff4c2bee61b31b661a27e8e3d`

Reference `prompts/assets/robot-tank-cadsmith-v1/firmware-chat-2026-11-25.md`: SHA-256 `7a095130f80f2379d2aac29e43f1d15d96e8b35275bb9deb3f12420dde6d5f48`

Reference `prompts/assets/robot-tank-cadsmith-v1/hull.step`: SHA-256 `3900b637ffd4bb657ede788ea70c96d86ba885747979970047afd5cc850e108a`

Reference `prompts/assets/robot-tank-cadsmith-v1/led_bracket.step`: SHA-256 `fe4e6526d0ae8038e4f87133edaf4b38cfdc89f511f7a915c33bc4e628cb7197`

Reference `prompts/assets/robot-tank-cadsmith-v1/lid.step`: SHA-256 `1915dffb799332f7871ce96f913d083839c2e8a479c60d0018ed125a1db3f07f`

Reference `prompts/assets/robot-tank-cadsmith-v1/model.py`: SHA-256 `0500d9de5b6c818b41381bce4887e64baa84474537012df9d71f80a20418808d`

Reference `prompts/assets/robot-tank-cadsmith-v1/report.json`: SHA-256 `6cd8df6d9dbc13c06e217fccea82c53eccb55df330fa69659488cb520edf00bc`

Reference `prompts/assets/robot-tank-cadsmith-v1/turret_head.step`: SHA-256 `14bda38c48e4c48fd481487016ef6267d05754bf07f060570ccfd8e8fa9aaf77`

Reference `prompts/assets/robot-tank-cadsmith-v1/wheel_front_left.step`: SHA-256 `136028340aedc346d6aaba9db250e0a106f3b080e0661ad1da7b39ddf9c76ae1`

Reference `prompts/assets/robot-tank-cadsmith-v5/SHA256SUMS`: SHA-256 `ceb49db77849f506f7f624d7fb3a964dfa9408fd54aba8b55d7443ed6d43a72a`

Reference `prompts/assets/robot-tank-cadsmith-v5/chassis.step`: SHA-256 `2a4a4b5caf1218b0e081c69a0029eb9e92772ba7e2c575f4c4942258a234a80d`

Reference `prompts/assets/robot-tank-cadsmith-v5/drawing.svg`: SHA-256 `1013f0e4ad81fcfe0f193cf9292237a79aac91b532d993338b8cb9961fea0c62`

Reference `prompts/assets/robot-tank-cadsmith-v5/esp32.step`: SHA-256 `1e1b9f199f40cbc8346660a554a7bc0eaa137e222aca020432c9b6ee995f3244`

Reference `prompts/assets/robot-tank-cadsmith-v5/hull.step`: SHA-256 `6cd01dacaef686c21fa5119986c43f2ef7c2d8db6df56c94675078a2e9e2b98b`

Reference `prompts/assets/robot-tank-cadsmith-v5/lid.step`: SHA-256 `42e1de372e21ac008d5d4864d65e8c505fab3bcb0d22fa97e83994ccea0661bc`

Reference `prompts/assets/robot-tank-cadsmith-v5/model.py`: SHA-256 `2f8277f217dca32d9de4f0a5969be4be22701be013b0ed25dd4aeed0fddfaa82`

Reference `prompts/assets/robot-tank-cadsmith-v5/pca9685.step`: SHA-256 `c7a31efb23078f31045ac60bcb6f43cec080d0de6c63ba09723f2450c657761a`

Reference `prompts/assets/robot-tank-cadsmith-v5/report.json`: SHA-256 `2b9d95d91e79ab07124b3fb8422dd0ac176abc664b2472b16a179c45c8182d7f`

Reference `prompts/assets/robot-tank-cadsmith-v5/screen_stack.step`: SHA-256 `3bd302e3582fc7ff37062fc814b23a46a110fa347e8bf0b757daec9bb1a80ce5`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_base.step`: SHA-256 `c37cb1ef41dbaafb1440761c2c29ea70caa9919c73edd964a4a1aba2f8b53d2f`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_tier_1.step`: SHA-256 `0803025ca855faae62f574628d7ec50ab7df0843253c977e27da3c1c53560c34`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_turret_mount.step`: SHA-256 `e1fc492f484defe7afd62458dbdb383addbd966ba883e65336ea455c86c70c54`

Reference `references/IMAGES.md`: SHA-256 `93ac22eae5f50c54d84e5cfb292685e2b9f264b463f168e92f0c7e9b6e35e13a`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `references/user-images/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `references/user-images/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

## 10. firmware

Note SHA-256: `c4e55f73e992daecb49e1b21711e192689ff69e941050d97f7076d509658252a`

Changed contract fields: firmwareBehavior, assumptions, tasks

User message (verbatim):

```text
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

```

Lead routing note:

Người dùng: "tham khảo cái UI trên Phone của [crab-robot-v17g]… làm tao 1 cái UI điều khiển như vậy". Đây là yêu cầu mới, trả lời câu hỏi mở trước đó: xe tăng giờ cần điều khiển bằng điện thoại qua Wi-Fi, ngoài liên kết USB với host. Tham chiếu đã kiểm hash: prompts/assets/crab-phone-ui/ui.html, network_http.h, DIRECT-AP.md. Chỉ đọc làm mẫu, không sửa repo crab.

Firmware (phải rebuild, vẫn trên đích ESP32 DevKit + ST7789 240×240 theo note trước):
- ESP32 tự phát AP mở riêng của xe, tên kiểu "XeTang-XXXX" do firmware chọn. Trang ở http://192.168.4.1/, captive portal trả cùng trang. Màn 240×240 hiện tên mạng, địa chỉ và QR. Wi-Fi nhà là tùy chọn như crab: quét, nhập mật khẩu, lưu NVS, không trả hay ghi log mật khẩu, báo lỗi tiếng Việt. Thiếu Wi-Fi nhà thì AP vẫn chạy. Giao diện bằng tiếng Việt.
- Trang "Lái": pad 8 hướng giữ để chạy, thả là dừng (↖↑↗←DỪNG→↙↓↘), cùng 3 mức tốc độ 0.4/0.65/1. Firmware ánh xạ sang lái vi sai 6 bánh: tới/lui, xoay tại chỗ trái/phải, cua chéo. API theo mẫu crab: session có token, một chủ điều khiển tại một thời điểm; move có seq/dir/fresh; lease lệnh khoảng 500 ms; GET status. Hằng số tự chọn và ghi là mục tiêu chưa thử.
- Trang "Ráp": hiệu chuẩn trung tính và chiều quay từng bánh CH0–5, cùng tâm và giới hạn turret CH6. Dùng chung cơ chế hiệu chuẩn có giới hạn thời gian mà hợp đồng đã yêu cầu. Mở trang này thì khóa lái.
- Điện thoại là nguồn "điều khiển tay" trong phân xử chế độ. Không giành quyền khi host cue hoặc chế độ tự dò đang chạy, trừ khi đã STOP. STOP từ bất kỳ nguồn nào đều thắng. Giữ mọi đường dừng sẵn có: hết lease, thả nút, đổi hay mất session, mất client AP, watchdog, lỗi I2C, nút dừng cục bộ do board chỉ định. Thêm vào đó: chỉ cho tới/lui khi dữ liệu sonar hướng đó còn mới và tin cậy, khi bị chặn thì trang hiện lý do. Khởi động luôn đứng yên, mặc định OE cao/ACT_EN thấp.
- Nút đèn: điện cho LED vẫn là câu hỏi mở và chưa có chân. Hiện nút ở trạng thái "chưa nối", không tự thêm GPIO.
- Status chỉ đọc có thể gồm chế độ, lý do khóa và hai khoảng cách sonar, đo không hợp lệ thì ghi rõ. Người dùng CHƯA yêu cầu điều khiển turret bằng tay hay nút bật tự dò trên điện thoại. Để làm câu hỏi mở, chưa thêm.
- Giữ USB-UART và giao thức MOTOR/CUE. Viết test bằng mock cho parser HTTP, token/seq, lease, phân xử nguồn và khóa theo sonar. Bổ sung hướng dẫn kết nối điện thoại vào tài liệu firmware. firmware/WIRING.md không đổi chân.
- Không flash, không chạy servo. Chưa khẳng định tầm phủ, độ ổn định radio hay hành vi trên điện thoại thật.

Không giao board: không đổi chân, rail hay bảng dây. Radio nằm sẵn trong DevKit, nguồn logic vẫn đi theo nhánh logic từ pin như note trước. Không giao case hay print: không đổi hình học hay plate, không có yêu cầu in. Các yêu cầu khác giữ nguyên, kể cả case v1/v5 stack và các phương án turret/màn chưa chốt.

Reference `prompts/assets/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `prompts/assets/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `prompts/assets/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `prompts/assets/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `prompts/assets/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `prompts/assets/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.step`: SHA-256 `969db3a4c0dfff0078d15465cc651843cbd3d1639416684627861e45a0739b99`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_L.stl`: SHA-256 `58acbc848111aeb9494a65ba38b133a280eff92bb77ed162ee169deb7f1f61c4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.step`: SHA-256 `43279bc785fc8d484c790f5160b2e69abf27a15eb3eb2ed1ebbf7c774f76832c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/07_drive_wheel_R.stl`: SHA-256 `161f27fb9624ff1412b5072694928c3fcaace2ed75af16e1fde3cf04cedfe654`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.step`: SHA-256 `385515423bcdc6acfed95c63f9a3354fcb8b49e09fb8b2ed42e8503911c46d29`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_L.stl`: SHA-256 `919fc9f071681ace65fc84683e6a7028b9691ea528694accf323183ecc6f4fc8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.step`: SHA-256 `4e1314e402aea54170ea0aa94cb078576869a96217a13ed62f060640c9afe9e8`

Reference `prompts/assets/claude-pet-wheels-3c5e945/08_drive_guide_R.stl`: SHA-256 `3b1aa783f94aa5d530554a75218bfc182b380de5a6ca7ce4470be7a4818ffb85`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.step`: SHA-256 `c8e3ae32a0e409d93defaad638d99eabad35ed5cebaedc255d37e693a9011f20`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_L.stl`: SHA-256 `46df24d095c0127fe27f21ec1b31ad002e65dc001b0a40f6d3f2d5520af51532`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.step`: SHA-256 `3abb6260052ae468d736585d6dfce9084a6beeb59143ae96b1d9b0f40910c343`

Reference `prompts/assets/claude-pet-wheels-3c5e945/09_horn_cap_R.stl`: SHA-256 `e0c9a1c80b5a358d12182907ad0a0e82da2061809d7d62cf018baaf9cd442271`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.step`: SHA-256 `f495d1eb35fef2a9eed51f58e2a6ef22435b1dbc399408085ed8580fd7342140`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_L.stl`: SHA-256 `e785045c004390718c76d0394a52d2c28b8ad755996bbccd66f405d35a416608`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.step`: SHA-256 `ad419db5aa7749597e1997ef2d56037476f57367f5211cadee506430be5349a4`

Reference `prompts/assets/claude-pet-wheels-3c5e945/10_idler_wheel_R.stl`: SHA-256 `6014f24cd63819adb952e94885dfaca4b1c2ed855c717ae4dc7ddf75c89c46ad`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.step`: SHA-256 `348ad795e8e70f163d5cc1daf50e37ba25c6602077af0a5fbf0ada04b3f6830c`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_L.stl`: SHA-256 `05716c2d510ca1bd9f01d0aa1a976996effea12269e3588a538cd0cd33915fee`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.step`: SHA-256 `6e1a41f7deea6010429c6dcca5b1867323dc1c524b011f150afc8f34cabebec2`

Reference `prompts/assets/claude-pet-wheels-3c5e945/11_idler_guide_R.stl`: SHA-256 `b009e198d5bfbb45556c43a89ff5c17e7e9039b2a654e73aa05be8b3ca8d5740`

Reference `prompts/assets/claude-pet-wheels-3c5e945/SHA256SUMS`: SHA-256 `370c4b538888c0a473110b8af1866a886ac8cdf627550fa7ee8e9878a8bc030b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/axle-detail.png`: SHA-256 `5594247b82f15ab6cc93a9a3e77585e074a37c17bf88346c62eace9389eedc37`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.md`: SHA-256 `56ab8c38cd6c2e20c282404da518602136efd1e1c9ead7c7e66f621b143a356e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/drive-assembly.png`: SHA-256 `408d9165e9881c0498c1663346f7f0b76af402c76dec11096906c415abcc8c8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware-list.md`: SHA-256 `01457ae7422838001fc6dae61b6a903eb6138e1a6b281621729ec6f131f19661`

Reference `prompts/assets/claude-pet-wheels-3c5e945/hardware.json`: SHA-256 `806e32561d1e905e4b2d78685a0e3a77ad41645faf5d2fd0e7115d59202c9a8e`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.step`: SHA-256 `d26c301b04d63d73695ba24594599564a2a5fa411f3e2a6c81ddd35cf5ed91a6`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_horn_L.stl`: SHA-256 `80157464e65b1e7d151588572b729107c3e7e64514a53caa6196277670392a91`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.step`: SHA-256 `10beadf6998135b463df2ee682bf13a799b60240efb63f93d6deff2ee0e9aa0b`

Reference `prompts/assets/claude-pet-wheels-3c5e945/ref_servo_L.stl`: SHA-256 `e3954c0479fc9013c52c24156a8508e0a2ef049d123e9e896eb553475d3a6f8b`

Reference `prompts/assets/crab-phone-ui/DIRECT-AP.md`: SHA-256 `99050aa01f4a7c13da1c58b35ac3339ccb3e67a1a851ea200583d8f2bd83d41f`

Reference `prompts/assets/crab-phone-ui/SHA256SUMS`: SHA-256 `5e4f24be2e5a3e5d3185cccb64bfdc8ff3814659c09cd44187d35921c15657bc`

Reference `prompts/assets/crab-phone-ui/network_http.h`: SHA-256 `bdb1aecbc7488b68d68748da56f53beb81b659c41b8175046b30c1358e8ad7b8`

Reference `prompts/assets/crab-phone-ui/ui.html`: SHA-256 `447d3b22498122862e1658617c97a778233b3d6bab04ffa8fc242c8a786945cf`

Reference `prompts/assets/robot-tank-cadsmith-v1/SHA256SUMS`: SHA-256 `fd36ec06531bd98559bd57699e7c4ae1f27d2d3465595212dc66fce67982622f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-53-33-PM.png`: SHA-256 `d324a2660e3081f5a89dd5be99491015ac7b980a243e6fe8732f97c7ee578199`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-54-41-PM.png`: SHA-256 `b29dbf3aaf5913d13fcc298cd43b70d6db0f5033632dd308f08cf127ab876b60`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-11-PM.png`: SHA-256 `8b83dc3d4efa4be511065ca42dd6e4b82a9055542731824dc392dfc95900281f`

Reference `prompts/assets/robot-tank-cadsmith-v1/Screenshot-2026-11-25-at-3-55-25-PM.png`: SHA-256 `a1ffd4756e4a5f066c85068d00c5381cb19f6ee922ae66f53dc2eb8d6714f2f3`

Reference `prompts/assets/robot-tank-cadsmith-v1/arm_front_left.step`: SHA-256 `b4dd773ca028ee345abd00851feb53026f53e84a3cdafe051fb5683e56458d24`

Reference `prompts/assets/robot-tank-cadsmith-v1/chassis.step`: SHA-256 `e6afd37a840523a3783d34da000b88e1229cc5095279c4e7815be06e532cddd3`

Reference `prompts/assets/robot-tank-cadsmith-v1/drawing.svg`: SHA-256 `7b1abe4cfb992d018b632e4d73547a2f7a0b8a9ff4c2bee61b31b661a27e8e3d`

Reference `prompts/assets/robot-tank-cadsmith-v1/firmware-chat-2026-11-25.md`: SHA-256 `7a095130f80f2379d2aac29e43f1d15d96e8b35275bb9deb3f12420dde6d5f48`

Reference `prompts/assets/robot-tank-cadsmith-v1/hull.step`: SHA-256 `3900b637ffd4bb657ede788ea70c96d86ba885747979970047afd5cc850e108a`

Reference `prompts/assets/robot-tank-cadsmith-v1/led_bracket.step`: SHA-256 `fe4e6526d0ae8038e4f87133edaf4b38cfdc89f511f7a915c33bc4e628cb7197`

Reference `prompts/assets/robot-tank-cadsmith-v1/lid.step`: SHA-256 `1915dffb799332f7871ce96f913d083839c2e8a479c60d0018ed125a1db3f07f`

Reference `prompts/assets/robot-tank-cadsmith-v1/model.py`: SHA-256 `0500d9de5b6c818b41381bce4887e64baa84474537012df9d71f80a20418808d`

Reference `prompts/assets/robot-tank-cadsmith-v1/report.json`: SHA-256 `6cd8df6d9dbc13c06e217fccea82c53eccb55df330fa69659488cb520edf00bc`

Reference `prompts/assets/robot-tank-cadsmith-v1/turret_head.step`: SHA-256 `14bda38c48e4c48fd481487016ef6267d05754bf07f060570ccfd8e8fa9aaf77`

Reference `prompts/assets/robot-tank-cadsmith-v1/wheel_front_left.step`: SHA-256 `136028340aedc346d6aaba9db250e0a106f3b080e0661ad1da7b39ddf9c76ae1`

Reference `prompts/assets/robot-tank-cadsmith-v5/SHA256SUMS`: SHA-256 `ceb49db77849f506f7f624d7fb3a964dfa9408fd54aba8b55d7443ed6d43a72a`

Reference `prompts/assets/robot-tank-cadsmith-v5/chassis.step`: SHA-256 `2a4a4b5caf1218b0e081c69a0029eb9e92772ba7e2c575f4c4942258a234a80d`

Reference `prompts/assets/robot-tank-cadsmith-v5/drawing.svg`: SHA-256 `1013f0e4ad81fcfe0f193cf9292237a79aac91b532d993338b8cb9961fea0c62`

Reference `prompts/assets/robot-tank-cadsmith-v5/esp32.step`: SHA-256 `1e1b9f199f40cbc8346660a554a7bc0eaa137e222aca020432c9b6ee995f3244`

Reference `prompts/assets/robot-tank-cadsmith-v5/hull.step`: SHA-256 `6cd01dacaef686c21fa5119986c43f2ef7c2d8db6df56c94675078a2e9e2b98b`

Reference `prompts/assets/robot-tank-cadsmith-v5/lid.step`: SHA-256 `42e1de372e21ac008d5d4864d65e8c505fab3bcb0d22fa97e83994ccea0661bc`

Reference `prompts/assets/robot-tank-cadsmith-v5/model.py`: SHA-256 `2f8277f217dca32d9de4f0a5969be4be22701be013b0ed25dd4aeed0fddfaa82`

Reference `prompts/assets/robot-tank-cadsmith-v5/pca9685.step`: SHA-256 `c7a31efb23078f31045ac60bcb6f43cec080d0de6c63ba09723f2450c657761a`

Reference `prompts/assets/robot-tank-cadsmith-v5/report.json`: SHA-256 `2b9d95d91e79ab07124b3fb8422dd0ac176abc664b2472b16a179c45c8182d7f`

Reference `prompts/assets/robot-tank-cadsmith-v5/screen_stack.step`: SHA-256 `3bd302e3582fc7ff37062fc814b23a46a110fa347e8bf0b757daec9bb1a80ce5`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_base.step`: SHA-256 `c37cb1ef41dbaafb1440761c2c29ea70caa9919c73edd964a4a1aba2f8b53d2f`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_tier_1.step`: SHA-256 `0803025ca855faae62f574628d7ec50ab7df0843253c977e27da3c1c53560c34`

Reference `prompts/assets/robot-tank-cadsmith-v5/stack_turret_mount.step`: SHA-256 `e1fc492f484defe7afd62458dbdb383addbd966ba883e65336ea455c86c70c54`

Reference `references/IMAGES.md`: SHA-256 `93ac22eae5f50c54d84e5cfb292685e2b9f264b463f168e92f0c7e9b6e35e13a`

Reference `references/user-images/2026-11-20-nose-current-blue-wedge.png`: SHA-256 `3e6fb7f8675dbccd279c4f0f587c979bc679aa9109a23354aa35a2dac6111138`

Reference `references/user-images/2026-11-20-nose-sketch-chevron.png`: SHA-256 `3dd263ef32e2df759c6248eae710d28eb17d3bf43e319b5f22e94ebe3d5af9f3`

Reference `references/user-images/2026-11-20-sonar-order-hc-sr04p.png`: SHA-256 `8ec21b7846ad1be930697c6f514a47bca21a0d6863aa7e20225c3b2e86860f7e`

Reference `references/user-images/2026-11-20-wheel-hub-tubes.png`: SHA-256 `0c43c2710a7927c0ef9f193761776d51d360caec376f4fd3313fa3bcb4ecd970`

Reference `references/user-images/2026-11-23-case-r002-overview.png`: SHA-256 `51a9b19c18624e05bb270d5c4eb581fde6e4f670dd6c3def6c6940f4a0f987d3`

Reference `references/user-images/2026-11-23-style-apc-references.png`: SHA-256 `9d9d217b434639f7bd6e7fc00f7203d76e19f5f4db738f34f07766e8d00bb201`
