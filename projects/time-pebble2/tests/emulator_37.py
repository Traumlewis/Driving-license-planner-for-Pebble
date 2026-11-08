"""Real Emery: standard lesson cell height and nested menu return locations."""
exec(open('/workspace/fahrschul-planer/tests/emulator_protocol.py').read().split("state=request({1:0")[0])
import subprocess,png
from libpebble2.services.screenshot import Screenshot
from libpebble2.protocol.apps import AppRunState,AppRunStateStart,AppRunStateStop
def click(name,n=1,duration=180):
 if n:subprocess.run(['/workspace/bin/pebble','emu-button','--emulator','emery','click',name,'--duration',str(duration),'--repeat',str(n),'--interval','180'],check=True,capture_output=True);time.sleep(.3)
def shot(name):
 time.sleep(.7);data=Screenshot(pebble).grab_image();png.from_array(data,mode='RGB;8').save('/workspace/artifacts/'+name);return data
def same_menu(a,b):assert a[80:]==b[80:] # ignore a changing countdown in the header
pebble.send_packet(AppRunState(command=2,data=AppRunStateStop(uuid=app)));time.sleep(.7)
pebble.send_packet(AppRunState(command=1,data=AppRunStateStart(uuid=app)));time.sleep(1)
before=request({1:0,2:0})['state'];assert before['language']==0
home=shot('v3.7-home.png');click('down');all_selected=shot('v3.7-home-all-selected.png')
click('select');list_new=shot('v3.7-list-new.png');click('select');shot('v3.7-plan.png');click('select');kinds=shot('v3.7-lesson-types.png')
assert list(kinds[81][:3])==[0,0,85] and list(kinds[82][:3])==[255,255,255] # header 34 + standard 48-pixel first row
click('down',5);click('select');click('down',6);edit_topic=shot('v3.7-edit-topic-selected.png')
click('select');click('down',5);click('back');edit_return=shot('v3.7-edit-topic-return.png');same_menu(edit_topic,edit_return)
click('back');list_return=shot('v3.7-list-new-return.png');same_menu(list_new,list_return)
click('back');home_return=shot('v3.7-home-all-return.png');same_menu(all_selected,home_return)
click('back');home_top=shot('v3.7-home-top-return.png');assert home_top[:34]==home[:34]
# The long-OK submenu returns to the same required-lessons counter and scroll position.
click('down',3);click('select');click('down',4);progress=shot('v3.7-progress-selected.png');click('select',duration=850);click('back');progress_return=shot('v3.7-progress-return.png');same_menu(progress,progress_return)
click('back');click('back') # home at Required lessons, then the home anchor
# An appointment and its delete confirmation each preserve their own parent selection.
if before['entries']:
 click('down');click('select');click('down');appointment_list=shot('v3.7-list-appointment-selected.png');click('select');click('down',4);delete_selected=shot('v3.7-actions-delete-selected.png')
 click('select');click('back');delete_return=shot('v3.7-actions-delete-return.png');same_menu(delete_selected,delete_return)
 click('back');appointment_return=shot('v3.7-list-appointment-return.png');same_menu(appointment_list,appointment_return)
 click('back');click('back')
after=request({1:0,2:0})['state'];assert after['entries']==before['entries'] and after['counts']==before['counts'] and after['topics']==before['topics']
assert after['alarmOk'] and after['storageOk']
print('PASS Emery 3.7: 48-pixel lesson cells; nested topic/edit/list/home return selection and scroll match; second home Back returns to top; long-OK and delete confirmation restore parents; data unchanged')
service.shutdown()
