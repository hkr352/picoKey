import board
from digitalio import DigitalInOut, Pull
from bat_display import Batdisplay

from kmk.extensions.rgb import AnimationModes
from kb import KMKKeyboard

# from kmk.extensions.LED import LED
from kmk.extensions.lock_status import LockStatus
from kmk.keys import KC
from kmk.modules.layers import Layers

Pico14 = KMKKeyboard()
Pico14.modules.append(Layers())

mode_bug = True

def mode_a(*args):
    return

NEKO_KEY = KC.NO.clone()
NEKO_KEY.after_press_handler(mode_a)

______ = KC.TRNS
XXXXXX = KC.NO

Pico14.keymap = [[
  # Layer 0 QWERTY
    KC.ESCAPE,  KC.NUMPAD_SLASH, KC.NUMPAD_ASTERISK, KC.BSPACE,
    KC.NUMPAD_7, KC.NUMPAD_8,     KC.NUMPAD_9,        KC.KP_MINUS,
    KC.NUMPAD_4, KC.NUMPAD_5,     KC.NUMPAD_6,        KC.KP_PLUS,
    KC.NUMPAD_1, KC.NUMPAD_2,     KC.NUMPAD_3,        KC.KP_ENTER,
    KC.NUMPAD_0, KC.NUMLOCK,       KC.NUMPAD_DOT,      #XXXXXX,
    NEKO_KEY,    KC.PS_TOG,        NEKO_KEY,
  ], [
  # Layer 1
    ______,      ______,          ______,   KC.TRNS,
    KC.HOME,     KC.UP,           KC.PGUP,  KC.TRNS,
    KC.LEFT,     ______,          KC.RIGHT, KC.TRNS,
    KC.END,      KC.DOWN,         KC.PGDN,  KC.TRNS,
    KC.RGB_MODE_RAINBOW,  KC.RGB_TOG,   KC.DEL,
    KC.TRNS,     KC.TRNS,         KC.TRNS,
  ]
]


if __name__ == '__main__':
    batdispley = Batdisplay()
    Pico14.modules.append(batdispley)
    Pico14._init()

    try:
        while True:
            Pico14._main_loop()
    finally:
        Pico14._deinit_hid()
        Pico14.deinit()