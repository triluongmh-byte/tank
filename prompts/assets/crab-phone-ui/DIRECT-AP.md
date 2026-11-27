> Note14 adds [continuous360° calibration and short jogs](CONTINUOUS360.md).
> Direct AP and manual navigation remain unchanged. In default continuous mode,
> drive arrows are disabled; light and all pages remain usable. No walking is claimed.

# Direct phone connection (release note 10)

The physical target the owner has is the original LILYGO T-Display-S3 with a
PCA9685 module. The integrated PCB has a separate build; it is unmanufactured
and is not authorized for flashing. Both targets contain this AP fix.

Join the open **CuaRobot-XXXX** network from QR #1. Keep the connection when the
phone says it has no internet, then open **http://192.168.4.1/**. Captive portal
probes serve the same control page. Home Wi-Fi is optional. The control page,
light and assembly page work without a station connection; status polls never
navigate. The product interface remains Vietnamese.

To configure home Wi-Fi, explicitly press **Wi-Fi**, scan, select a 2.4 GHz
network and enter its password. Wrong passwords and the 18-second timeout show
Vietnamese errors on the display and current page. They do not change pages or
save the failed credentials. Successful setup stores credentials privately in
NVS and displays QR #2 with the station web address. Credentials are never
returned in status or logged. Holding BOOT for 8 seconds while firmware runs
erases Wi-Fi credentials only. The AP remains available.

Saved networks are joined automatically on boot. Background retries run about
every 30 seconds only while no AP client is attached. An AP client arriving
cancels an unfinished background attempt. Manual scan/setup can preempt it.
The AP is never deliberately restarted by retry handling. The ESP32-S3 shares
one radio between AP and station: an attempt already underway before the phone
joins, manual scanning/joining, or an upstream channel change may interrupt the
link. Host tests cannot prove radio continuity; actual phone/range/channel
behaviour is unverified. Release and reconnect before pressing again after any
interruption. The independent 500 ms command lease still stops stale motion;
station loss alone no longer stops a valid AP control session. Hold/release,
session ordering and the persistent assembly lock are unchanged.

## Default-off actuator policy and separate experiment (notes 11–13)

The direct-AP fix was accepted at r016; note13 authorizes this separate source
change. Both new binaries default to continuous/unknown actuators and keep all
16 PCA outputs fully off. There is no sequential enable, standing pulse, gait or
raw-centre in that default state. Light, control-page navigation, assembly-page
navigation, QR and web work without a station connection or responding PCA.
Explicitly selecting verified 180-degree positional servos enables the unchanged
positional startup, gait and trim logic. That choice is RAM-only and reverts to
unknown at reboot; do not select it for the owner's continuous/unknown units.

The manually opened **Thử 1 servo** page is an experiment, not walking or angle
holding. It exclusively drives one unloaded CH0–7 with count-based pulses,
500 ms dead-man and a hard 2-second hold limit, then full PWM off. Release,
page/session changes, BOOT and inhibit stop it. Other channels stay hard off.
See [servo-test instructions and limits](SERVO-TEST.md). No servo classification
or test settings are stored; the owner observes and records each unit's type.

The owner's current parts include **no servo supply of established rating**.
Any physical servo test needs a supply decision first. The exposed 18650 and
unidentified module are neither recommended nor wired as a supply. Continuous
servos cannot hold angles: timed pulses add no feedback, neutral is not position
holding, and different clones may react differently to PWM off. Servo type,
health and neutral stability remain unknown. No purchases or motor operation.

The original LILYGO is the flash candidate only after independent review and
entry's identity/isolation/verified-backup/recovery prerequisites. The integrated
binary remains build-only. See [entry flash handoff](FLASH-CANDIDATE.md).

Build: `python3 tools/firmware/build.py --target all` from the project root.
Host checks: `python3 tools/firmware/check.py`; focused AP checks:
`python3 tools/firmware/check.py web http core`. Wiring and both hardware pin
profiles are unchanged. See [Vietnamese firmware guide](README.md) and
[handoff](HANDOFF.md). The entry agent owns top-level English publication.
