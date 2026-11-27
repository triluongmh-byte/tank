# Serial (DevKit USB-UART) protocol — tank-v1

115200 baud setting, printable ASCII lines ending LF or CRLF, no binary packets. Bounded 64-byte consumption per loop; framing rejects embedded controls, overflow and truncated motion commands. Replies are LF lines. A line accepted for a bounded motion request is not proof of physical motion. Controller state progression: OFF → power wait → neutral/center wait with new sonar → RUN → NEUTRAL → OFF; errors cut power directly.

Visual/status input retained from the named reference:

| Input | Meaning / reply |
|---|---|
| `idle`, `ask`, `thinking`, `processing`, `accepted`, `cancelled` | Pet state; ask/cancelled stop motion |
| `ping` | `PONG tank v1 pet` |
| `layout` | 240x240 dimensions, SPI bus and ticker format |
| `TITLE <UTF-8 bytes as hex>` | ≤160 decoded bytes; `ACK title` |
| `ACTION <UTF-8 bytes as hex>` | ≤96 decoded bytes; `ACK action` |
| `PROVIDER claude` / `codex` | `ACK provider` |
| `USAGE p0 seconds0 p1 seconds1`, `USAGE_AGE seconds` | Reference usage data |
| `HOST seconds-since-midnight wifi battery charging` | Reference host status, `ACK host` |
| `LIST generation count total`, `ROW generation index I-or-A-or-T-or-P id titlehex [replyhex]`, `END generation` | Transactional snapshot up to 12 sessions; `ACK list generation` |
| `tasks` | `TASK id state index/count` |
| `SESSIONS count`, `CELEBRATE <16 lowercase hex ID>` | Activity/celebration; existing ACK names |
| `MOOD generic/read/edit/test` | `ACK mood` |
| `POWER sleep/awake` | `ACK power`; sleep stops motion, wake does not arm |

Motor and tank inputs:

| Input | Meaning |
|---|---|
| `MOTOR CAPS` | `MOTOR CAPS tank-v1 channels=7 heartbeat=200ms calibration=required sonar=required hw=untested MAC=<actual efuse MAC>` |
| `MOTOR STATUS` | `MOTOR OFF/RUN/FAULT mode=<enum> armed=0/1 yaw=<deg> reason=<token>` |
| `MOTOR STOP`, `AUTO OFF` | Immediate OE HIGH and ACT_EN LOW; `ACK MOTOR STOP` |
| `MOTOR ARM` | Reinitialize PCA with outputs/rail inhibited; never moves; `ACK MOTOR ARM` |
| `MOTOR HEARTBEAT` | Refresh control lease; `ACK MOTOR HEARTBEAT`; does not arm/start/extend command duration |
| `MOTOR DRIVE FWD/BACK` | All six wheels in physical forward/reverse for 2000ms target duration |
| `MOTOR CUE WORK/DONE/LEFT/RIGHT/FWD/BACK` | WORK reverse 1050ms, DONE forward 1350ms, remaining 540ms; LEFT/RIGHT pivot conservatively requires both sonars |
| `MOTOR TEST <0..5 or L/R> <+/-/0> [2000ms]` | One wheel, 100ms default; L=LF/0, R=RF/3. Others full-off, no sonar guard for lifted-wheel calibration |
| `CAL GET`, `CAL SET i neutral_us direction span_us`, `CAL TURRET center_us us_per_degree`, `CAL SAVE` | Read/set/persist calibration while stopped; changes disarm |
| `TURRET <signed degrees>` | Only checked case interval; stops any prior wheel command, requires fresh ARM if switching active source |
| `AUTO ON` | Straight advance at 25% calibrated span, ≤9000ms, stop/power-cut on blocked/unknown/stale forward data |
| `AUTO SCAN` | Stationary left–center–right–center scan; disabled without checked case range |
| `SONAR STATUS` | `SONAR F=<mm>,<fresh-valid>,<yaw> R=<mm>,<fresh-valid>,<yaw> yaw=<current>`; valid echo is not a drive authorization by itself |

CUE and DRIVE ACKs keep the reference form, e.g. `ACK MOTOR CUE WORK 1050ms`, `ACK MOTOR DRIVE FWD 2000ms`. TEST ACK includes channel/direction/duration. Rejected movement returns `ERR MOTOR <reason>`; malformed motion framing/grammar cuts power and disarms. A syntactically valid competing request returns busy, preserves the current source and never starts another. To switch deliberately, STOP → ARM → command. Every stop clears arming; heartbeats alone never restart.

Heartbeat target is 200ms; ≥750ms silence cuts power even if USB remains connected and display traffic continues. Fixed command duration and max lease cannot be prolonged by heartbeat. `MOTOR STATUS`, `ping`, TITLE and other display messages do not refresh the control lease. A separate 100ms loop deadline/5ms polling timer cuts power if the loop stalls; task watchdog resets after 2s. These are engineering targets needing bench verification.

A disconnected/reconnected host must discard old parser fragments, verify the new identity and OFF status, then explicitly authorize ARM. `host/tank_transport.py` implements this bridge interface without opening devices. Do not copy the old MAC, cues-v3 receipt or GPIO20/21 assumptions. No verification receipt is supplied because no target has been flashed/observed.
