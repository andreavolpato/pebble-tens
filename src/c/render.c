#include "render.h"
#include "derived.h"
#include "layout.h"
#include "palette.h"

static int rect_right(GRect r) { return r.origin.x + r.size.w; }
static int rect_bottom(GRect r) { return r.origin.y + r.size.h; }

static int clampi(int v, int lo, int hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}

// Fill a rect with solid ink, or with the grid-wide spectral ramp (rainbow):
// each column samples the ramp at its position across the whole grid.
static void draw_ink_rect(GContext *ctx, GRect r, GRect grid, bool rainbow,
                          GColor ink) {
  if (r.size.w <= 0 || r.size.h <= 0) return;
  if (!rainbow) {
    graphics_context_set_fill_color(ctx, ink);
    graphics_fill_rect(ctx, r, 0, GCornerNone);
    return;
  }
  int span = grid.size.w - 1;
  if (span < 1) span = 1;
  for (int x = r.origin.x; x < rect_right(r); x++) {
    int t = (x - grid.origin.x) * 1000 / span;
    graphics_context_set_stroke_color(ctx, tens_spectral(t));
    graphics_draw_line(ctx, GPoint(x, r.origin.y), GPoint(x, rect_bottom(r) - 1));
  }
}

// The missing (unfilled) part of a bar/box: muted outline border or muted fill.
static void draw_missing(GContext *ctx, GRect bar, bool missing_fill,
                         GColor muted) {
  if (missing_fill) {
    graphics_context_set_fill_color(ctx, muted);
    graphics_fill_rect(ctx, bar, 0, GCornerNone);
  } else {
    graphics_context_set_stroke_color(ctx, muted);
    graphics_draw_rect(ctx, bar);
  }
}

// A solid color bar filled up to progress over a muted track.
static void fill_solid_bar(GContext *ctx, GRect bar, int progress, GColor color,
                           bool missing_fill, GColor muted) {
  draw_missing(ctx, bar, missing_fill, muted);
  progress = clampi(progress, 0, 1000);
  int fill_w = bar.size.w * progress / 1000;
  if (fill_w > 0) {
    graphics_context_set_fill_color(ctx, color);
    graphics_fill_rect(ctx, GRect(bar.origin.x, bar.origin.y, fill_w, bar.size.h),
                       0, GCornerNone);
  }
}

// Life bar in rainbow mode: one continuous spectral ramp revealed up to progress.
static void fill_gradient_bar(GContext *ctx, GRect bar, int progress,
                              bool missing_fill, GColor muted) {
  draw_missing(ctx, bar, missing_fill, muted);
  progress = clampi(progress, 0, 1000);
  int fill_w = bar.size.w * progress / 1000;
  int span = bar.size.w - 1;
  if (span < 1) span = 1;
  for (int dx = 0; dx < fill_w; dx++) {
    int t = dx * 1000 / span;
    graphics_context_set_stroke_color(ctx, tens_spectral(t));
    int x = bar.origin.x + dx;
    graphics_draw_line(ctx, GPoint(x, bar.origin.y), GPoint(x, rect_bottom(bar) - 1));
  }
}

static void render_grid(GContext *ctx, const TensLayout *L,
                        const TensDerived *d, const TensSettings *cfg,
                        GColor ink, GColor muted) {
  GRect grid = tens_day_rect(L);
  for (int i = 0; i < 144; i++) {
    GRect cell = tens_ten_minute_cell(L, i);
    if (i < d->ten_minute_index) {
      draw_ink_rect(ctx, cell, grid, cfg->rainbow, ink);
    } else if (i == d->ten_minute_index) {
      // Current box: muted missing part, then the completed-minute lines.
      draw_missing(ctx, cell, cfg->missing_fill, muted);
      // Minute lines fill along the cell's long axis (same as the boxes).
      int count = d->minute_of_box;
      GRect fill;
      if (L->cell_x == 3) {
        int cols = clampi(count, 0, cell.size.w);
        int x = cfg->fill_invert ? (rect_right(cell) - cols) : cell.origin.x;
        fill = GRect(x, cell.origin.y, cols, cell.size.h);
      } else {
        int rows = clampi(count, 0, cell.size.h);
        int y = cfg->fill_invert ? (rect_bottom(cell) - rows) : cell.origin.y;
        fill = GRect(cell.origin.x, y, cell.size.w, rows);
      }
      draw_ink_rect(ctx, fill, grid, cfg->rainbow, ink);
    } else {
      // Future box: a centered 4x4 muted dot placeholder.
      int d4 = 4;
      int ox = cell.origin.x + (cell.size.w - d4) / 2;
      int oy = cell.origin.y + (cell.size.h - d4) / 2;
      graphics_context_set_fill_color(ctx, muted);
      graphics_fill_rect(ctx, GRect(ox, oy, d4, d4), 0, GCornerNone);
    }
  }
}

void tens_render(GContext *ctx, GRect bounds, const struct tm *now,
                 const TensSettings *cfg) {
  bool dm = cfg->dark_mode;
  GColor bg = dm ? GColorBlack : GColorWhite;
  GColor ink = dm ? GColorWhite : GColorBlack;
  // Subtle gray (low-contrast): placeholders and unfilled tracks/outlines.
  // Dark gray on black, light gray on white.
  GColor muted = dm ? GColorDarkGray : GColorLightGray;
  // Contrasty gray: the month/year bars in rainbow mode. Light on black,
  // dark on white.
  GColor gray = dm ? GColorLightGray : GColorDarkGray;

  graphics_context_set_fill_color(ctx, bg);
  graphics_fill_rect(ctx, bounds, 0, GCornerNone);

  TensDerived d;
  tens_derive(now, cfg, &d);

  TensLayout L;
  tens_layout_init(&L, cfg->layout_4x6, cfg->hours_horizontal);

  render_grid(ctx, &L, &d, cfg, ink, muted);

  // Two bars: top half month | year, plus the long life bar. In rainbow mode
  // month/year are the contrasty gray; otherwise their fixed colors. Life
  // mirrors the boxes: spectral when rainbow, solid ink otherwise.
  GColor month_color = cfg->rainbow ? gray : TENS_COLOR_MONTH;
  GColor year_color = cfg->rainbow ? gray : TENS_COLOR_YEAR;
  fill_solid_bar(ctx, tens_month_bar(&L), d.frac_month, month_color,
                 cfg->missing_fill, muted);
  fill_solid_bar(ctx, tens_year_bar(&L), d.frac_year, year_color,
                 cfg->missing_fill, muted);

  GRect life = tens_life_bar(&L);
  if (cfg->rainbow) {
    fill_gradient_bar(ctx, life, d.frac_life, cfg->missing_fill, muted);
  } else {
    fill_solid_bar(ctx, life, d.frac_life, ink, cfg->missing_fill, muted);
  }
}
