// Derived values computed from the clock + settings, mirroring
// python/src/tens/derived.py. Fractions are in permille (0..1000) to avoid
// floating point.
#pragma once
#include <pebble.h>
#include "settings.h"

typedef struct {
  int ten_minute_index;  // 0..143 (current ten-minute box)
  int minute_of_box;     // 0..9 (completed minutes inside the current box)
  int frac_week;         // permille through the week (Mon -> Sun)
  int frac_month;        // permille through the month
  int frac_year;         // permille through the year (Jan 1 -> Dec 31)
  int frac_life;         // permille through the configured lifespan (clamped)
} TensDerived;

void tens_derive(const struct tm *now, const TensSettings *cfg, TensDerived *out);
