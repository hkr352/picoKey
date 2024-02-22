import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction
import time
import displayio
import terminalio
import busio
import alarm
import neopixel
from adafruit_led_animation.animation.rainbowcomet import RainbowComet


# can try import bitmap_label below for alternative
from adafruit_display_text import label
import adafruit_displayio_sh1107

from kmk.modules import Module

# position = potknob.value  # 0-65535の範囲の値
# pos = potknob.value // 256  # 0-255の範囲にする


class Batdisplay(Module):

    '''
    Modules differ from extensions in that they not only can read the state, but
    are allowed to modify the state. The will be loaded on boot, and are not
    allowed to be unloaded as they are required to continue functioning in a
    consistant manner.
    '''

    def __init__(self, pin=board.A2):
        self.clac_buf = ""
        self.mode = 0
        self.batV = AnalogIn(pin) #GP28
        self.sleep_time = 0
        # print(self.batV.value)

        self.pixels = neopixel.NeoPixel(board.GP22, 19, brightness=0.1)
        self.rainbow_comet = RainbowComet(self.pixels, speed=0.1, tail_length=19, bounce=True)

        SCL=board.GP5
        SDA=board.GP4
        self.brd_LED = DigitalInOut(board.LED) #(board.GP0)
        self.brd_LED.direction = Direction.OUTPUT
        self.brd_LED.value = True

        try:
            i2c = busio.I2C(SCL, SDA)
        except:
            displayio.release_displays()
            i2c = busio.I2C(SCL, SDA)

        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        # displayio.re

        # SH1107 is vertically oriented 64x128
        self.WIDTH = 128
        self.HEIGHT = 64
        self.BORDER = 1

        self.display = adafruit_displayio_sh1107.SH1107(
            display_bus, width=self.WIDTH, height=self.HEIGHT, rotation=0
        )

        # self.display.auto_refresh = False
        # https://learn.adafruit.com/circuitpython-display_text-library/label-placement

        # Make the display context
        self.splash = displayio.Group()
        self.display.show(self.splash)
        

        # white back
        color_bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF  # White
        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
        self.splash.append(bg_sprite)

        # Draw a smaller inner rectangle in black
        inner_bitmap = displayio.Bitmap(self.WIDTH - self.BORDER * 2, self.HEIGHT - self.BORDER * 2, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = displayio.TileGrid(
            inner_bitmap, pixel_shader=inner_palette, x=self.BORDER, y=self.BORDER)
        self.splash.append(inner_sprite)

        self.bat_aria = label.Label(
            terminalio.FONT, text="3.3V", color=0xFFFFFF)
        self.bat_aria.anchor_point = (1.0, 0.5)
        self.bat_aria.anchored_position = (self.WIDTH - 8, 8)
        self.splash.append(self.bat_aria)

        self.mode_label = label.Label(
            terminalio.FONT, text="mode A", color=0xFFFFFF)
        self.mode_label.anchor_point = (0.0, 0.5)
        self.mode_label.anchored_position = (8, 8)
        self.splash.append(self.mode_label)

    
        self.clac_aria = label.Label(terminalio.FONT, text="0", scale=2, color=0xFFFFFF)
        self.clac_aria.anchor_point = (1.0, 1.0)
        self.clac_aria.anchored_position = (self.WIDTH - self.BORDER, self.HEIGHT - self.BORDER)
        self.splash.append(self.clac_aria)

        # self.display.refresh()

        self.tickTime = time.monotonic()
        self.sleep_time = time.monotonic()

    def draw_text_2(self, value):
        # text2 = str(value) # "SH1107"
        # text2 = str(format(value, '.2f')) 
        text2 = str(round(value, 2))
        # text2 = "{:.2f}".format(value)
        # text2 = "{:.d}".format( int( value) )
        
        self.text_area2.text = text2
    
    def get_state(self):
        if time.monotonic() - self.tickTime > 1:
            # 3.3 / 65535 = 0.00005
            neko = (0.00005 * self.batV.value) * 3
            # neko = self.batV.value
            # print(neko)
            self.bat_aria.text = str(round(neko, 2)) + "V"

            self.tickTime = time.monotonic()
            # print(time.monotonic())
            self.brd_LED.value = not self.brd_LED.value
            # print(str(self.brd_LED.value)) 
        
        return
    
    # The below methods should be implemented by subclasses

    def during_bootup(self, keyboard):
        # try:
        #     i2c = busio.I2C(keyboard.SCL, keyboard.SDA)
        # except:
        #     displayio.release_displays()
        #     i2c = busio.I2C(keyboard.SCL, keyboard.SDA)

        # self.display = adafruit_displayio_sh1107.SH1107(
        #     displayio.I2CDisplay(i2c, device_address=0x3C),
        #     width=self.WIDTH,
        #     height=self.HEIGHT,
        #     rotation=0
        # )
        # self.display.auto_refresh = False
        
        return
        
    def before_matrix_scan(self, keyboard):
        '''
        Return value will be injected as an extra matrix update
        '''
        self.rainbow_comet.animate()

        # self.draw_text_2 (self.get_state())
        self.get_state()
        if time.monotonic() - self.sleep_time > 60:
            self.mode_label.text = "mode Sleep"
            self.display.sleep()
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            # pin_alarm = alarm.pin.PinAlarm(pin=board.GP11, value=True)
            pin_alarm = alarm.pin.PinAlarm(pin=board.GP6, value=False, pull=True)
            alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
            self.sleep_time = time.monotonic()
        return keyboard

    def after_matrix_scan(self, keyboard):
        '''
        Return value will be replace matrix update if supplied
        '''
        return

    def process_key(self, keyboard, key, is_pressed, int_coord):
        self.sleep_time = time.monotonic() # sleep time reset

        if is_pressed:
            # print(int_coord)
            # print(key.code)
            if int_coord == 19: #0:
                self.mode_label.text = "mode A"
                self.mode = 0
                return key
            elif int_coord == 20: #1:
                self.mode_label.text = "mode B"
                self.mode = 1
                return key
            elif int_coord == 21: #2:
                self.mode_label.text = "mode C"
                self.mode = 2
                return key

            # led [int_coord] = 1
            if key.code == 42:
                # self.clac_aria.text
                self.clac_buf= self.clac_buf[:-1]
                if self.clac_buf == "":
                    self.clac_buf = "0"

            elif key.code == 84:
                self.clac_buf += "/"
                # self.clac_aria.text = self.clac_buf
            elif key.code == 85:
                self.clac_buf +="*"
                # self.clac_aria.text = self.clac_buf
            elif key.code == 86:
                self.clac_buf +="-"
                # self.clac_aria.text = self.clac_buf
            elif key.code == 87:
                self.clac_buf +="+"
                # self.clac_aria.text = self.clac_buf
            elif key.code == 88:
                # self.clac_buf +="*"
                self.clac_buf = str( eval(self.clac_buf) )
                # self.clac_aria.text = str( eval(self.clac_aria.text) )
                # self.clac_aria.text = self.clac_buf

            elif 99 >= key.code and key.code >= 89:
                if 97 >= key.code and key.code >= 89:
                    _clac_buf = str(key.code - 88) # 1~9
                elif key.code == 98:
                    _clac_buf ="0"
                elif key.code == 99:
                    _clac_buf ="."
                else :
                    self.clac_buf = "0"
                    # self.clac_aria.text = str(self.clac_buf)
                    # return key

                # 0の時、代入して0をけす
                if self.clac_buf == "0":
                    self.clac_buf = _clac_buf
                else:
                    self.clac_buf += _clac_buf
            else:
                self.clac_buf = "0"

            # print(self.clac_buf)
            self.clac_aria.text = str(self.clac_buf)
            # print(key.code) # key number?
            # print(self.keymap[[0,int_coord]])
            # print(int_coord)

        # if ispressd = press :
            # led [int_coord] = 1
        # else :
            # led [int_coord] = 0
            # 電卓モード時にキー送信無しにしたい
            # if self.mode == 2:
                # key.code = 1006 # 1006ってなに
                
        return key

    def before_hid_send(self, keyboard):
        return
    
    def after_hid_send(self, keyboard):
        return

    def on_powersave_enable(self, keyboard):
        return

    def on_powersave_disable(self, keyboard):
        return

    def deinit(self, keyboard):
        pass
