// Draws the whole Tens scene into a layer's GContext, mirroring
// python/src/tens/scene.py build_scene().
#pragma once
#include <pebble.h>
#include "settings.h"

void tens_render(GContext *ctx, GRect bounds, const struct tm *now,
                 const TensSettings *cfg);
