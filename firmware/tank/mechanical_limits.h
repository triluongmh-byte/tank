#pragma once
// Imported from case/firmware-limits.json (status passed, contract a3ef67fc…, yaw -70..+70 about +Z, 0 = nose).
// reconcile.py checks this file against that hash-bound case file. Re-import and rebuild if the case changes it.
namespace tank { constexpr int CASE_YAW_MIN=-70, CASE_YAW_MAX=70; }
