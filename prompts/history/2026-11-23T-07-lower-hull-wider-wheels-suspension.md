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
