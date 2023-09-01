import sys
import os
import plyer
import time
import pyttsx3
import shutil
import subprocess

USER = os.getlogin()
TITLE = 'Battery Health Alert'
APPNAME = 'i3Health'
CHARGE_COMPLETE_MESSAGE = 'Battery charging complete'
SHORT_SLEEP = 1.3
LONG_SLEEP = 47
LOW_BATTERY_ICON_PATH = './icons/low-battery.ico' if 'win' in sys.platform else ''
BATTERY_OK_ICON_PATH = './icons/battery-ok.ico' if 'win' in sys.platform else ''
FILE_NAME = sys.executable
NEW_REG_ENTRY = "i3_Health"

battery_percentage = 0
notification = 0
charging = True


def check_battery():
    global battery_percentage
    global charging

    # get the current battery percentage and charging state
    battery_percentage = plyer.battery.get_state()['percentage']
    charging = plyer.battery.get_state()['isCharging']

def create_persistence():
    APP_DATA_FOLDER = os.environ["AppData"]
    FINAL_PATH = os.path.join(APP_DATA_FOLDER, "i3_Health.exe")

    # copy the app to the temp data folder if it is not there
    if not os.path.exists(FINAL_PATH):
        shutil.copy(FILE_NAME, FINAL_PATH)


        # delete the key in the registry editor that points to the app
        subprocess.call("reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run\ /v i3_Health /f", shell=True)

        # # adding a registry to the registry editor that points to the app
        subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v ' + NEW_REG_ENTRY + ' /t REG_SZ /d "' + FINAL_PATH + '"', shell=True)

    return True
    

def alert_user():
    # global allows changing a variable within a func
    # keep track of notifications to avoid creating multiple notifications if one already exists
    global notification
    try:
        init_speaker = pyttsx3.init()

        # get voices installed
        voices = init_speaker.getProperty('voices')

        try:
            # try to set last voice
            init_speaker.setProperty('voice', voices[-1].id)
        except:
            # set to default first voice
            init_speaker.setProperty('voice', voices[0].id)

        # call the other function that checks for percentage & charging & assigns sets the necessary vars
        check_battery()
        if battery_percentage in range(37):

            # check if the current battery percentage is < 37 and the the battery is not charging
            if charging == False:
                if notification < 1:
                    plyer.notification.notify(
                    	title=TITLE, 
                    	message=f'Gomen {USER} chan, please plug in your battery to avoid disturbances', 
                    	app_name=APPNAME, 
                    	app_icon=LOW_BATTERY_ICON_PATH, 
                    	ticker=APPNAME,
                    	timeout=15, 
                    	toast=True)
                    time.sleep(SHORT_SLEEP)
                    init_speaker.say(f'Pardon my intrusion but, your battery is at {battery_percentage} percent')
                    init_speaker.runAndWait()
                    time.sleep(30)
                    notification += 1
                else:
                    init_speaker.say(f'Pardon my intrusion but, your battery is at {battery_percentage} percent')
                    init_speaker.runAndWait()

                    # time to be idle before sending next notification
                    time.sleep(LONG_SLEEP)

        elif battery_percentage == 100:
            if charging == False:
                if notification < 1:
                    plyer.notification.notify(
                    	title=TITLE, 
                    	message=f'Ohayou {USER} chan, battery charging complete!', 
                    	app_name=APPNAME, 
                    	app_icon=BATTERY_OK_ICON_PATH, 
                    	ticker=APPNAME,
                    	timeout=15,
                    	toast=True)
                    time.sleep(SHORT_SLEEP)
                    init_speaker.say(CHARGE_COMPLETE_MESSAGE)
                    init_speaker.runAndWait()
                    notification += 1

                    # time to be idle before sending next notification
                    time.sleep(LONG_SLEEP)
                else:
                    init_speaker.say(CHARGE_COMPLETE_MESSAGE)
                    init_speaker.runAndWait()

                    # time to be idle before sending next notification
                    time.sleep(45)

        else:
            time.sleep(2)
            alert_user()

    except KeyboardInterrupt:
        print(' QUITTING SESSION ')
        sys.exit()

    except Exception as error:
        print(error)
        sys.exit(1)

# run the main function as long there is a logged in user
while USER != None:
    if 'win' in sys.platform:
        if create_persistence():
            alert_user()
    else:
        plyer.notification.notify(
            title=TITLE, 
            message=f'Gomen {USER} chan, this code has only been tested on Windows systems.', 
            app_name=APPNAME, 
            app_icon=LOW_BATTERY_ICON_PATH, 
            ticker=APPNAME,
            timeout=5, 
            toast=True
            )
        sys.exit(1)
