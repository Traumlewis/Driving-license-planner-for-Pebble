#include <pebble.h>
#include "app.h"
#include "rules.h"
#include "topics.h"
#include "i18n.h"

// Device-local safe canvas. Round corners are outside the inscribed content square.
#if defined(PBL_PLATFORM_GABBRO)
#define UI_WIDTH 184
#define UI_HEIGHT 184
#define UI_LEFT 38
#define UI_TOP 38
#else
#define UI_WIDTH 144
#define UI_HEIGHT 168
#define UI_LEFT 0
#define UI_TOP 0
#undef GColorOxfordBlue
#undef GColorCyan
#undef GColorMelon
#define GColorOxfordBlue GColorBlack
#define GColorCyan GColorWhite
#define GColorMelon GColorWhite
#endif
#if defined(PBL_PLATFORM_FLINT)
#define UI_SELECTION GColorBlack
#define UI_SELECTION_TEXT GColorWhite
#else
#define UI_SELECTION GColorCyan
#define UI_SELECTION_TEXT GColorOxfordBlue
#endif
#define UI_INFO_HEADER 44

#define WAKE_COOKIE 321
#define TEST_COOKIE 909
static const char *const kinds[]={LK_Praxis_Ubungsfahrt_63e3fd80,LK_Praxis_Landstrasse_d030c0ca,LK_Praxis_Autobahn_028a72c7,LK_Praxis_Nachtfahrt_c290aa14,LK_Praxis_Grundausbildung_5a10f7a2,LK_Theorie_Grundstoff_4502013b,LK_Theorie_Zusatzstoff_8f17cabd};
static const char *const counters[]={LK_Landstrasse_LA_d9046e5d,LK_Autobahn_AU_d31b4ca6,LK_Nachtfahrt_NA_b6610768,LK_Grundausbildung_GA_420dab61,LK_Grundstoff_GS_81ee2446,LK_Zusatzstoff_ZS_ec7bd61a};
typedef enum {HOME,LIST,CLASSES,PROFILES,EDIT,KINDS,PROGRESS,ACTIONS,DELETE_CONFIRM,COMPLETE_CONFIRM,TOPICS,TOPIC_PICK,ALERT,PENDING,PROGRESS_ACTIONS,PROGRESS_RESET,SETTINGS,EXPLANATIONS} Page;
static int progress_counter;
static Page page;
#define NAVIGATION_LIMIT 12
typedef struct {Page page;uint16_t row;GPoint offset;uint32_t item_id,context_id;} MenuView;
static MenuView navigation[NAVIGATION_LIMIT];
static int navigation_depth;
static AppTimer *progress_hold_timer;
static bool progress_hold_fired;
static int progress_touch_row;
static Window *window,*msg_window,*num_window;
static Window *status_window;
static Layer *status_layer,*footer_layer,*info_header;
static char info_title[64];
static int info_symbol;
static bool language_setup_notice;
static AppTimer *status_timer;
static char status_title[96],status_detail[96];
static MenuLayer *menu;
static TextLayer *msg_text;
static ScrollLayer *msg_scroll;
static Layer *num_layer,*date_layer;
static Window *date_window;
static struct tm date_value;
static int date_mode,date_field;
static GBitmap *class_icons[16];
static Rule rules[10];
static int rule_count,selected=-1,list_map[MAX_ENTRIES],list_count;
static uint32_t edit_id;
static Entry draft;
static struct tm draft_tm;
static bool ui_ready,processing;
bool alarm_ok=true;
static WakeupId wake_id=-1;
static int32_t test_at;
static int number_field,number_value,number_min,number_max;
static char number_title[80];
#if defined(PBL_PLATFORM_FLINT)
static char msg_buf[1024];
#else
static char msg_buf[2048];
#endif
static int alert_queue[MAX_ENTRIES],alert_count,completion_queue[MAX_ENTRIES],completion_count;
static bool alert_seen[MAX_ENTRIES],completion_seen[MAX_ENTRIES];
static void refresh(void);
static void show_page(Page p);
static void process_events(bool show);
static void schedule_next(void);
static void edit_datetime(int mode);
static void date_draw(Layer *l,GContext *ctx);
static void date_clicks(void *ctx);
static void touch_handler(const TouchEvent *event,void *context);
static void touch_controls(GContext *ctx,bool next);
static uint16_t rows(MenuLayer *m,uint16_t section,void *ctx);
static int16_t header_height(MenuLayer *m,uint16_t section,void *ctx);
static int16_t row_height(MenuLayer *m,MenuIndex *i,void *ctx);
static void select_row(MenuLayer *m,MenuIndex *i,void *ctx);
static void back(ClickRecognizerRef r,void *ctx);
static void start_progress_touch(int y);
static void cancel_progress_touch(void);
static void move_menu(bool up);
static void footer_draw(Layer *layer,GContext *ctx);
static void load_rules(void) {rule_count=rules_for(cfg.cls,rules);if(cfg.profile<0||cfg.profile>=rule_count)cfg.profile=0;}
static const uint16_t *targets(void) {return rules[cfg.profile].target;}

static bool draft_uses_minutes(void){
 if(draft.kind==0||draft.kind>=5)return false;
 if(draft.cls==cfg.cls)return targets()[kind_counter(draft.kind)]>0;
 Rule available[10];int n=rules_for(draft.cls,available),profile=profiles[draft.cls];
 if(profile<0||profile>=n)profile=0;
 return n>0&&available[profile].target[kind_counter(draft.kind)]>0;
}
static bool progress_has_minutes(int counter){return counter>=0&&counter<4&&targets()[counter]>0;}
static bool progress_can_hold(int counter){return counter==4||counter==5||progress_has_minutes(counter);}
int profile_extra(int c){Rule r[10];int n=rules_for(c,r);return r[profiles[c]<n?profiles[c]:0].target[5];}
static bool selected_valid(void) {return selected>=0&&selected<MAX_ENTRIES&&entries[selected].active;}
static int active_count(void) {int n=0;for(int i=0;i<MAX_ENTRIES;i++)n+=entries[i].active?1:0;return n;}
static int pending_count(void) {int n=0;for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active&&end_time(&entries[i])<=time(NULL))n++;return n;}
static int next_entry(void) {
 int result=-1;int32_t now=time(NULL);
 for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active&&end_time(&entries[i])>now&&(result<0||entries[i].when<entries[result].when))result=i;
 return result;
}
static void build_list(void) {
 list_count=0;
 for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active&&(page!=PENDING||end_time(&entries[i])<=time(NULL)))list_map[list_count++]=i;
 for(int i=1;i<list_count;i++){int value=list_map[i],j=i-1;while(j>=0&&entries[list_map[j]].when>entries[value].when){list_map[j+1]=list_map[j];j--;}list_map[j+1]=value;}
}
static void date_text(time_t when,char *buf,size_t n) {struct tm *t=localtime(&when);strftime(buf,n,T("%d.%m.%Y %H:%M"),t);}
static void lead_text(int lead,char *buf,size_t n) {if(lead)snprintf(buf,n,T(LK_02d_02d_vorher_ff4a8bfd),lead/60,lead%60);else snprintf(buf,n,T(LK_Aus_6997e3eb));}
static void dismiss_status(void){if(status_timer){app_timer_cancel(status_timer);status_timer=NULL;}if(status_window&&window_stack_contains_window(status_window))window_stack_remove(status_window,false);}
static void status_timeout(void *context){(void)context;status_timer=NULL;if(window_stack_contains_window(status_window))window_stack_remove(status_window,false);}
static void status_draw(Layer *layer,GContext *ctx){

 (void)layer;graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,UI_HEIGHT),0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);
 graphics_draw_text(ctx,status_detail,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(6,1,UI_WIDTH-12,32),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);
 int x=UI_WIDTH/2;graphics_context_set_fill_color(ctx,GColorCyan);graphics_fill_circle(ctx,GPoint(x,63),18);graphics_context_set_stroke_color(ctx,GColorOxfordBlue);graphics_context_set_stroke_width(ctx,3);graphics_draw_line(ctx,GPoint(x-10,63),GPoint(x-2,71));graphics_draw_line(ctx,GPoint(x-2,71),GPoint(x+11,55));
 graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,status_title,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(6,88,UI_WIDTH-12,52),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);
 graphics_draw_text(ctx,T(LK_Schliesst_nach_2_Sekunden_6a25d987),fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,UI_HEIGHT-23,UI_WIDTH-8,22),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
}
void show_status(const char *title,const char *detail){
 if(!ui_ready)return;
 if(status_timer)app_timer_cancel(status_timer);
 snprintf(status_title,sizeof(status_title),"%s",T(title));snprintf(status_detail,sizeof(status_detail),"%s",T(detail));
 layer_mark_dirty(status_layer);if(!window_stack_contains_window(status_window))window_stack_push(status_window,false);
 status_timer=app_timer_register(2000,status_timeout,NULL);
}
static void layout_message(void){

 text_layer_set_size(msg_text,GSize(UI_WIDTH-16,4096));GSize size=text_layer_get_content_size(msg_text);text_layer_set_size(msg_text,GSize(UI_WIDTH-16,size.h+16));scroll_layer_set_content_size(msg_scroll,GSize(UI_WIDTH,size.h+28));scroll_layer_set_content_offset(msg_scroll,GPointZero,false);
}

static void show_notice(const char *title,int symbol,const char *body){
 if(!ui_ready)return;
 dismiss_status();
 snprintf(info_title,sizeof(info_title),"%s",T(title));info_symbol=symbol;
 snprintf(msg_buf,sizeof(msg_buf),"%s",T(body));
 window_set_background_color(msg_window,GColorWhite);text_layer_set_text_color(msg_text,GColorOxfordBlue);
 text_layer_set_font(msg_text,fonts_get_system_font(UI_WIDTH<160?FONT_KEY_GOTHIC_18:FONT_KEY_GOTHIC_24));text_layer_set_text(msg_text,msg_buf);layout_message();
 scroll_layer_set_frame(msg_scroll,GRect(UI_LEFT,UI_TOP+UI_INFO_HEADER,UI_WIDTH,UI_HEIGHT-UI_INFO_HEADER));layer_set_bounds(scroll_layer_get_layer(msg_scroll),GRect(0,0,UI_WIDTH,UI_HEIGHT-UI_INFO_HEADER));
 layer_set_hidden(info_header,false);layer_mark_dirty(info_header);
 if(!window_stack_contains_window(msg_window))window_stack_push(msg_window,true);
}
void show_message(const char *text){show_notice(T(LK_Hinweis_ad6c499c),1,text);}
static void info_header_draw(Layer *layer,GContext *ctx){

 (void)layer;graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,UI_INFO_HEADER),0,GCornerNone);graphics_context_set_stroke_color(ctx,GColorCyan);graphics_context_set_fill_color(ctx,GColorCyan);graphics_context_set_stroke_width(ctx,2);
 if(info_symbol==4){graphics_draw_line(ctx,GPoint(13,10),GPoint(22,30));graphics_draw_line(ctx,GPoint(22,30),GPoint(4,30));graphics_draw_line(ctx,GPoint(4,30),GPoint(13,10));graphics_draw_line(ctx,GPoint(13,17),GPoint(13,23));graphics_fill_circle(ctx,GPoint(13,27),1);}
 else if(info_symbol==2){graphics_draw_round_rect(ctx,GRect(7,9,12,23),2);graphics_draw_line(ctx,GPoint(10,28),GPoint(16,28));}
 else if(info_symbol==0||info_symbol==6){graphics_draw_rect(ctx,GRect(5,12,16,20));for(int y=17;y<29;y+=5)graphics_draw_line(ctx,GPoint(9,y),GPoint(18,y));}
 else if(info_symbol==5){for(int i=0;i<3;i++)graphics_fill_rect(ctx,GRect(5+i*6,24-i*6,4,8+i*6),0,GCornerNone);}
 else {graphics_draw_circle(ctx,GPoint(13,21),9);graphics_draw_line(ctx,GPoint(13,19),GPoint(13,27));graphics_fill_circle(ctx,GPoint(13,15),1);}
 GFont font=fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD);GSize size=graphics_text_layout_get_content_size(info_title,font,GRect(0,0,UI_WIDTH-52,80),GTextOverflowModeWordWrap,GTextAlignmentCenter);int y=(UI_INFO_HEADER-size.h)/2-5;
 graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,info_title,font,GRect(26,y,UI_WIDTH-52,UI_INFO_HEADER-y),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);graphics_draw_line(ctx,GPoint(0,UI_INFO_HEADER-2),GPoint(UI_WIDTH,UI_INFO_HEADER-2));
}
static void show_info(const char *title,int symbol,const char *body){
 const char *text=T(body),*start=strstr(text,"\n\n");if(start)text=start+2;
 show_notice(title,symbol,text);
}
static void buzz(void) {static const uint32_t pattern[]={500,180,500,180,900};vibes_enqueue_custom_pattern((VibePattern){.durations=pattern,.num_segments=5});light_enable_interaction();}
static void refresh(void){

 if(!ui_ready){return;}menu_layer_set_highlight_colors(menu,UI_SELECTION,UI_SELECTION_TEXT);int h=UI_HEIGHT-(page==TOPICS?20:0);scroll_layer_set_frame(menu_layer_get_scroll_layer(menu),GRect(UI_LEFT,UI_TOP,UI_WIDTH,h));layer_set_bounds(menu_layer_get_layer(menu),GRect(0,0,UI_WIDTH,h));layer_set_hidden(footer_layer,page!=TOPICS);build_list();menu_layer_reload_data(menu);layer_mark_dirty(menu_layer_get_layer(menu));
}
static MenuView capture_view(void){
 MenuView view={.page=page,.row=menu_layer_get_selected_index(menu).row,.offset=scroll_layer_get_content_offset(menu_layer_get_scroll_layer(menu)),.context_id=selected_valid()?entries[selected].id:0};
 int pos=page==LIST?(int)view.row-1:(int)view.row;
 if((page==LIST||page==PENDING)&&pos>=0&&pos<list_count)view.item_id=entries[list_map[pos]].id;
 return view;
}
static void set_page(Page p){page=p;refresh();menu_layer_set_selected_index(menu,MenuIndex(0,0),MenuRowAlignTop,false);scroll_layer_set_content_offset(menu_layer_get_scroll_layer(menu),GPointZero,false);}
static void reset_navigation(Page p){navigation_depth=0;set_page(p);}
static void show_page(Page p){
 if(p==page){refresh();return;}
 if(navigation_depth==NAVIGATION_LIMIT){memmove(navigation,navigation+1,sizeof(navigation[0])*(NAVIGATION_LIMIT-1));navigation_depth--;}
 navigation[navigation_depth++]=capture_view();set_page(p);
}
static void restore_view(MenuView view){
 page=view.page;selected=view.context_id?find_id(entries,view.context_id):-1;refresh();
 int count=rows(menu,0,NULL),row=view.row;
 if(view.item_id&&(page==LIST||page==PENDING))for(int i=0;i<list_count;i++)if(entries[list_map[i]].id==view.item_id){row=i+(page==LIST?1:0);break;}
 if(row>=count)row=count?count-1:0;
 menu_layer_set_selected_index(menu,MenuIndex(0,row),MenuRowAlignNone,false);
 ScrollLayer *scroll=menu_layer_get_scroll_layer(menu);int minimum=layer_get_bounds(scroll_layer_get_layer(scroll)).size.h-scroll_layer_get_content_size(scroll).h;
 if(minimum>0)minimum=0;
 if(view.offset.y>0)view.offset.y=0;
 if(view.offset.y<minimum)view.offset.y=minimum;
 view.offset.x=0;scroll_layer_set_content_offset(scroll,view.offset,false);
}
static void return_page(void){
 while(navigation_depth){MenuView view=navigation[--navigation_depth];if((view.page==ACTIONS||view.page==DELETE_CONFIRM||view.page==COMPLETE_CONFIRM)&&find_id(entries,view.context_id)<0)continue;
  restore_view(view);return;
 }
 reset_navigation(cfg.cls<0?CLASSES:HOME);
}
static void return_to(Page p){for(int i=navigation_depth-1;i>=0;i--)if(navigation[i].page==p){MenuView view=navigation[i];navigation_depth=i;restore_view(view);return;}reset_navigation(p);}
static void show_event_page(Page p){if(page==ALERT||page==COMPLETE_CONFIRM)set_page(p);else show_page(p);}

static void surface_alerts(void) {
 if(!ui_ready)return;
 if(alert_count||completion_count)dismiss_status();
 // Keep all simultaneously due lessons in the alert list; do not overwrite one another.
 if(alert_count){buzz();if(window_stack_contains_window(msg_window))window_stack_remove(msg_window,false);if(window_stack_contains_window(num_window))window_stack_remove(num_window,false);if(window_stack_contains_window(date_window))window_stack_remove(date_window,false);show_event_page(ALERT);return;}
 if(completion_count){buzz();if(window_stack_contains_window(msg_window))window_stack_remove(msg_window,false);if(window_stack_contains_window(num_window))window_stack_remove(num_window,false);if(window_stack_contains_window(date_window))window_stack_remove(date_window,false);show_event_page(COMPLETE_CONFIRM);selected=completion_queue[0];}
}
static void schedule_next(void) {
 int32_t next=queue_next(entries),now=time(NULL);
 if(test_at&&(!next||test_at<next))next=test_at;
 if(!next){if(wake_id>=0)wakeup_cancel(wake_id);wake_id=-1;persist_delete(WAKE_KEY);alarm_ok=!storage_error;return;}
 if(next<=now)next=now+1;
 time_t old_at=0;
 if(wake_id>=0&&wakeup_query(wake_id,&old_at)&&old_at==next){alarm_ok=!storage_error;return;}
 if(wake_id>=0)wakeup_cancel(wake_id);
 // A one-minute window is shared by all entries using one persistent queue wakeup.
 wake_id=wakeup_schedule(next,WAKE_COOKIE,true);
 alarm_ok=wake_id>=0&&!storage_error;
 if(wake_id>=0){if(persist_write_int(WAKE_KEY,wake_id)<0){storage_error=true;alarm_ok=false;}}
 else persist_delete(WAKE_KEY);
}
static void process_events(bool show) {
 if(processing)return;
 processing=true;
 int32_t now=time(NULL);bool changed=false,new_event=false;
 for(int i=0;i<MAX_ENTRIES;i++){
  Entry old=entries[i];int event=consume_due(&entries[i],now);
  if(memcmp(&old,&entries[i],sizeof(Entry))!=0){store_entry(i);changed=true;}
  if((event&1)&&!alert_seen[i]){new_event=true;alert_seen[i]=true;alert_queue[alert_count++]=i;}
  if((event&2)&&!completion_seen[i]){new_event=true;completion_seen[i]=true;completion_queue[completion_count++]=i;}
 }
 if(changed)store_revision();
 bool test_due=test_at&&test_at<=now;if(test_due){test_at=0;persist_delete(28);}
 schedule_next();processing=false;refresh();
 if(show&&new_event&&(alert_count||completion_count))surface_alerts();
 else if(show&&test_due){buzz();show_info(T(LK_Alarmtest_c4d250b1),3,T("ALARMTEST\n\nAutomatisch gestartet.\n\nSo erinnert dich die Uhr auch bei geschlossener App."));}
}
void state_changed(void) {
 if(ui_ready&&language_setup_notice&&language_pack_ready()){window_stack_remove(msg_window,false);language_setup_notice=false;}
 if(cfg.cls<0){for(int i=0;i<MAX_ENTRIES;i++)if(entries[i].active){cfg.cls=entries[i].cls;cfg.profile=profiles[cfg.cls];load_rules();store_config();break;}}

 // Preserve other simultaneous alerts and completion questions across one booking/edit.
 int out=0;memset(alert_seen,0,sizeof(alert_seen));
 for(int n=0;n<alert_count;n++){int i=alert_queue[n];if(entries[i].active){alert_queue[out++]=i;alert_seen[i]=true;}}alert_count=out;
 out=0;memset(completion_seen,0,sizeof(completion_seen));
 for(int n=0;n<completion_count;n++){int i=completion_queue[n];if(entries[i].active&&end_time(&entries[i])<=time(NULL)){completion_queue[out++]=i;completion_seen[i]=true;}}completion_count=out;
 process_events(false);
 if(ui_ready)reset_navigation(cfg.cls<0?CLASSES:HOME);
 phone_push(0,0,NULL);
}
static void wake_handler(WakeupId id,int32_t cookie) {(void)cookie;if(id==wake_id){wake_id=-1;persist_delete(WAKE_KEY);}process_events(true);}
static void begin_edit(int index) {
 edit_id=index>=0?entries[index].id:0;
 if(index>=0)draft=entries[index];else{
  if(free_slot(entries)<0){show_notice(T(LK_Terminliste_voll_56bbc00d),6,T(LK_Alle_24_Terminplatze_sind_belegt_Bitte_abgesc_6cdec1c7));return;}
  memset(&draft,0,sizeof(draft));draft=(Entry){.when=time(NULL)+90000,.lead={60,30},.units=1,.cls=cfg.cls,.topic=NO_TOPIC,.active=1,.kind=cfg.cls==14?5:0};
 }
 time_t t=draft.when;draft_tm=*localtime(&t);draft_tm.tm_sec=0;show_page(EDIT);
}
static bool save_draft(void) {
 time_t when;
 if(!valid_date(&draft_tm,&when)){show_notice(T(LK_Datum_prufen_bd0ee609),4,T("Ungültiges Datum oder Uhrzeit. Bitte prüfen; auch die Zeitumstellung kann eine Uhrzeit ungültig machen."));return false;}
 if(when<=time(NULL)){show_notice(T(LK_Datum_prufen_bd0ee609),4,T(LK_Der_Termin_muss_in_der_Zukunft_liegen_d29418af));return false;}
 if(draft.lead[1]&&draft.lead[0]==draft.lead[1]){show_notice(T(LK_Erinnerungen_prufen_86dde7cf),4,T(LK_Bitte_zwei_unterschiedliche_Erinnerungszeiten_17f19057));return false;}
 if(edit_id&&find_id(entries,edit_id)<0){show_notice(T(LK_Termin_fehlt_c5e0c2c3),6,T(LK_Der_Termin_wurde_inzwischen_geloscht_Bitte_ne_9660c4ed));return false;}
 int index=edit_id?find_id(entries,edit_id):free_slot(entries);if(index<0){show_notice(T(LK_Terminliste_voll_56bbc00d),6,T(LK_Alle_Terminplatze_sind_belegt_c29a2eea));return false;}
 draft.when=when;draft.snooze=0;draft.review=0;draft.flags=0;draft.token=0;
 if(!draft.id)draft.id=allocate_id();
 if(!entry_valid(&draft)||!draft.id){show_notice(T(LK_Speicherfehler_71eed920),4,T(LK_Termindaten_ungultig_oder_Speicherfehler_5a95d9d9));return false;}
 bool skipped=false;for(int k=0;k<2;k++)if(draft.lead[k]&&draft.when-(int32_t)draft.lead[k]*60<=time(NULL)){draft.flags|=1<<k;skipped=true;}
 Entry old=entries[index];entries[index]=draft;
 if(!store_entry(index)){entries[index]=old;show_notice(T(LK_Speicherfehler_71eed920),4,T(LK_Speicherfehler_Termin_nicht_gespeichert_Bitte_4a235b6b));return false;}
 store_revision();state_changed();
 if(!alarm_ok)show_notice(T(LK_Alarmstatus_b0ff7d4e),3,T("TERMIN GESPEICHERT\n\nAlarm konnte nicht aktiviert werden! Unter Einstellungen den Alarm erneut aktivieren."));else show_status(T(LK_Termin_gespeichert_8224dbe3),skipped?T(LK_Vorwarnung_ubersprungen_ad5f6505):T(LK_Terminplanung_a6229b03));return true;
}
static void apply_number(void) {
 switch(number_field){
 case 0:draft_tm.tm_year=number_value-1900;break;case 1:draft_tm.tm_mon=number_value-1;break;case 2:draft_tm.tm_mday=number_value;break;case 3:draft_tm.tm_hour=number_value;break;case 4:draft_tm.tm_min=number_value;break;
 case 5:draft.lead[0]=number_value*15;break;case 6:draft.lead[1]=number_value*15;break;case 7:if(draft_uses_minutes()){draft.units=number_value*5/45;draft.extra_minutes=number_value*5%45;}else{draft.units=number_value;draft.extra_minutes=0;}break;
 case 16:practice[cfg.cls].exercise_units=number_value;store_progress(cfg.cls);store_revision();break;
 case 17:if(progress_has_minutes(progress_counter))set_extra_minutes(cfg.cls,progress_counter,number_value*5);break;
 default:{int k=number_field-10;set_progress_count(cfg.cls,k,number_value+topic_units(cfg.cls,k));break;}
 }refresh();
}
static void num_draw(Layer *l,GContext *ctx){

 (void)l;static char value[30],hint[70];hint[0]=0;graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,UI_HEIGHT),0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);
 graphics_draw_text(ctx,T(number_title),fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(6,1,UI_WIDTH-12,40),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);
 if(number_field==5||number_field==6){if(number_value)snprintf(value,sizeof(value),T("%02d:%02d"),number_value/4,number_value%4*15);else snprintf(value,sizeof(value),T(LK_Aus_6997e3eb));}else snprintf(value,sizeof(value),T("%d"),((number_field==7&&draft_uses_minutes())||number_field==17)?number_value*5:number_value);
 graphics_context_set_text_color(ctx,GColorCyan);graphics_draw_text(ctx,value,fonts_get_system_font(FONT_KEY_BITHAM_30_BLACK),GRect(2,46,UI_WIDTH-4,43),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
 const char *unit=(number_field==5||number_field==6)?T(LK_Vorwarnzeit_14c6b73f):((number_field==7&&draft_uses_minutes())||number_field==17)?T(LK_Minuten_497af2bf):T(LK_Einheiten_fa8cfe70);graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,unit,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(4,88,UI_WIDTH-8,24),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
 if(number_field==14||number_field==15)snprintf(hint,sizeof(hint),T(LK_u_per_Hakchen_geschutzt_c30f9880),topic_units(cfg.cls,number_field-10));else if(number_field==17||(number_field==7&&draft_uses_minutes()))snprintf(hint,sizeof(hint),"%s",T(LK_45_Min_1_Einheit_040553e8));else if(number_field==7)snprintf(hint,sizeof(hint),"%s",T(draft.kind>=5?LK_90_Min_1_Einheit_76e05804:LK_45_Min_1_Einheit_040553e8));
 graphics_draw_text(ctx,hint,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,110,UI_WIDTH-8,28),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);touch_controls(ctx,false);
}
static void num_up(ClickRecognizerRef r,void *c){(void)r;(void)c;if(++number_value>number_max)number_value=number_field>=14?number_max:number_min;layer_mark_dirty(num_layer);}
static void num_down(ClickRecognizerRef r,void *c){(void)r;(void)c;if(--number_value<number_min)number_value=number_field>=14?number_min:number_max;layer_mark_dirty(num_layer);}
static void num_select(ClickRecognizerRef r,void *c){(void)r;(void)c;apply_number();window_stack_pop(true);if(storage_error)show_notice(T(LK_Fortschritt_8dc68203),5,T(LK_Fortschritt_nicht_gespeichert_Bitte_App_neu_s_2095b54e));}
static void num_clicks(void *ctx){(void)ctx;window_single_repeating_click_subscribe(BUTTON_ID_UP,100,num_up);window_single_repeating_click_subscribe(BUTTON_ID_DOWN,100,num_down);window_single_click_subscribe(BUTTON_ID_SELECT,num_select);}
static void edit_number(int field,const char *title,int value,int min,int max){number_field=field;snprintf(number_title,sizeof(number_title),"%s",title);number_value=value;number_min=min;number_max=max;layer_mark_dirty(num_layer);window_stack_push(num_window,true);}
static int month_days(int year,int month) {static const int days[]={31,28,31,30,31,30,31,31,30,31,30,31};return days[month]+(month==1&&year%4==0&&(year%100!=0||year%400==0));}
static void date_draw(Layer *l,GContext *ctx){

 (void)l;static char value[32];graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,UI_HEIGHT),0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,date_mode?T(LK_Uhrzeit_b0b30059):T(LK_Datum_df5c3008),fonts_get_system_font(FONT_KEY_GOTHIC_24_BOLD),GRect(4,8,UI_WIDTH-8,34),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
 if(date_mode)snprintf(value,sizeof(value),T("%02d:%02d"),date_value.tm_hour,date_value.tm_min);else snprintf(value,sizeof(value),T("%02d.%02d.%04d"),date_value.tm_mday,date_value.tm_mon+1,date_value.tm_year+1900);
 graphics_context_set_text_color(ctx,GColorCyan);graphics_draw_text(ctx,value,fonts_get_system_font(date_mode?FONT_KEY_BITHAM_30_BLACK:FONT_KEY_GOTHIC_24_BOLD),GRect(4,55,UI_WIDTH-8,43),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);graphics_context_set_fill_color(ctx,GColorCyan);int fieldw=(UI_WIDTH-12)/(date_mode?2:3);graphics_fill_rect(ctx,GRect(6+date_field*fieldw,100,fieldw-4,2),0,GCornerNone);
 const char *label=date_mode?(date_field?T(LK_Minuten_497af2bf):T(LK_Stunden_f3bf6eff)):(date_field==0?T(LK_Tag_982963c1):date_field==1?T(LK_Monat_da13625e):T(LK_Jahr_956a6e5a));graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,label,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(4,106,UI_WIDTH-8,28),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);touch_controls(ctx,date_mode?date_field<1:date_field<2);
}
static void date_adjust(int delta){int *v,min,max;
 if(date_mode){v=date_field?&date_value.tm_min:&date_value.tm_hour;min=0;max=date_field?59:23;}
 else if(date_field==0){v=&date_value.tm_mday;min=1;max=month_days(date_value.tm_year+1900,date_value.tm_mon);}
 else if(date_field==1){v=&date_value.tm_mon;min=0;max=11;}else{v=&date_value.tm_year;min=126;max=137;}
 *v+=delta;if(*v<min)*v=max;if(*v>max)*v=min;
 int days=month_days(date_value.tm_year+1900,date_value.tm_mon);if(date_value.tm_mday>days)date_value.tm_mday=days;
 layer_mark_dirty(date_layer);
}
static void date_up(ClickRecognizerRef r,void *ctx){(void)r;(void)ctx;date_adjust(1);}
static void date_down(ClickRecognizerRef r,void *ctx){(void)r;(void)ctx;date_adjust(-1);}
static void date_select(ClickRecognizerRef r,void *ctx){(void)r;(void)ctx;if(++date_field==(date_mode?2:3)){draft_tm=date_value;refresh();window_stack_pop(true);}else layer_mark_dirty(date_layer);}
static void date_clicks(void *ctx){(void)ctx;window_single_repeating_click_subscribe(BUTTON_ID_UP,130,date_up);window_single_repeating_click_subscribe(BUTTON_ID_DOWN,130,date_down);window_single_click_subscribe(BUTTON_ID_SELECT,date_select);}
static void edit_datetime(int mode){date_mode=mode;date_field=0;date_value=draft_tm;layer_mark_dirty(date_layer);window_stack_push(date_window,true);}

static void touch_controls(GContext *ctx,bool next){

#if defined(PBL_PLATFORM_FLINT)
 (void)next;graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,T(LK_Oben_Unten_3f15d803),fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,UI_HEIGHT-23,UI_WIDTH-8,22),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
#else
 int width=(UI_WIDTH-16)/3,y=UI_HEIGHT-40;graphics_context_set_fill_color(ctx,GColorCyan);for(int i=0;i<3;i++)graphics_fill_rect(ctx,GRect(4+i*(width+4),y,width,34),0,GCornerNone);graphics_context_set_text_color(ctx,GColorOxfordBlue);const char *labels[]={"-",next?T(LK_Weiter_aeff967b):"OK","+"};for(int i=0;i<3;i++)graphics_draw_text(ctx,labels[i],fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(4+i*(width+4),y+3,width,28),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
#endif
}
static void __attribute__((unused)) touch_handler(const TouchEvent *event,void *context) {
 TouchEvent local=*event;local.x-=UI_LEFT;local.y-=UI_TOP;event=&local;
 (void)context;static bool active,moved;static int16_t x0,y0,last_x,last_y,scroll0,max_distance;static int axis;static Window *target;static Page touch_page;
 if(event->non_navigational){active=false;cancel_progress_touch();return;}
 Window *top=window_stack_get_top_window();
 if(top!=window&&top!=num_window&&top!=date_window&&top!=msg_window){cancel_progress_touch();return;}
 ScrollLayer *scroll=top==window?menu_layer_get_scroll_layer(menu):msg_scroll;
 if(event->type==TouchEvent_Touchdown){
  if(event->x<0||event->x>=UI_WIDTH||event->y<0||event->y>=UI_HEIGHT){active=false;cancel_progress_touch();return;}
  if(top==window&&(event->y<0||event->y>=layer_get_bounds(scroll_layer_get_layer(scroll)).size.h)){active=false;cancel_progress_touch();return;}
  active=true;moved=false;axis=0;target=top;touch_page=page;x0=last_x=event->x;y0=last_y=event->y;max_distance=0;
  scroll0=scroll_layer_get_content_offset(scroll).y;
  progress_hold_fired=false;cancel_progress_touch();if(top==window)start_progress_touch(event->y);
  if(top==window){MenuIndex current=menu_layer_get_selected_index(menu);menu_layer_set_selected_index(menu,current,MenuRowAlignNone,false);scroll_layer_set_content_offset(scroll,GPoint(0,scroll0),false);}
  return;
 }
 if(!active||target!=top||(top==window&&touch_page!=page)){active=false;cancel_progress_touch();return;}
 if(event->type==TouchEvent_PositionUpdate){last_x=event->x;last_y=event->y;}
 int x=last_x,y=last_y;int dx=x-x0,dy=y-y0;int ax=abs(dx),ay=abs(dy);if(ax+ay>max_distance)max_distance=ax+ay;
 if(max_distance>12)cancel_progress_touch();
 if(progress_hold_fired){active=false;cancel_progress_touch();return;}
 if(!axis&&max_distance>12)axis=ay>ax?1:2;
 if(event->type==TouchEvent_PositionUpdate&&(top==window||top==msg_window)&&axis==1){
  int minimum=layer_get_bounds(scroll_layer_get_layer(scroll)).size.h-scroll_layer_get_content_size(scroll).h;if(minimum>0)minimum=0;
  int raw=scroll0+dy,value=raw;if(value>0)value=0;if(value<minimum)value=minimum;
  scroll_layer_set_content_offset(scroll,GPoint(0,value),false);moved=true;
  // Rebase at a hard edge: reversing the finger moves immediately, with no elastic dead zone.
  if(raw!=value){scroll0=value;y0=y;}
  return;
 }
 if(event->type!=TouchEvent_Liftoff)return;
 cancel_progress_touch();
 active=false;
 if(axis!=1&&dx>50&&ax>ay){if(top==window)back(NULL,NULL);else window_stack_pop(true);return;}
 if(top==window){
  if(y<0||y>=layer_get_bounds(scroll_layer_get_layer(scroll)).size.h)return;
  if(moved||max_distance>20)return;
  int content_y=y-scroll_layer_get_content_offset(scroll).y;
  int cursor=header_height(menu,0,NULL),count=rows(menu,0,NULL);
  for(int row=0;row<count;row++){
   MenuIndex index=MenuIndex(0,row);int height=row_height(menu,&index,NULL);
   if(content_y>=cursor&&content_y<cursor+height){
    if(menu_layer_get_selected_index(menu).row==row)select_row(menu,&index,NULL);
    else menu_layer_set_selected_index(menu,index,MenuRowAlignNone,false);
    break;
   }
   cursor+=height;
  }
  return;
 }
 if(top==msg_window)return;
 if(ay>40&&ay>ax){if(top==num_window){if(dy<0)num_up(NULL,NULL);else num_down(NULL,NULL);}else date_adjust(dy<0?1:-1);return;}
 if(moved||max_distance>20)return;
 if(y>=UI_HEIGHT-42&&y<=UI_HEIGHT-4){
  if(x<UI_WIDTH/3){if(top==num_window)num_down(NULL,NULL);else date_adjust(-1);}
  else if(x>=UI_WIDTH*2/3){if(top==num_window)num_up(NULL,NULL);else date_adjust(1);}
  else {if(top==num_window)num_select(NULL,NULL);else date_select(NULL,NULL);}
 }else if(top==date_window&&y>=50&&y<=104){date_field=date_mode?(x<UI_WIDTH/2?0:1):(x<UI_WIDTH/3?0:x<UI_WIDTH*2/3?1:2);layer_mark_dirty(date_layer);}
}

static int topic_count(void){return 12+targets()[5];}
static int pick_count(void){if(draft.kind==5)return 13;if(draft.kind==6){Rule temp[10];int n=rules_for(draft.cls,temp);int p=profiles[draft.cls]<n?profiles[draft.cls]:0;return 1+temp[p].target[5];}return 1;}
static uint16_t rows(MenuLayer *m,uint16_t s,void *ctx){(void)m;(void)s;(void)ctx;switch(page){
 case HOME:return 7;case SETTINGS:case EXPLANATIONS:return 3;case LIST:return list_count+1;case PENDING:return list_count?list_count:1;case CLASSES:return 16;case PROFILES:return rule_count;case EDIT:return 9;case KINDS:return draft.cls==14?2:7;case PROGRESS:return 7;case ACTIONS:return selected_valid()?5:1;case DELETE_CONFIRM:return 2;case COMPLETE_CONFIRM:return 3;case TOPICS:return topic_count();case TOPIC_PICK:return pick_count();case ALERT:return alert_count+2;case PROGRESS_ACTIONS:return !progress_can_hold(progress_counter)?1:progress_counter==4||progress_counter==5?2:3;case PROGRESS_RESET:return 2;}return 0;}
static int16_t separator_height(MenuLayer *m,MenuIndex *i,void *ctx){(void)m;(void)i;(void)ctx;return 0;}
static int16_t header_height(MenuLayer *m,uint16_t s,void *ctx){
(void)m;(void)s;(void)ctx;return page==HOME?112:(page==PROGRESS||page==TOPICS||page==TOPIC_PICK)?48:36;
}
static void list_entry_title(const Entry *e,char *text,size_t size){
 const char *const names[]={LK_Ubungsfahrt_0b8286c5,LK_Landstrasse_5984748c,LK_Autobahn_d2c9f448,LK_Nachtfahrt_ffa854d3,LK_Grundausbildung_4b389408,LK_Grundstoff_bae3ed52,LK_Zusatzstoff_614bd4e2};
 const char *name=e->kind>=5?T(kinds[e->kind]):T(names[e->kind]);
 if(e->cls!=cfg.cls)snprintf(text,size,"%s | %s",classes[e->cls],name);else snprintf(text,size,"%s",name);
}
static int list_title_height(const char *text){
GSize size=graphics_text_layout_get_content_size(text,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(0,0,UI_WIDTH-12,44),GTextOverflowModeWordWrap,GTextAlignmentLeft);return size.h<18?18:size.h>36?36:size.h;
}

static int16_t row_height(MenuLayer *m,MenuIndex *i,void *ctx){

 (void)m;(void)i;(void)ctx;if(page==HOME)return 34;if(page==PROGRESS)return 54;if(page==LIST||page==PENDING||page==ALERT)return 60;return 48;
}
static void footer_draw(Layer *layer,GContext *ctx){

 (void)layer;graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,20),0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,T(LK_Hakchen_zahlen_als_Einheit_c1616440),fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(3,0,UI_WIDTH-6,20),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
}
static void class_icon(GContext *ctx,int cls,GPoint point) {
 if(cls<0||cls>=16)return;
 graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(point.x-1,point.y-1,38,36),4,GCornersAll);
 if(!class_icons[cls]){
#if defined(PBL_PLATFORM_FLINT)
 int cached=0;for(int i=0;i<16;i++)if(class_icons[i])cached++;
 if(cached>=4)for(int i=0;i<16;i++)if(i!=cls&&class_icons[i]){gbitmap_destroy(class_icons[i]);class_icons[i]=NULL;break;}
#endif
 static const uint32_t resources[]={RESOURCE_ID_CLASS_0,RESOURCE_ID_CLASS_1,RESOURCE_ID_CLASS_2,RESOURCE_ID_CLASS_3,RESOURCE_ID_CLASS_4,RESOURCE_ID_CLASS_5,RESOURCE_ID_CLASS_6,RESOURCE_ID_CLASS_7,RESOURCE_ID_CLASS_8,RESOURCE_ID_CLASS_9,RESOURCE_ID_CLASS_10,RESOURCE_ID_CLASS_11,RESOURCE_ID_CLASS_12,RESOURCE_ID_CLASS_13,RESOURCE_ID_CLASS_14,RESOURCE_ID_CLASS_15};class_icons[cls]=gbitmap_create_with_resource(resources[cls]);}
 if(class_icons[cls]){graphics_context_set_compositing_mode(ctx,
#if defined(PBL_PLATFORM_FLINT)
 GCompOpAssign
#else
 GCompOpSet
#endif
 );graphics_draw_bitmap_in_rect(ctx,class_icons[cls],GRect(point.x,point.y,36,34));graphics_context_set_compositing_mode(ctx,GCompOpAssign);}
}

static void home_header_draw(GContext *ctx){

 graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,GRect(0,0,UI_WIDTH,112),0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);static char text[90],date[32],clock[12];int next=next_entry();
 graphics_draw_text(ctx,T(LK_Fahrschul_Planer_8d88df9a),fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(3,0,UI_WIDTH-6,24),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);snprintf(text,sizeof(text),T(LK_Klasse_s_8e6c0375),cfg.cls>=0?classes[cfg.cls]:"?");graphics_draw_text(ctx,text,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,22,UI_WIDTH-8,18),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
 const char *const lessons[]={LK_Ubungsfahrt_0b8286c5,LK_Landstrasse_5984748c,LK_Autobahn_d2c9f448,LK_Nachtfahrt_ffa854d3,LK_Grundausbildung_4b389408,LK_Grundstoff_bae3ed52,LK_Zusatzstoff_614bd4e2};
 if(next>=0){Entry *e=&entries[next];time_t when=e->when;snprintf(text,sizeof(text),"%s",T(lessons[e->kind]));strftime(date,sizeof(date),T("%d.%m.%Y"),localtime(&when));strftime(clock,sizeof(clock),"%H:%M",localtime(&when));}else{snprintf(text,sizeof(text),"%s",T(LK_Noch_kein_Termin_13cfe16f));snprintf(date,sizeof(date),"%s",T(LK_Plane_deine_Fahrstunde_4a4fb061));snprintf(clock,sizeof(clock),"--:--");}
 if(storage_error)snprintf(text,sizeof(text),"%s",T(LK_Speicherfehler_Neu_starten_607689d0));else if(!alarm_ok)snprintf(text,sizeof(text),"%s",T(LK_Alarm_fehlt_Erneut_versuchen_f0f5d684));
 graphics_draw_text(ctx,text,fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD),GRect(4,39,UI_WIDTH-8,20),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);graphics_draw_text(ctx,date,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,58,UI_WIDTH-8,20),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);graphics_context_set_text_color(ctx,GColorCyan);graphics_draw_text(ctx,clock,fonts_get_system_font(FONT_KEY_BITHAM_30_BLACK),GRect(3,74,UI_WIDTH-6,38),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
}
static void header_draw(GContext *ctx,const Layer *l,uint16_t s,void *c){(void)s;(void)c;GRect b=layer_get_bounds(l);graphics_context_set_fill_color(ctx,GColorOxfordBlue);graphics_fill_rect(ctx,b,0,GCornerNone);graphics_context_set_text_color(ctx,GColorWhite);
 const char *title=T(LK_Fahrschul_Planer_8d88df9a);switch(page){case HOME:break;case SETTINGS:title=T(LK_Einstellungen_3e5af3d1);break;case EXPLANATIONS:title=T(LK_Erklarungen_7478dc86);break;case LIST:title=T(LK_Deine_Termine_434b258a);break;case PENDING:title=T(LK_Stunden_offen_c03ff006);break;case CLASSES:title=T(LK_Deine_Klasse_a47f71c8);break;case PROFILES:title=T(LK_Dein_Vorbesitz_56d7a40b);break;case EDIT:title=T(LK_Termin_planen_7c23b5cd);break;case KINDS:title=T(LK_Unterrichtsart_d97b7c6c);break;case PROGRESS:title=T(LK_Dein_Fortschritt_91784f7a);break;case ACTIONS:title=T(LK_Dein_Termin_18955587);break;case DELETE_CONFIRM:title=T(LK_Termin_loschen_f7eb0937);break;case COMPLETE_CONFIRM:title=T(LK_Unterricht_erledigt_0214b13c);break;case TOPICS:title=T(LK_Theorie_Themen_e8712ee4);break;case TOPIC_PICK:title=T(LK_Thema_wahlen_00e51575);break;case ALERT:title=T(LK_Termin_Erinnerung_4c7140c4);break;case PROGRESS_ACTIONS:title=T(LK_Zusatze_verwalten_111554a0);break;case PROGRESS_RESET:title=T(LK_Zusatze_loschen_c505ae07);break;}
 if(page!=HOME){
  GFont font=fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD);GSize size=graphics_text_layout_get_content_size(title,font,GRect(0,0,UI_WIDTH-12,80),GTextOverflowModeWordWrap,GTextAlignmentCenter);int y=(36-size.h)/2-5;graphics_context_set_text_color(ctx,GColorWhite);graphics_draw_text(ctx,title,font,GRect(6,y,UI_WIDTH-12,36-y),GTextOverflowModeWordWrap,GTextAlignmentCenter,NULL);
  static char subtitle[70];subtitle[0]=0;if(page==PROGRESS)snprintf(subtitle,sizeof(subtitle),"%s",T(LK_OK_halten_Zusatze_6fe498bb));else if(page==TOPICS)snprintf(subtitle,sizeof(subtitle),T(LK_Klasse_s_d_Themen_84450d4f),classes[cfg.cls],topic_count());else if(page==TOPIC_PICK)snprintf(subtitle,sizeof(subtitle),T(LK_Klasse_s_8e6c0375),classes[draft.cls]);
  if(subtitle[0])graphics_draw_text(ctx,subtitle,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(4,29,UI_WIDTH-8,20),GTextOverflowModeTrailingEllipsis,GTextAlignmentCenter,NULL);
  return;
 }
 home_header_draw(ctx);
}
static void row_chevron(GContext *ctx,int height){
graphics_context_set_stroke_width(ctx,2);int y=height/2;graphics_draw_line(ctx,GPoint(UI_WIDTH-12,y-4),GPoint(UI_WIDTH-8,y));graphics_draw_line(ctx,GPoint(UI_WIDTH-8,y),GPoint(UI_WIDTH-12,y+4));
}
static void standard_row(GContext *ctx,const Layer *layer,const char *title,const char *subtitle,bool large_value){

 (void)large_value;int height=layer_get_bounds(layer).size.h;GFont font=fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD);GSize size=graphics_text_layout_get_content_size(title,font,GRect(0,0,1000,30),GTextOverflowModeWordWrap,GTextAlignmentLeft);if(subtitle[0]&&size.w>UI_WIDTH-16)font=fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD);
 graphics_draw_text(ctx,title,font,GRect(6,subtitle[0]?0:5,UI_WIDTH-12,subtitle[0]?24:height-6),GTextOverflowModeWordWrap,GTextAlignmentLeft,NULL);
 if(subtitle[0])graphics_draw_text(ctx,subtitle,fonts_get_system_font(FONT_KEY_GOTHIC_18),GRect(6,22,UI_WIDTH-12,25),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);
}
static bool cell_selected(const Layer *layer){return menu_cell_layer_is_highlighted(layer);}
static void progress_row(GContext *ctx,const Layer *layer,int row){

 const char *const labels[]={LK_Landstrasse_5984748c,LK_Autobahn_d2c9f448,LK_Nachtfahrt_ffa854d3,LK_Grundausbildung_4b389408,LK_Grundstoff_bae3ed52,LK_Zusatzstoff_614bd4e2,LK_Ubungsfahrten_ad92b736};unsigned value=row<6?counts[cfg.cls][row]:practice[cfg.cls].exercise_units,goal=row<6?targets()[row]:0,rest=(row<4||row==6)?practice[cfg.cls].remainder[row<4?row:4]:0;static char count[32],note[64];if(goal)snprintf(count,sizeof(count),"%u/%u",value,goal);else snprintf(count,sizeof(count),"%u",value);
 int count_width=51;graphics_draw_text(ctx,T(labels[row]),fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD),GRect(6,1,UI_WIDTH-count_width-16,23),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);graphics_draw_text(ctx,count,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(UI_WIDTH-6-count_width,0,count_width,25),GTextOverflowModeTrailingEllipsis,GTextAlignmentRight,NULL);
 
 bool selected=cell_selected(layer);
#if defined(PBL_PLATFORM_FLINT)
 graphics_context_set_fill_color(ctx,selected?GColorBlack:GColorWhite);
#else
 graphics_context_set_fill_color(ctx,GColorWhite);
#endif
 graphics_fill_rect(ctx,GRect(6,28,UI_WIDTH-12,7),0,GCornerNone);
#if defined(PBL_PLATFORM_FLINT)
 graphics_context_set_fill_color(ctx,selected?GColorWhite:GColorBlack);
#else
 graphics_context_set_fill_color(ctx,selected?GColorOxfordBlue:GColorCyan);
#endif
 int fill=goal?(int)((UI_WIDTH-14)*(value<goal?value:goal)/goal):(value?UI_WIDTH-14:0);if(fill)graphics_fill_rect(ctx,GRect(7,29,fill,5),0,GCornerNone);
#if defined(PBL_PLATFORM_FLINT)
 graphics_context_set_stroke_color(ctx,selected?GColorWhite:GColorBlack);
#else
 graphics_context_set_stroke_color(ctx,GColorOxfordBlue);
#endif
 graphics_context_set_stroke_width(ctx,1);graphics_draw_rect(ctx,GRect(6,28,UI_WIDTH-12,7));graphics_context_set_text_color(ctx,selected?UI_SELECTION_TEXT:GColorOxfordBlue);
 if(rest)snprintf(note,sizeof(note),T(LK_u_Minuten_6e6eddeb),rest);else snprintf(note,sizeof(note),"%s",T(row==4||row==5?LK_90_Minuten_Einheiten_95292d40:LK_45_Minuten_Einheiten_89b80737));graphics_draw_text(ctx,note,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(6,35,UI_WIDTH-12,19),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);
}
static void topic_row(GContext *ctx,int topic){

 static char text[96];if(topic>=12&&cfg.cls!=4)snprintf(text,sizeof(text),T(LK_Zusatzstoff_d_555ebbbd),topic-11);else snprintf(text,sizeof(text),"%s",T(topic_label(cfg.cls,topic)));
 graphics_context_set_stroke_width(ctx,2);graphics_draw_rect(ctx,GRect(5,17,14,14));if(topics[cfg.cls]&(1u<<topic)){graphics_draw_line(ctx,GPoint(7,23),GPoint(11,27));graphics_draw_line(ctx,GPoint(11,27),GPoint(17,20));}graphics_draw_text(ctx,text,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(25,0,UI_WIDTH-31,47),GTextOverflowModeWordWrap,GTextAlignmentLeft,NULL);
}
static void separator_draw(GContext *ctx,const Layer *layer,MenuIndex *index,void *context){(void)ctx;(void)layer;(void)index;(void)context;}
static void row_draw(GContext *ctx,const Layer *l,MenuIndex *idx,void *c){(void)c;int r=idx->row;if(!language_pack_ready()&&page!=ALERT&&!(page==ACTIONS&&(r==2||r==3))){language_setup_notice=true;show_notice("Sprache / Language",1,"Bitte Sprache in den Handy-Einstellungen laden.\n\nLoad a language in the phone settings.\n\nTermine und Alarme bleiben gespeichert.");return;}static char title[90],sub[100];title[0]=sub[0]=0;Entry *e=selected_valid()?&entries[selected]:NULL;
 switch(page){
 case HOME:switch(r){
 case 0:snprintf(title,sizeof(title),T(LK_Neuer_Termin_39e943e7));break;
 case 1:snprintf(title,sizeof(title),T(LK_Alle_Termine_d_f64ff486),active_count());break;
 case 2:snprintf(title,sizeof(title),T(LK_Stunden_buchen_d_dae17580),pending_count());break;
 case 3:snprintf(title,sizeof(title),T(LK_Pflichtstunden_85cf0708));break;
 case 4:snprintf(title,sizeof(title),T(LK_Theorie_Themen_e8712ee4));break;
 case 5:snprintf(title,sizeof(title),T(LK_Einstellungen_3e5af3d1));break;
 case 6:snprintf(title,sizeof(title),T(LK_Erklarungen_7478dc86));break;}break;
 case SETTINGS:switch(r){
 case 0:snprintf(title,sizeof(title),T(LK_Klasse_s_8e6c0375),classes[cfg.cls]);snprintf(sub,sizeof(sub),T(LK_Termine_aller_Klassen_bleiben_1a97c507));break;
 case 1:snprintf(title,sizeof(title),T(LK_Ausbildungsprofil_fe95ffc9));snprintf(sub,sizeof(sub),T("%s"),T(rules[cfg.profile].label));break;
 case 2:snprintf(title,sizeof(title),T("%s"),alarm_ok?T(LK_Alarm_testen_9c4a140c):T(LK_Alarm_erneut_aktivieren_f18225d8));snprintf(sub,sizeof(sub),T("%s"),alarm_ok?T(LK_App_schliessen_Test_in_1_Min_bbc128d6):T(LK_Alle_gespeicherten_Termine_prufen_3317064f));break;}break;
 case EXPLANATIONS:switch(r){
 case 0:snprintf(title,sizeof(title),T(LK_Rechtliche_Vorgaben_88580760));snprintf(sub,sizeof(sub),T(LK_FahrschAusbO_Stand_06_11_26_f99f7725));break;
 case 1:snprintf(title,sizeof(title),T(LK_Bedingungen_Kurzel_dd2d41c3));snprintf(sub,sizeof(sub),T(LK_Fahrschul_Planer_3_8_44_094fa0f8));break;
 case 2:snprintf(title,sizeof(title),T(LK_Handy_Eingabe_ded1a7d1));snprintf(sub,sizeof(sub),T(LK_Einstellungen_in_der_Pebble_App_3f190208));break;}break;
 case LIST:case PENDING:{if(page==LIST&&r==0){snprintf(title,sizeof(title),T(LK_Neuer_Termin_39e943e7));snprintf(sub,sizeof(sub),T(LK_d_von_24_Platzen_belegt_3ea313e3),active_count());break;}int pos=page==LIST?r-1:r;if(pos>=list_count){snprintf(title,sizeof(title),T(LK_Alles_erledigt_99db5fa9));break;}Entry *x=&entries[list_map[pos]];list_entry_title(x,title,sizeof(title));char dt[32];time_t when=x->when;strftime(dt,sizeof(dt),T(LK_d_m_H_M_191558b7),localtime(&when));snprintf(sub,sizeof(sub),T("%s%s"),end_time(x)<=time(NULL)?T(LK_Offen_708ea52e):T(""),dt);break;}
 case CLASSES:snprintf(title,sizeof(title),T(LK_Klasse_s_8e6c0375),classes[r]);snprintf(sub,sizeof(sub),T("%s"),r==cfg.cls?T(LK_Aktuell_ausgewahlt_70d8c2da):T(LK_Termine_und_Fortschritt_behalten_e899ec9f));break;
 case PROFILES:snprintf(title,sizeof(title),T("%s"),T(rules[r].label));snprintf(sub,sizeof(sub),T("LA %u | AU %u | NA %u"),rules[r].target[0],rules[r].target[1],rules[r].target[2]);break;
 case EDIT:switch(r){
 case 0:snprintf(title,sizeof(title),T("%s"),T(kinds[draft.kind]));break;
 case 1:snprintf(title,sizeof(title),T(LK_Datum_df5c3008));snprintf(sub,sizeof(sub),T("%02d.%02d.%04d"),draft_tm.tm_mday,draft_tm.tm_mon+1,draft_tm.tm_year+1900);break;
 case 2:snprintf(title,sizeof(title),T(LK_Uhrzeit_b0b30059));snprintf(sub,sizeof(sub),T("%02d:%02d"),draft_tm.tm_hour,draft_tm.tm_min);break;
 case 3:case 4:snprintf(title,sizeof(title),T(LK_Erinnerung_d_530934a0),r-2);lead_text(draft.lead[r-3],sub,sizeof(sub));break;
 case 5:if(draft_uses_minutes())snprintf(title,sizeof(title),T(LK_Dauer_d_Minuten_2207b039),duration_minutes(&draft));else snprintf(title,sizeof(title),T(LK_Einheiten_d_ad88f070),draft.units);snprintf(sub,sizeof(sub),"%s",T(draft.kind>=5?LK_Theorie_90_Minuten_Einheiten_1ca5e72f:draft_uses_minutes()?LK_In_5_Minuten_Schritten_5baac6b7:LK_45_Minuten_Einheiten_89b80737));break;
 case 6:snprintf(title,sizeof(title),T(LK_Theorie_Thema_0f0e1da9));snprintf(sub,sizeof(sub),T("%s"),draft.topic==NO_TOPIC?T(LK_Optional_keine_Zuordnung_d3f3e089):T(topic_label(draft.cls,draft.topic)));break;
 case 7:snprintf(title,sizeof(title),T(LK_Termin_speichern_aa17f0d9));snprintf(sub,sizeof(sub),T(LK_Klasse_s_Abschlussfrage_aktiv_80957490),classes[draft.cls]);break;
 case 8:snprintf(title,sizeof(title),T(LK_Abbrechen_07af7cb3));break;}break;
 case KINDS:snprintf(title,sizeof(title),T("%s"),T(kinds[draft.cls==14?r+5:r]));break;
 case PROGRESS:break;
 case ACTIONS:if(!e){snprintf(title,sizeof(title),T(LK_Termin_nicht_mehr_vorhanden_a62acf37));break;}switch(r){case 0:snprintf(title,sizeof(title),T(LK_Termin_bearbeiten_3f6ebbb4));date_text(e->when,sub,sizeof(sub));break;case 1:snprintf(title,sizeof(title),T(LK_Erledigt_Stunden_buchen_ecc5c235));snprintf(sub,sizeof(sub),T(LK_d_Minuten_Klasse_s_dc3ad3c7),duration_minutes(e),classes[e->cls]);break;case 2:snprintf(title,sizeof(title),T(LK_Details_Erinnerungen_7a6a64d6));snprintf(sub,sizeof(sub),T("%s"),T(kinds[e->kind]));break;case 3:snprintf(title,sizeof(title),T(LK_In_10_Minuten_erinnern_43087abe));snprintf(sub,sizeof(sub),T(LK_Zusatzliche_Erinnerung_2263a43a));break;case 4:snprintf(title,sizeof(title),T(LK_Termin_loschen_9bfb61ae));break;}break;
 case DELETE_CONFIRM:snprintf(title,sizeof(title),T("%s"),r?T(LK_Ja_Termin_loschen_e0ba48da):T(LK_Abbrechen_07af7cb3));break;
 case COMPLETE_CONFIRM:if(!e){snprintf(title,sizeof(title),T(LK_Termin_nicht_mehr_vorhanden_a62acf37));break;}switch(r){case 0:snprintf(title,sizeof(title),T(LK_Ja_Stunden_buchen_2d1d1f56));snprintf(sub,sizeof(sub),T(LK_s_d_Min_3298839c),T(kinds[e->kind]),duration_minutes(e));break;case 1:snprintf(title,sizeof(title),T(LK_In_30_Minuten_fragen_75fcd236));snprintf(sub,sizeof(sub),T(LK_Noch_nicht_abgeschlossen_980e3738));break;case 2:snprintf(title,sizeof(title),T(LK_Spater_manuell_buchen_58d2bb4f));snprintf(sub,sizeof(sub),T(LK_Bleibt_unter_Stunden_buchen_1ab7aff2));break;}break;
 case PROGRESS_ACTIONS:{bool theory=progress_counter==4||progress_counter==5;if(r==0){snprintf(title,sizeof(title),T("%s"),theory?T(LK_Manuell_bearbeiten_36c9c1ae):T(LK_Einheiten_bearbeiten_b9c71b65));snprintf(sub,sizeof(sub),T("%s"),theory?T(LK_Hakchen_bleiben_geschutzt_9fd983c9):T(LK_Ganze_45_Minuten_Einheiten_0c307db1));}else if(!theory&&r==1){snprintf(title,sizeof(title),T(LK_Minuten_bearbeiten_c3d8ba37));snprintf(sub,sizeof(sub),T(LK_In_5_Minuten_Schritten_5baac6b7));}else{snprintf(title,sizeof(title),T("%s"),theory?T(LK_Manuell_loschen_07c7e580):T(LK_Minuten_loschen_ed408384));snprintf(sub,sizeof(sub),T("%s"),theory?T(LK_Hakchen_bleiben_geschutzt_9fd983c9):T(LK_Ganze_Einheiten_bleiben_0d6249a0));}break;}
 case PROGRESS_RESET:snprintf(title,sizeof(title),T("%s"),r?T(LK_Ja_Zusatze_loschen_e89189c5):T(LK_Abbrechen_07af7cb3));break;
 case TOPICS:break;
 case TOPIC_PICK:if(!r){snprintf(title,sizeof(title),T(LK_Keine_Zuordnung_af83cfb5));break;}int t=draft.kind==5?r-1:r+11;snprintf(title,sizeof(title),T("%s %d"),draft.kind==5?T(LK_Grundstoff_bae3ed52):T(LK_Zusatzstoff_614bd4e2),r);snprintf(sub,sizeof(sub),T("%s"),T(topic_label(draft.cls,t)));break;
 case ALERT:if(r<alert_count){Entry *x=&entries[alert_queue[r]];list_entry_title(x,title,sizeof(title));date_text(x->when,sub,sizeof(sub));}else if(r==alert_count){snprintf(title,sizeof(title),T(LK_Alle_in_10_Min_erinnern_17d35f7f));snprintf(sub,sizeof(sub),T(LK_d_Termin_e_ed32968f),alert_count);}else snprintf(title,sizeof(title),T(LK_Erinnerung_schliessen_a7551e14));break;
 }
 graphics_context_set_text_color(ctx,cell_selected(l)?UI_SELECTION_TEXT:GColorOxfordBlue);graphics_context_set_stroke_color(ctx,cell_selected(l)?UI_SELECTION_TEXT:GColorOxfordBlue);
 if(page==HOME){GFont font=fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD);GSize size=graphics_text_layout_get_content_size(title,font,GRect(0,0,1000,30),GTextOverflowModeWordWrap,GTextAlignmentLeft);if(size.w>UI_WIDTH-26)font=fonts_get_system_font(FONT_KEY_GOTHIC_14_BOLD);graphics_draw_text(ctx,title,font,GRect(6,3,UI_WIDTH-23,30),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);row_chevron(ctx,34);}
 else if(page==PROGRESS)progress_row(ctx,l,r);
 else if(page==TOPICS)topic_row(ctx,r);
 else if(page==CLASSES){class_icon(ctx,r,GPoint(3,7));graphics_context_set_text_color(ctx,cell_selected(l)?UI_SELECTION_TEXT:GColorOxfordBlue);graphics_draw_text(ctx,title,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(44,0,UI_WIDTH-48,27),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);graphics_draw_text(ctx,sub,fonts_get_system_font(FONT_KEY_GOTHIC_14),GRect(44,26,UI_WIDTH-48,20),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);}
 else if(page==KINDS||(page==EDIT&&r==0))graphics_draw_text(ctx,title,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(6,0,UI_WIDTH-12,48),GTextOverflowModeWordWrap,GTextAlignmentLeft,NULL);
 else if((page==LIST&&r>0)||page==PENDING||(page==ALERT&&r<alert_count)){int y=list_title_height(title);graphics_draw_text(ctx,title,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(6,0,UI_WIDTH-12,y+2),GTextOverflowModeWordWrap,GTextAlignmentLeft,NULL);graphics_draw_text(ctx,sub,fonts_get_system_font(FONT_KEY_GOTHIC_18_BOLD),GRect(6,y,UI_WIDTH-12,25),GTextOverflowModeTrailingEllipsis,GTextAlignmentLeft,NULL);}
 else standard_row(ctx,l,title,sub,page==EDIT);
}

static void clear_alerts(void){alert_count=0;memset(alert_seen,0,sizeof(alert_seen));}
static void clear_completion(int index){completion_seen[index]=false;for(int i=0;i<completion_count;i++)if(completion_queue[i]==index){for(int j=i+1;j<completion_count;j++)completion_queue[j-1]=completion_queue[j];completion_count--;break;}}
static void snooze_entry(int index){entries[index].snooze=time(NULL)+600;store_entry(index);store_revision();}
static void details(Entry *e){static char text[650],dt[32],end[32],a[32],b[32];date_text(e->when,dt,sizeof(dt));date_text(end_time(e),end,sizeof(end));lead_text(e->lead[0],a,sizeof(a));lead_text(e->lead[1],b,sizeof(b));snprintf(text,sizeof(text),T("KLASSE %s\n%s\n%s\n\n%d Minuten\nGeplantes Ende:\n%s\n\nErinnerung 1: %s\nErinnerung 2: %s\n\n%s\n\nThema: %s"),classes[e->cls],T(kinds[e->kind]),dt,duration_minutes(e),end,a,b,alarm_ok?T(LK_Systemalarm_aktiv_53c692bd):T(LK_Alarmfehler_Erneut_aktivieren_0148dc48),e->topic==NO_TOPIC?T(LK_Keine_Zuordnung_af83cfb5):T(topic_label(e->cls,e->topic)));show_notice(T(LK_Termindetails_e5ad8bb2),6,text);}
static void choose_class(int cls){
 bool first_setup=cfg.cls<0;
 cfg.cls=cls;cfg.profile=profiles[cls];load_rules();store_config();store_revision();
 if(first_setup)show_page(PROFILES);else return_to(SETTINGS);
}
static void select_row(MenuLayer *m,MenuIndex *idx,void *ctx){(void)m;(void)ctx;int r=idx->row;Entry *e=selected_valid()?&entries[selected]:NULL;
 switch(page){
 case HOME:switch(r){
 case 0:begin_edit(-1);break;
 case 1:show_page(LIST);break;case 2:show_page(PENDING);break;case 3:show_page(PROGRESS);break;case 4:show_page(TOPICS);break;case 5:show_page(SETTINGS);break;case 6:show_page(EXPLANATIONS);break;}break;
 case SETTINGS:switch(r){case 0:show_page(CLASSES);break;case 1:show_page(PROFILES);break;
 case 2:if(!alarm_ok){process_events(false);show_notice(T(LK_Alarmstatus_b0ff7d4e),3,alarm_ok?T(LK_Alle_Alarme_sind_wieder_aktiv_f9e49aca):T("Alarme weiter blockiert. Bitte Uhr neu starten und hier erneut versuchen. Termine bleiben gespeichert."));}else{test_at=time(NULL)+60;persist_write_int(28,test_at);schedule_next();show_info(T(LK_Alarmtest_c4d250b1),3,alarm_ok?T("ALARMTEST\n\nApp jetzt schließen. In einer Minute öffnet sich die App mit Vibration. Deine Termine bleiben erhalten."):T(LK_Testalarm_konnte_nicht_aktiviert_werden_cd071da0));}break;
}break;
 case EXPLANATIONS:switch(r){
 case 2:show_info(T(LK_Handy_Eingabe_ded1a7d1),2,T("HANDY-EINGABE\n\nIn der Pebble-App beim Fahrschul Planer die Einstellungen öffnen. Dort Termine anlegen, bearbeiten und löschen.\n\nZur Übertragung die Uhr-App öffnen und Bluetooth verbinden.\n\nDie Uhr bleibt vollständig ohne diese Zusatzfunktion bedienbar."));break;
 case 1:show_info(T(LK_Bedingungen_Kurzel_dd2d41c3),1,T("FAHRSCHUL PLANER 3.8.44\n\n24 Termine, 2 Erinnerungen und 10-Min.-Schlummern.\nNach dem geplanten Ende fragt die Uhr nach Stunden. Gebucht wird nur nach Bestätigung.\n\nLA Landstraße / AU Autobahn\nNA Nacht / UE Übung\nGA Grundausbildung\nGS Grundstoff / ZS Zusatzstoff\n\nPraxis ab 45 Min., +5-Min.-Schritte.\n45 Restminuten ergeben 1 Einheit.\nTheorie je 90 Min.\nTheorie-Häkchen zählen als eine 90-Minuten-Einheit. Entfernen zieht diese Einheit ab. Zugeordnete Theorie-Termine zählen dasselbe Thema nicht doppelt.\nGS/ZS manuell bearbeitet nur zusätzliche Einheiten. Häkchen bleiben geschützt und können nur in der Themenliste entfernt werden.\n\nOben/Unten scrollen. Mitte wählt, Zurück schließt. OK unter Pflichtstunden halten: Zusätze bearbeiten oder löschen. Neue Termine: 01:00 und 00:30 vorher. Erinnerung 2 lässt sich direkt im Termin auf Aus stellen.\n\nVersion 3.8.44\n(Idee by Traumlewis | Code by Codex)"));break;
 case 0:show_info(T(LK_Rechtliche_Vorgaben_88580760),0,T("PFLICHTSTUNDEN\n\nFahrschAusbO: Par. 4, Anlagen 1, 2.2, 2.8, 4 und 5. Stand 06.11.2026.\n\nProfil passend zum Vorbesitz wählen. 0 = keine feste Mindestzahl, nicht keine Ausbildung.\n\nThemen sind eine Lernhilfe; Reihenfolge mit Fahrschule abstimmen. Zusatzstoff außer B wird als nummerierte Liste geführt.\n\nDetails in QUELLEN.md."));break;}break;
 case LIST:case PENDING:if(page==LIST&&!r){begin_edit(-1);break;}r-=page==LIST?1:0;if(r>=0&&r<list_count){selected=list_map[r];show_page(ACTIONS);}break;
 case CLASSES:choose_class(r);break;
 case PROFILES:cfg.profile=r;store_config();store_revision();if(navigation_depth&&navigation[0].page==HOME&&navigation_depth>1)return_to(SETTINGS);else return_to(HOME);break;
 case EDIT:switch(r){case 0:show_page(KINDS);menu_layer_set_selected_index(menu,MenuIndex(0,draft.cls==14?draft.kind-5:draft.kind),MenuRowAlignCenter,false);break;case 1:edit_datetime(0);break;case 2:edit_datetime(1);break;case 3:edit_number(5,T(LK_Erinnerung_1_940250b1),draft.lead[0]/15,1,192);break;case 4:edit_number(6,T(LK_Erinnerung_2_7c4d39d4),draft.lead[1]/15,0,192);break;case 5:if(draft_uses_minutes())edit_number(7,T(LK_Praxisdauer_Minuten_f86b6821),duration_minutes(&draft)/5,9,108);else edit_number(7,T(draft.kind>=5?LK_Theorie_Einheiten_03c02c33:LK_Praxis_Einheiten_618b345c),draft.units,1,12);break;case 6:if(draft.kind>=5)show_page(TOPIC_PICK);else show_notice(T(LK_Theorie_Thema_0f0e1da9),1,T(LK_Themen_sind_nur_fur_Theorie_Termine_verfugbar_5dac2058));break;case 7:save_draft();break;case 8:return_page();break;}break;
 case KINDS:draft.kind=draft.cls==14?r+5:r;draft.topic=NO_TOPIC;if(!draft_uses_minutes())draft.extra_minutes=0;return_page();break;
 case PROGRESS:if(r>=4&&r<6){unsigned protected=topic_units(cfg.cls,r);edit_number(10+r,r==4?T(LK_Grundstoff_manuell_0a5ee3e4):T(LK_Zusatzstoff_manuell_632c7a08),counts[cfg.cls][r]-protected,0,999-protected);}else if(r<4)edit_number(10+r,T(counters[r]),counts[cfg.cls][r],0,999);else edit_number(16,T(LK_Ubungsfahrten_ad92b736),practice[cfg.cls].exercise_units,0,999);break;
 case PROGRESS_ACTIONS:if(!progress_can_hold(progress_counter)&&r!=0)break;if(r==0){Page old=page;page=PROGRESS;MenuIndex index=MenuIndex(0,progress_counter);select_row(menu,&index,NULL);page=old;}else if(r==1&&progress_counter!=4&&progress_counter!=5){int slot=progress_counter<4?progress_counter:4;edit_number(17,T(LK_Zusatzminuten_b29c7da2),practice[cfg.cls].remainder[slot]/5,0,extra_minutes_limit(cfg.cls,progress_counter)/5);}else show_page(PROGRESS_RESET);break;
 case PROGRESS_RESET:if(r){bool theory=progress_counter==4||progress_counter==5;bool ok=theory?set_progress_count(cfg.cls,progress_counter,topic_units(cfg.cls,progress_counter)):set_extra_minutes(cfg.cls,progress_counter,0);if(!ok){show_notice(T(LK_Fortschritt_8dc68203),5,T(LK_Fortschritt_nicht_gespeichert_Bitte_App_neu_s_2095b54e));break;}}if(r)return_to(PROGRESS);else return_page();if(r)show_status(T(LK_Zusatze_geloscht_86ee3f20),T(LK_Pflichtstunden_85cf0708));break;
 case TOPICS:if(toggle_topic(cfg.cls,r))refresh();else show_notice(T(LK_Theorie_Themen_e8712ee4),1,T(LK_Thema_nicht_gespeichert_Bitte_App_neu_starten_adb2776d));break;
 case TOPIC_PICK:draft.topic=!r?NO_TOPIC:draft.kind==5?r-1:r+11;return_page();break;
 case ACTIONS:if(!e){return_to(HOME);break;}switch(r){case 0:begin_edit(selected);break;case 1:if(end_time(e)>time(NULL))show_notice(T(LK_Stunden_buchen_5d717818),1,T("Der Unterricht ist laut Planung noch nicht beendet. Danach kannst du die Stunden bestätigen. Vorhandene Stunden sind unter Pflichtstunden korrigierbar."));else show_page(COMPLETE_CONFIRM);break;case 2:details(e);break;case 3:snooze_entry(selected);clear_alerts();schedule_next();return_to(HOME);if(alarm_ok)show_status(T(LK_In_10_Minuten_77b8836e),T(LK_Erneute_Erinnerung_577b9f7b));else show_notice(T(LK_Alarmstatus_b0ff7d4e),3,T(LK_Schlummern_gespeichert_aber_Alarm_blockiert_B_ef01bf8a));break;case 4:show_page(DELETE_CONFIRM);break;}break;
 case DELETE_CONFIRM:if(r&&e){Entry old=*e;e->active=0;if(!store_entry(selected)){*e=old;show_notice(T(LK_Loschfehler_2e07ae38),4,T(LK_Loschen_nicht_gespeichert_Bitte_neu_starten_8c2263fa));break;}store_revision();state_changed();}else return_page();break;
 case COMPLETE_CONFIRM:if(!e){return_to(HOME);break;}if(r==0){if(book_entry(selected)){clear_completion(selected);state_changed();if(completion_count)surface_alerts();else show_status(T(LK_Stunden_gebucht_8ffcdc18),T(LK_Fortschritt_aktualisiert_7ce53448));}else show_notice(T(LK_Buchungsfehler_9e2083de),4,T("Buchung nicht gespeichert oder Unterricht noch nicht beendet. Bitte prüfen und App bei Speicherfehler neu starten."));}else{if(r==1)e->review=time(NULL)+1800;e->flags|=ASKED;store_entry(selected);store_revision();clear_completion(selected);schedule_next();if(completion_count)surface_alerts();else return_to(HOME);}break;
 case ALERT:if(r<alert_count){selected=alert_queue[r];show_page(ACTIONS);}else if(r==alert_count){for(int i=0;i<alert_count;i++)if(entries[alert_queue[i]].active)snooze_entry(alert_queue[i]);clear_alerts();schedule_next();return_to(HOME);if(alarm_ok)show_status(T(LK_In_10_Minuten_77b8836e),T(LK_Erneute_Erinnerung_577b9f7b));else show_notice(T(LK_Alarmstatus_b0ff7d4e),3,T(LK_Alarmfehler_Bitte_unter_Einstellungen_erneut__aa2b7c63));}else{clear_alerts();if(completion_count)surface_alerts();else return_to(HOME);}break;
 }
}
static void back(ClickRecognizerRef r,void *ctx){
 (void)r;(void)ctx;
 if(page==HOME){
  if(menu_layer_get_selected_index(menu).row||scroll_layer_get_content_offset(menu_layer_get_scroll_layer(menu)).y){reset_navigation(HOME);return;}
  window_stack_pop(true);return;
 }
 if(page==CLASSES&&cfg.cls<0&&!navigation_depth){window_stack_pop(true);return;}
 if(page==ALERT){clear_alerts();if(completion_count){surface_alerts();return;}}
 if(page==COMPLETE_CONFIRM&&selected_valid())clear_completion(selected);
 return_page();
}

static void menu_up(ClickRecognizerRef r,void *c){(void)r;(void)c;move_menu(true);}
static void menu_down(ClickRecognizerRef r,void *c){(void)r;(void)c;move_menu(false);}
static void move_menu(bool up){
 MenuIndex current=menu_layer_get_selected_index(menu);int count=rows(menu,0,NULL),next=(int)current.row+(up?-1:1);if(next<0||next>=count)return;
 ScrollLayer *scroll=menu_layer_get_scroll_layer(menu);int offset=scroll_layer_get_content_offset(scroll).y,viewport=layer_get_bounds(scroll_layer_get_layer(scroll)).size.h,top=header_height(menu,0,NULL);
 for(int row=0;row<next;row++){MenuIndex index=MenuIndex(0,row);top+=row_height(menu,&index,NULL);}
 MenuIndex index=MenuIndex(0,next);int bottom=top+row_height(menu,&index,NULL);
 MenuRowAlign align=MenuRowAlignNone;if(!next)align=MenuRowAlignBottom;else if(bottom+offset>viewport)align=MenuRowAlignBottom;else if(top+offset<0)align=MenuRowAlignTop;
 menu_layer_set_selected_next(menu,up,align,true);
}

static void menu_select(ClickRecognizerRef r,void *c){(void)r;(void)c;MenuIndex i=menu_layer_get_selected_index(menu);select_row(menu,&i,NULL);}
static void cancel_progress_touch(void){if(progress_hold_timer){app_timer_cancel(progress_hold_timer);progress_hold_timer=NULL;}}
static void progress_touch_timeout(void *context){(void)context;progress_hold_timer=NULL;if(page!=PROGRESS||window_stack_get_top_window()!=window||!progress_can_hold(progress_touch_row))return;progress_counter=progress_touch_row;menu_layer_set_selected_index(menu,MenuIndex(0,progress_counter),MenuRowAlignNone,false);progress_hold_fired=true;show_page(PROGRESS_ACTIONS);}
static void start_progress_touch(int y){if(page!=PROGRESS)return;int content=y-scroll_layer_get_content_offset(menu_layer_get_scroll_layer(menu)).y-header_height(menu,0,NULL);if(content<0)return;for(int row=0;row<7;row++){MenuIndex index=MenuIndex(0,row);int height=row_height(menu,&index,NULL);if(content<height){if(!progress_can_hold(row))return;progress_touch_row=row;progress_hold_timer=app_timer_register(650,progress_touch_timeout,NULL);return;}content-=height;}}
static void menu_hold(ClickRecognizerRef r,void *c){(void)r;(void)c;if(page==PROGRESS){progress_counter=menu_layer_get_selected_index(menu).row;if(progress_can_hold(progress_counter))show_page(PROGRESS_ACTIONS);}else menu_select(NULL,NULL);}
static void menu_clicks(void *ctx){(void)ctx;window_single_click_subscribe(BUTTON_ID_BACK,back);window_single_repeating_click_subscribe(BUTTON_ID_UP,150,menu_up);window_single_repeating_click_subscribe(BUTTON_ID_DOWN,150,menu_down);window_single_click_subscribe(BUTTON_ID_SELECT,menu_select);window_long_click_subscribe(BUTTON_ID_SELECT,650,menu_hold,NULL);}
static void minute_tick(struct tm *t,TimeUnits u){(void)t;(void)u;process_events(true);}
static void init(void){
 store_load();language_pack_init();if(cfg.cls>=0){load_rules();profiles[cfg.cls]=cfg.profile;}
 if(persist_exists(WAKE_KEY))wake_id=persist_read_int(WAKE_KEY);
 if(persist_exists(28))test_at=persist_read_int(28);
 window=window_create();window_set_background_color(window,GColorOxfordBlue);GRect b=GRect(UI_LEFT,UI_TOP,UI_WIDTH,UI_HEIGHT);menu=menu_layer_create(b);menu_layer_pad_bottom_enable(menu,false);menu_layer_set_normal_colors(menu,GColorWhite,GColorOxfordBlue);menu_layer_set_highlight_colors(menu,UI_SELECTION,UI_SELECTION_TEXT);
 menu_layer_set_callbacks(menu,NULL,(MenuLayerCallbacks){.get_num_rows=rows,.get_separator_height=separator_height,.draw_separator=separator_draw,.get_header_height=header_height,.get_cell_height=row_height,.draw_header=header_draw,.draw_row=row_draw});layer_add_child(window_get_root_layer(window),menu_layer_get_layer(menu));window_set_click_config_provider(window,menu_clicks);
 msg_window=window_create();window_set_background_color(msg_window,GColorWhite);msg_scroll=scroll_layer_create(b);scroll_layer_set_shadow_hidden(msg_scroll,true);scroll_layer_set_click_config_onto_window(msg_scroll,msg_window);layer_add_child(window_get_root_layer(msg_window),scroll_layer_get_layer(msg_scroll));msg_text=text_layer_create(GRect(8,5,UI_WIDTH-16,1600));text_layer_set_background_color(msg_text,GColorClear);text_layer_set_text_color(msg_text,GColorOxfordBlue);text_layer_set_font(msg_text,fonts_get_system_font(FONT_KEY_GOTHIC_24));scroll_layer_add_child(msg_scroll,text_layer_get_layer(msg_text));
 info_header=layer_create(GRect(UI_LEFT,UI_TOP,UI_WIDTH,UI_INFO_HEADER));layer_set_update_proc(info_header,info_header_draw);layer_add_child(window_get_root_layer(msg_window),info_header);layer_set_hidden(info_header,true);
 num_window=window_create();window_set_background_color(num_window,GColorOxfordBlue);num_layer=layer_create(b);layer_set_update_proc(num_layer,num_draw);layer_add_child(window_get_root_layer(num_window),num_layer);window_set_click_config_provider(num_window,num_clicks);
 date_window=window_create();window_set_background_color(date_window,GColorOxfordBlue);date_layer=layer_create(b);layer_set_update_proc(date_layer,date_draw);layer_add_child(window_get_root_layer(date_window),date_layer);window_set_click_config_provider(date_window,date_clicks);
 status_window=window_create();window_set_background_color(status_window,GColorOxfordBlue);status_layer=layer_create(b);layer_set_update_proc(status_layer,status_draw);layer_add_child(window_get_root_layer(status_window),status_layer);window_set_touch_bridge_disabled(status_window,true);
 footer_layer=layer_create(GRect(UI_LEFT,UI_TOP+UI_HEIGHT-20,UI_WIDTH,20));layer_set_update_proc(footer_layer,footer_draw);layer_add_child(window_get_root_layer(window),footer_layer);layer_set_hidden(footer_layer,true);
 ui_ready=true;page=cfg.cls<0?CLASSES:HOME;build_list();window_stack_push(window,true);
#if !defined(PBL_PLATFORM_FLINT)
 app_touch_navigation_enable(true);touch_service_subscribe(touch_handler,NULL);
 window_set_touch_bridge_disabled(window,true);window_set_touch_bridge_disabled(num_window,true);window_set_touch_bridge_disabled(date_window,true);window_set_touch_bridge_disabled(msg_window,true);
#endif
 wakeup_service_subscribe(wake_handler);tick_timer_service_subscribe(MINUTE_UNIT,minute_tick);phone_init();process_events(true);
 if(!language_pack_ready()&&!alert_count){language_setup_notice=true;show_notice("Sprache / Language",1,"Bitte Sprache in den Handy-Einstellungen laden.\n\nLoad a language in the phone settings.\n\nTermine und Alarme bleiben gespeichert.");}
 if(storage_error)show_notice(T(LK_Speicherfehler_71eed920),4,T("SPEICHERFEHLER\n\nBitte Uhr-App neu starten. Gespeicherte Daten werden beim Start erneut geladen. Bis dahin keine weiteren Änderungen vornehmen."));
}
static void deinit(void){layer_destroy(info_header);layer_destroy(footer_layer);dismiss_status();layer_destroy(status_layer);window_destroy(status_window);cancel_progress_touch();
#if !defined(PBL_PLATFORM_FLINT)
 touch_service_unsubscribe();app_touch_navigation_enable(false);
#endif
for(int i=0;i<16;i++){if(class_icons[i])gbitmap_destroy(class_icons[i]);}
 layer_destroy(date_layer);window_destroy(date_window);phone_deinit();tick_timer_service_unsubscribe();menu_layer_destroy(menu);text_layer_destroy(msg_text);scroll_layer_destroy(msg_scroll);layer_destroy(num_layer);window_destroy(num_window);window_destroy(msg_window);window_destroy(window);}
int main(void){init();app_event_loop();deinit();}
