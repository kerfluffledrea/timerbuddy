import tkinter as tk
import os
import sys
import time
import datetime
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import mixer

mixer.init()
mixer.set_num_channels(3)
mixer.set_reserved(1)

MARGIN = 8
DRAGTHRESHOLD = 8

mod_path = str(str(os.getcwd()))
default_settings={
        'width': 100, 
        'height': 45, 
        'alwaysontop': True,
        'titlebar': False,
        'theme': 'prime',
        'sections': [
            {'name': 'TODO', 'width': 185, 'cards': 4}, 
            {'name': 'IN PROGRESS', 'width': 380, 'cards': 2},
            {'name': 'COMPLETE', 'width': 185, 'cards': 5}
            ], 
        'font': {
            'card': 'Unifont 14', 
            'counter': 'Consolas 10', 
            'header': 'Consolas 12 bold', 
            'timer': 'Unifont 22'}, 
        'customtheme': {
            'bg': 'black', 
            'main': 'magenta', 
            'secondary': 'cyan',
            'tertiary': 'grey25'
            }
        }

SETTINGS = default_settings
WIDTH = SETTINGS['width']
HEIGHT = SETTINGS['height']
FONT = SETTINGS['font']['card']
TIMERFONT = SETTINGS['font']['timer']

GLOBALRELIEF = None
if str(sys.platform).lower() == 'win32' or str(sys.platform).lower() == 'darwin':
    GLOBALRELIEF = tk.RAISED
else:
    GLOBALRELIEF = tk.FLAT

THEMES = dict()
THEMES['custom'] = {
    'name' : 'custom',
    'bg' : SETTINGS['customtheme']['bg'],
    'main' : SETTINGS['customtheme']['main'],
    'secondary' : SETTINGS['customtheme']['secondary'],
    'tertiary' : SETTINGS['customtheme']['tertiary']
    }

THEMES['prime'] = {
    'name' : 'prime',
    'bg' : 'black',
    'main' : '#00ffcc',
    'secondary' : 'magenta',
    'tertiary' : 'yellow'
}

THEMES['fortress'] = {
    'name' : 'fortress',
    'bg' : 'black',
    'main' : 'white',
    'secondary' : 'yellow',
    'tertiary' : '#333333'
}

THEMES['ihaveahax'] = {
    'name' : 'ihaveahax',
    'bg' : '#e2e6f7',
    'main' : '#4c558f',
    'secondary' : '#2e51ed',
    'tertiary' : 'yellow'
}

THEMES['trioptimum'] = {
    'name' : 'trioptimum',
    'bg' : 'black',
    'main' : '#00FF44',
    'secondary' : '#3353FF',
    'tertiary' : 'yellow'
}

THEMES['uplink'] = {
    'name' : 'uplink',
    'bg' : 'black',
    'main' : '#0320aa',
    'secondary' : '#081f6f',
    'tertiary' : 'yellow'
}

THEMES['peach'] = {
    'name' : 'peach',
    'bg' : '#ffC8eD',
    'main' : '#EF1050',
    'secondary' : 'gold',
    'tertiary' : 'blue'
}

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)



# No Touchie
STARTUP_SOUND = mixer.Sound(resource_path("sfx/start.wav"))
ALARM_SOUND = mixer.Sound(resource_path("sfx/alarm.wav"))

# Menu SFX
HOURDONK_SOUND = mixer.Sound(resource_path("sfx/donk.wav"))
TIMERSTART_SOUND = mixer.Sound(resource_path("sfx/starttimer.wav"))
TIMERSTOP_SOUND = mixer.Sound(resource_path("sfx/stoptimer.wav"))
CLICKDOWN_SOUND = mixer.Sound(resource_path("sfx/click.wav"))
CLICKUP_SOUND = mixer.Sound(resource_path("sfx/click.wav"))
RATCHET_SOUND = mixer.Sound(resource_path("sfx/ratchet.wav"))
CLICKFAIL_SOUND = mixer.Sound(resource_path("sfx/clickfail.wav"))

# Screams
WILHELM_SCREAM = mixer.Sound(resource_path("sfx/scream-wilhelm.wav"))

def muteSounds():
    HOURDONK_SOUND.set_volume(0)
    CLICKDOWN_SOUND.set_volume(0)
    CLICKUP_SOUND.set_volume(0)
    CLICKFAIL_SOUND.set_volume(0)
    RATCHET_SOUND.set_volume(0)
    TIMERSTART_SOUND = set_volume(0)
    TIMERSTOP_SOUND = set_volume(0)

def balanceSounds():
    HOURDONK_SOUND.set_volume(0.5)
    CLICKDOWN_SOUND.set_volume(0.2)
    CLICKUP_SOUND.set_volume(0.15)
    CLICKFAIL_SOUND.set_volume(0.5)
    RATCHET_SOUND.set_volume(0.3)
    TIMERSTART_SOUND.set_volume(1)
    TIMERSTOP_SOUND.set_volume(1)

class Timer:
    def __init__(self, theme_name):
        self.root = tk.Tk()
        self.canvas = None
        self.root.resizable(False, False)
        self.root.wm_title("Timer Buddy")
        self.sections = []
        self.cards = []
        self.overflow_cards = []
        self.theme = {}
        self.context_menu = None
        self.middle_click_origin = None
        self.grabbed_card_section = None
        self.control_held = False
        self.lmb_held = False
        self.rmb_held = False
        self.pinned = tk.BooleanVar()
        self.pinned.set(SETTINGS['alwaysontop'])
        self.drag_origin = ()
        self.selected_theme = tk.StringVar(value=theme_name)
        self.updateAlwaysOntop()
        self.setTheme(theme_name)
        self.alarm_flips = 0        
        self.time = datetime.datetime(year=1000,month=1,day=1,hour=0,minute=5,second=0)
        self.timer_started = False
        self.timer_when_full = None
        self.alarm_plays = tk.IntVar()
        self.alarm_plays.set(0)
        self.menu_sfx = tk.BooleanVar()
        self.menu_sfx.set(True)

        # TODO: IDK What to do with this lol
        if os.path.isfile(mod_path+"/icon.png"):
            self.root.iconphoto(False, tk.PhotoImage(file=mod_path+"/icon.png"))

        if not SETTINGS['titlebar']:
            if str(sys.platform).lower() == 'win32':
                self.root.overrideredirect(True)
            else:
                self.root.wm_attributes('-type', 'splash')

        self.root.geometry(str(WIDTH)+"x"+str(HEIGHT))
        self.root.configure(background=self.theme['bg'])
        self.canvas = tk.Canvas(self.root, bg=self.theme['bg'], width=WIDTH, height=HEIGHT, highlightthickness=1, highlightbackground=self.theme['main'])
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.handleClickDown)
        self.canvas.bind('<ButtonRelease-1>', self.handleClickUp)
        self.canvas.bind('<B1-Motion>', self.handleClickDrag)
        self.timer = self.canvas.create_text(WIDTH/2, HEIGHT/2 - 2, text="00:00", font=TIMERFONT, fill=self.theme['main'])
        
        self.progress_line = self.canvas.create_line(MARGIN, HEIGHT-7, WIDTH-MARGIN, HEIGHT-7, fill=self.theme['main'])
        self.elapsed_progress_line = self.canvas.create_line(0, 0, 0, 0, fill=self.theme['tertiary'])
        self.flourish = self.canvas.create_line(WIDTH-MARGIN, 0, WIDTH, MARGIN, fill=self.theme['main'])
        self.hour_lines = []
        for i in range(3):
            self.hour_lines.append(self.canvas.create_line(6+i*5, 1, 6+i*5, 6, fill=self.theme['bg']))

        if sys.platform == 'darwin':
            self.canvas.bind('<Button-2>', self.handleRightClickDown)
            self.canvas.bind('<ButtonRelease-2>', self.handleRightClickUp)
            self.canvas.bind('<ButtonRelease-3>', self.handleMiddleClickUp)
        else:
            self.canvas.bind('<ButtonRelease-2>', self.handleMiddleClickUp)
            self.canvas.bind('<Button-3>', self.handleRightClickDown)
            self.canvas.bind('<ButtonRelease-3>', self.handleRightClickUp)
        self.updateDisplays()
        STARTUP_SOUND.play()

    def destroyContextMenu(self):
        if self.context_menu:
            self.context_menu.destroy()

    def toggleInteractionsMuted(self):
        if self.menu_sfx.get():
            balanceSounds()
        else:
            muteSounds()
    
    def updateAlwaysOntop(self):
        if self.pinned.get() or True: # TODO: Reevaluate this later
            self.root.wm_attributes("-topmost", "true")
            SETTINGS['alwaysontop'] = True
        else:
            self.root.wm_attributes("-topmost", "false")
            SETTINGS['alwaysontop'] = False

    def updateClockDisplay(self):
        self.canvas.itemconfig(self.timer, text=('{:02}:{:02}'.format(self.time.minute, self.time.second)))

    def updateHourDisplay(self):
        old_hour_display = 0
        for i in range(3):
            if self.canvas.itemcget(self.hour_lines[i], 'fill') == self.theme['main']:
                old_hour_display += 1
        for i in range(3):
            self.canvas.itemconfig(self.hour_lines[i], fill=self.theme['bg'])
        for i in range(self.time.hour):
            self.canvas.itemconfig(self.hour_lines[i], fill=self.theme['main'])
        if old_hour_display != self.time.hour:
            mixer.Channel(0).play(HOURDONK_SOUND)

    def updateProgressDisplay(self):
        full_bar_width = WIDTH - MARGIN*2
        if self.timer_started:
            seconds_when_full = self.timer_when_full.hour * 360 + self.timer_when_full.minute * 60 + self.timer_when_full.second
            seconds_remaining = self.time.hour * 360 + self.time.minute * 60 + self.time.second
            self.canvas.itemconfig(self.progress_line, fill=self.theme['secondary'])
            self.canvas.itemconfig(self.elapsed_progress_line, fill=self.theme['tertiary'])
            if seconds_remaining == 0:
                self.canvas.coords(self.progress_line, 0, 0, 0, 0)
                self.canvas.coords(self.elapsed_progress_line, MARGIN, HEIGHT-7, WIDTH-MARGIN, HEIGHT-7)
            else:
                self.canvas.coords(self.progress_line, MARGIN, HEIGHT-7, MARGIN+full_bar_width*(seconds_remaining/seconds_when_full), HEIGHT-7)
                self.canvas.coords(self.elapsed_progress_line, MARGIN+full_bar_width*(seconds_remaining/seconds_when_full),HEIGHT-7, WIDTH-MARGIN, HEIGHT-7)
        else:
            self.canvas.itemconfig(self.progress_line, fill=self.theme['main'])
            self.canvas.coords(self.progress_line, MARGIN, HEIGHT-7, MARGIN+full_bar_width, HEIGHT-7)
            self.canvas.coords(self.elapsed_progress_line, 0,0,0,0)

    def updateDisplays(self):
        self.updateClockDisplay()
        self.updateHourDisplay()
        self.updateProgressDisplay()
    
    def scream(self):
        # TODO: Randomly Select from a Bunch
        WILHELM_SCREAM.play()
    
    # --- Timer Operations ---
    def startTimer(self):
        if (self.time.hour + self.time.minute + self.time.second) > 0:
            TIMERSTART_SOUND.play()
            self.timer_when_full = self.time
            self.timer_started = True
            self.updateDisplays()
            self.tick()

    def stopTimer(self):
        TIMERSTOP_SOUND.play()
        self.timer_when_full = None
        self.timer_started = False
        self.updateDisplays()

    def resetTimer(self):
        ALARM_SOUND.stop()
        self.time = datetime.datetime(year=1000,month=1,day=1,hour=0,minute=5,second=0)
        self.canvas.itemconfig(self.timer, text=('{:02}:{:02}'.format(self.time.minute, self.time.second)))
        self.stopTimer()
        self.updateDisplays()

    def finishTimer(self):
        self.canvas.itemconfig(self.timer, text=('{:02}:{:02}'.format(self.time.minute, self.time.second)))
        mixer.Channel(0).play(ALARM_SOUND, loops=self.alarm_plays.get()) 
        self.stopTimer()
        self.updateDisplays()
        self.alarmColorChange()

    def alarmColorChange(self):
        if self.alarm_flips % 2 == 0:
            self.canvas.config(highlightbackground=self.theme['main'])
            self.canvas.itemconfig(self.flourish, fill=self.theme['main'])
            self.canvas.itemconfig(self.progress_line, fill=self.theme['main'])
            self.canvas.itemconfig(self.timer, fill=self.theme['main'])
        else:
            self.canvas.config(highlightbackground=self.theme['secondary'])
            self.canvas.itemconfig(self.flourish, fill=self.theme['secondary'])
            self.canvas.itemconfig(self.progress_line, fill=self.theme['secondary'])
            self.canvas.itemconfig(self.timer, fill=self.theme['secondary'])

        self.alarm_flips += 1
        if mixer.Channel(0).get_busy():
            self.canvas.after(115, self.alarmColorChange)
        else:
            self.canvas.config(highlightbackground=self.theme['main'])
            self.canvas.itemconfig(self.flourish, fill=self.theme['main'])
            self.canvas.itemconfig(self.progress_line, fill=self.theme['main'])
            self.canvas.itemconfig(self.timer, fill=self.theme['main'])
            self.alarm_flips = 0

    def tick(self):
        if self.timer_started:
            time_delta = datetime.timedelta(seconds=1)
            self.time = self.time-time_delta
            self.canvas.itemconfig(self.timer, text=('{:02}:{:02}'.format(self.time.minute, self.time.second)))
            self.updateDisplays()
            if self.time.hour == 0 and self.time.minute == 0 and self.time.second == 0:
                self.finishTimer()
            else:
                self.canvas.after(930, self.tick)

    # --- Event Handlers ---
    def handleClickDown(self, event):
        if self.timer_started or mixer.Channel(0).get_busy():
            CLICKFAIL_SOUND.play()
        else:
            CLICKDOWN_SOUND.play()
            self.lmb_held = True
        self.drag_origin = (event.x, event.y)
        self.destroyContextMenu()

    def handleClickUp(self, event):
        if not self.timer_started:
            CLICKUP_SOUND.play()
        self.lmb_held = False
        self.canvas.config(cursor='')
        self.drag_origin = None
        for s in self.sections:
            s.setColor(self.theme['bg'])

    def handleClickDrag(self, event):
        if self.drag_origin and self.lmb_held and not self.timer_started:
            x, y = event.x - self.drag_origin[0], event.y - self.drag_origin[1]
            if y < -DRAGTHRESHOLD:
                if self.drag_origin[0] <= WIDTH / 2:
                    self.time = self.time + datetime.timedelta(minutes=1)
                    self.drag_origin = (self.drag_origin[0], self.drag_origin[1]-DRAGTHRESHOLD)
                    RATCHET_SOUND.play()
                else:
                    self.time = self.time + datetime.timedelta(seconds=1)
                    self.drag_origin = (self.drag_origin[0], self.drag_origin[1]-DRAGTHRESHOLD)
                    RATCHET_SOUND.play()
            if y > DRAGTHRESHOLD:
                if self.drag_origin[0] <= WIDTH / 2 and (self.time.hour > 0 or self.time.minute > 0):
                    self.time = self.time - datetime.timedelta(minutes=1)
                    self.drag_origin = (self.drag_origin[0], self.drag_origin[1]+DRAGTHRESHOLD)
                    RATCHET_SOUND.play()
                elif self.drag_origin[0] > WIDTH / 2 and (self.time.second > 0):
                    self.time = self.time - datetime.timedelta(seconds=1)
                    self.drag_origin = (self.drag_origin[0], self.drag_origin[1]+DRAGTHRESHOLD)
                    RATCHET_SOUND.play()
            if self.time.hour > 3:
                self.time = datetime.datetime(1000, 1, 1, 0, self.time.minute, self.time.second)
            else:
                self.time = datetime.datetime(1000, 1, 1, self.time.hour, self.time.minute, self.time.second)
            self.canvas.itemconfig(self.timer, text=('{:02}:{:02}'.format(self.time.minute, self.time.second)))
            self.updateDisplays()

    def handleMiddleClickUp(self, event):
        if self.timer_started:
            self.stopTimer()
        elif mixer.Channel(0).get_busy():
            ALARM_SOUND.stop()
        else:
            self.startTimer()

    def handleRightClickDown(self, event):
        self.rmb_held = True
        self.destroyContextMenu()

    def handleRightClickUp(self, event):
        self.rmb_held = False
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.theme['bg'], fg=self.theme['secondary'], selectcolor=self.theme['secondary'], font=FONT)
        themes_menu = tk.Menu(self.context_menu, tearoff=0, bg=self.theme['bg'], fg=self.theme['secondary'], selectcolor=self.theme['secondary'], font=FONT)
        themes_menu.add_radiobutton(label="Kerfluffle", variable=self.selected_theme, value='prime', command=lambda: self.setTheme('prime'))
        themes_menu.add_radiobutton(label="Tri.Optimum", variable=self.selected_theme, value='trioptimum', command=lambda: self.setTheme('trioptimum'))
        themes_menu.add_radiobutton(label="Fortress", variable=self.selected_theme, value='fortress', command=lambda: self.setTheme('fortress'))
        themes_menu.add_radiobutton(label="Peachy", variable=self.selected_theme, value='peach', command=lambda: self.setTheme('peach'))
        themes_menu.add_radiobutton(label="ihaveahax", variable=self.selected_theme, value='ihaveahax', command=lambda: self.setTheme('ihaveahax'))
        themes_menu.add_radiobutton(label="Custom", variable=self.selected_theme, value='custom', command=lambda: self.setTheme('custom'))
        
        alarm_plays_menu = tk.Menu(self.context_menu, tearoff=0, bg=self.theme['bg'], fg=self.theme['secondary'], selectcolor=self.theme['secondary'], font=FONT)
        alarm_plays_menu.add_radiobutton(label="Once", variable=self.alarm_plays, value=0)
        alarm_plays_menu.add_radiobutton(label="Twice", variable=self.alarm_plays, value=1)
        alarm_plays_menu.add_radiobutton(label="Thrice", variable=self.alarm_plays, value=2)
        alarm_plays_menu.add_radiobutton(label="99999999ice", variable=self.alarm_plays, value=99999999)

        if self.timer_started:
            self.context_menu.add_command(label="Stop Timer", command=lambda: self.stopTimer())
        else:
            self.context_menu.add_command(label="Start Timer", command=lambda: self.startTimer())
        self.context_menu.add_command(label="Reset Timer", command=lambda: self.resetTimer())
        self.context_menu.add_separator()
        self.context_menu.add_cascade(label="Play Alarm...", menu=alarm_plays_menu)
        self.context_menu.add_cascade(label="Theme...", menu=themes_menu)
        self.context_menu.add_checkbutton(label="Menu SFX", variable=self.menu_sfx, onvalue=1, offvalue=0, command=lambda: self.toggleInteractionsMuted())
        self.context_menu.add_command(label="Scream", command=lambda: self.scream())
        self.context_menu.add_command(label="Quit", command=lambda: sys.exit())
        self.context_menu.post(event.x_root, event.y_root)
    
    def setTheme(self, theme):
        self.selected_theme.set(theme)
        self.theme['name'] = theme
        self.theme['bg'] = THEMES[theme]['bg']
        self.theme['main'] = THEMES[theme]['main']
        self.theme['secondary'] = THEMES[theme]['secondary']
        self.theme['tertiary'] = THEMES[theme]['tertiary']
        if self.canvas:
            self.canvas.config(self.canvas, highlightbackground=self.theme['main'], bg=self.theme['bg'])
            self.canvas.itemconfig(self.timer, fill=self.theme['main'])
            self.canvas.itemconfig(self.flourish, fill=self.theme['main'])
            self.updateDisplays()
        SETTINGS['theme'] = self.theme['name']

balanceSounds()
t = Timer(SETTINGS['theme'])
t.root.mainloop()
