#include <pebble.h>
static Window *window; static Layer *layer; static unsigned page; static bool alternate;
static const char *keys[]={FONT_KEY_GOTHIC_14,FONT_KEY_GOTHIC_14_BOLD,FONT_KEY_GOTHIC_18,FONT_KEY_GOTHIC_18_BOLD,FONT_KEY_GOTHIC_24,FONT_KEY_GOTHIC_24_BOLD,FONT_KEY_GOTHIC_28_BOLD};
static void draw(Layer *l,GContext *c){GRect b=layer_get_bounds(l);graphics_context_set_fill_color(c,GColorBlack);graphics_fill_rect(c,b,0,GCornerNone);graphics_context_set_text_color(c,GColorWhite);graphics_draw_text(c,keys[page],fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(0,0,b.size.w,20),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);graphics_draw_text(c,alternate?"Õõ Ää Öö Üü\nĎď Ťť Ňň":"Ĺĺ Ľľ Ŕŕ\nČč Ćć Đđ\nŠš Žž Ôô",fonts_get_system_font(keys[page]),GRect(16,19,b.size.w-32,b.size.h-19),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);}
static void next(ClickRecognizerRef r,void *ctx){(void)r;(void)ctx;page=(page+1)%7;layer_mark_dirty(layer);}
static void flip(ClickRecognizerRef r,void *ctx){(void)r;(void)ctx;alternate=!alternate;layer_mark_dirty(layer);}
static void clicks(void *ctx){(void)ctx;window_single_click_subscribe(BUTTON_ID_DOWN,next);window_single_click_subscribe(BUTTON_ID_SELECT,flip);}
int main(void){window=window_create();window_set_click_config_provider(window,clicks);Layer *root=window_get_root_layer(window);layer=layer_create(layer_get_bounds(root));layer_set_update_proc(layer,draw);layer_add_child(root,layer);window_stack_push(window,true);app_event_loop();layer_destroy(layer);window_destroy(window);}
