# all these imports come from MicroPython. https://docs.micropython.org/en/latest/index.html
from machine import Pin,SPI,PWM
import framebuf
import time

# info on the screen here: https://www.waveshare.com/wiki/Pico-LCD-1.14
# pin numbers. These are the GPIO pin numbers, not the absolute numbers on the board
# backlight
BL = 13
#data/command
DC = 8
# reset
RST = 12
# SPI data input
MOSI = 11
# SPI clock input
SCK = 10
# chip select
CS = 9

# FrameBuffer is a class provided by micropython that allows drawing
class LCD_1inch14(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        # this LCD doesn't seem to use standard forward RGB565.
        # turns out it's BRG565.
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

def unknown_startup():
    # this was in the source example for the LCD but not sure why it's required
    pwm = PWM(Pin(BL))
    pwm.freq(1000)
    pwm.duty_u16(32768)#max 65535 


MAX_5_BIT = (2 ** 5) - 1
MAX_6_BIT = (2 ** 6) - 1
MAX_8_BIT = (2 ** 8) - 1
    
def rgb888_to_brg565(hex_color):
    """
    converts a 24-bit RGB hex (e.g. #FFFFFF colour to the 16bit brg colour used by the waveshare LCD.
    
    hex_color should be a value, like 0x00FF00 or 0b000000001111111100000000. I guess any value form will work if it's >= 0 and <= 2^32 - 1
    """
    
    # get the first 8 bits from the 24 bit value. The left is padded with 0 so no need to mask
    red_8_bit = hex_color >> 16
    # get the second 8 bits from the 24 bit value. The left will have 8 valid bits still so mask
    green_8_bit = (hex_color >> 8) & 0b00000000_11111111
    # get the third 8 bits from the 24 bit value. the left will have 16 valid bits still so mask
    blue_8_bit = hex_color & 0b00000000_00000000_11111111
    
    # debug
    #print(f"R: {red_8_bit}, G: {green_8_bit}, B: {blue_8_bit}")
    
    # map each from 0 to 255 to 0 to whatever their max is
    blue_mapped = round((MAX_5_BIT / MAX_8_BIT) * blue_8_bit)
    red_mapped = round((MAX_6_BIT / MAX_8_BIT) * red_8_bit)
    green_mapped = round((MAX_5_BIT / MAX_8_BIT) * green_8_bit)
    
    # shift them to their bit positions in BRG565 and recombine them
    blue_shifted = blue_mapped << 11
    red_shifted = red_mapped << 5
    # green is already all the way to the right
    
    combined = blue_shifted | red_shifted | green_mapped
    
    return combined
