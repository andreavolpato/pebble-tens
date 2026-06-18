#include "settings.h"
#include <string.h>

#define SETTINGS_PERSIST_KEY 1

static TensSettings s_settings;

static void set_defaults(void) {
  s_settings = (TensSettings){
      .rainbow = false,
      .dark_mode = false,
      .layout_4x6 = false,  // "6x4" = 6 columns x 4 rows
      .hours_horizontal = true,
      .fill_invert = false,
      .missing_fill = false,
      .birth_year = 1990,
      .birth_month = 4,
      .birth_day = 12,
      .life_span_years = 80,
  };
}

const TensSettings *tens_settings(void) { return &s_settings; }

void tens_settings_init(void) {
  set_defaults();
  if (persist_exists(SETTINGS_PERSIST_KEY)) {
    persist_read_data(SETTINGS_PERSIST_KEY, &s_settings, sizeof(s_settings));
  }
}

// Read a boolean tuple keyed by `key`; pkjs sends 1/0 as an int.
static bool read_bool(DictionaryIterator *iter, uint32_t key, bool current) {
  Tuple *t = dict_find(iter, key);
  return t ? (t->value->int32 != 0) : current;
}

static int read_int(DictionaryIterator *iter, uint32_t key, int current) {
  Tuple *t = dict_find(iter, key);
  return t ? (int)t->value->int32 : current;
}

bool tens_settings_apply(DictionaryIterator *iter) {
  TensSettings prev = s_settings;
  s_settings.rainbow = read_bool(iter, MESSAGE_KEY_RAINBOW, s_settings.rainbow);
  s_settings.dark_mode =
      read_bool(iter, MESSAGE_KEY_DARK_MODE, s_settings.dark_mode);
  s_settings.layout_4x6 =
      read_bool(iter, MESSAGE_KEY_LAYOUT_4X6, s_settings.layout_4x6);
  s_settings.hours_horizontal =
      read_bool(iter, MESSAGE_KEY_HOURS_HORIZONTAL, s_settings.hours_horizontal);
  s_settings.fill_invert =
      read_bool(iter, MESSAGE_KEY_FILL_INVERT, s_settings.fill_invert);
  s_settings.missing_fill =
      read_bool(iter, MESSAGE_KEY_MISSING_STYLE, s_settings.missing_fill);
  s_settings.birth_year =
      read_int(iter, MESSAGE_KEY_BIRTH_YEAR, s_settings.birth_year);
  s_settings.birth_month =
      read_int(iter, MESSAGE_KEY_BIRTH_MONTH, s_settings.birth_month);
  s_settings.birth_day =
      read_int(iter, MESSAGE_KEY_BIRTH_DAY, s_settings.birth_day);
  s_settings.life_span_years =
      read_int(iter, MESSAGE_KEY_LIFE_SPAN_YEARS, s_settings.life_span_years);
  if (s_settings.life_span_years <= 0) s_settings.life_span_years = 80;

  persist_write_data(SETTINGS_PERSIST_KEY, &s_settings, sizeof(s_settings));
  return memcmp(&prev, &s_settings, sizeof(s_settings)) != 0;
}
