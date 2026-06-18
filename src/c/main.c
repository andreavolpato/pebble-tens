#include <pebble.h>
#include "render.h"
#include "settings.h"

static Window *s_window;
static Layer *s_layer;

static void layer_update(Layer *layer, GContext *ctx) {
  time_t now = time(NULL);
  struct tm *t = localtime(&now);
  tens_render(ctx, layer_get_bounds(layer), t, tens_settings());
}

static void tick_handler(struct tm *tick_time, TimeUnits units_changed) {
  layer_mark_dirty(s_layer);
}

static void inbox_received(DictionaryIterator *iter, void *context) {
  if (tens_settings_apply(iter)) {
    layer_mark_dirty(s_layer);
  }
}

static void window_load(Window *window) {
  Layer *root = window_get_root_layer(window);
  s_layer = layer_create(layer_get_bounds(root));
  layer_set_update_proc(s_layer, layer_update);
  layer_add_child(root, s_layer);
}

static void window_unload(Window *window) { layer_destroy(s_layer); }

static void init(void) {
  tens_settings_init();

  s_window = window_create();
  window_set_window_handlers(s_window, (WindowHandlers){
                                           .load = window_load,
                                           .unload = window_unload,
                                       });
  window_stack_push(s_window, true);

  tick_timer_service_subscribe(MINUTE_UNIT, tick_handler);
  app_message_register_inbox_received(inbox_received);
  app_message_open(256, 64);
}

static void deinit(void) {
  tick_timer_service_unsubscribe();
  window_destroy(s_window);
}

int main(void) {
  init();
  app_event_loop();
  deinit();
}
