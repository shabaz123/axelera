#ifndef LCD_I2C_16X2_HEADER_FILE_
#define LCD_I2C_16X2_HEADER_FILE_

// I2C port defines
#define I2C_PORT_SELECTED 1
#define I2C_SDA_PIN 14
#define I2C_SCL_PIN 15

// backlight defines
// Uncomment the following line if you have the RGB backlight model
// #define RGB_BACKLIGHT
// uncomment the following line for SN3193 based backlight control
#define PWM_BACKLIGHT

#define LCD_ADDRESS   (0x7c>>1)
// used with the RGB backlight model:
#define RGB_ADDRESS   (0xc0>>1)
// used with non-RGB models with brightness control:
#define SN3193_IIC_ADDRESS 0x6B

#define LINE_0 0
#define LINE_1 1

#define REG_RED        0x04
#define REG_GREEN      0x03
#define REG_BLUE       0x02
#define REG_MODE1      0x00
#define REG_MODE2      0x01
#define REG_OUTPUT     0x08
#define LCD_CLEARDISPLAY 0x01
#define LCD_RETURNHOME 0x02
#define LCD_ENTRYMODESET 0x04
#define LCD_DISPLAYCONTROL 0x08
#define LCD_CURSORSHIFT 0x10
#define LCD_FUNCTIONSET 0x20
#define LCD_SETCGRAMADDR 0x40
#define LCD_SETDDRAMADDR 0x80

#define LCD_ENTRYRIGHT 0x00
#define LCD_ENTRYLEFT 0x02
#define LCD_ENTRYSHIFTINCREMENT 0x01
#define LCD_ENTRYSHIFTDECREMENT 0x00

#define LCD_DISPLAYON 0x04
#define LCD_DISPLAYOFF 0x00
#define LCD_CURSORON 0x02
#define LCD_CURSOROFF 0x00
#define LCD_BLINKON 0x01
#define LCD_BLINKOFF 0x00

#define LCD_DISPLAYMOVE 0x08
#define LCD_CURSORMOVE 0x00
#define LCD_MOVERIGHT 0x04
#define LCD_MOVELEFT 0x00

#define LCD_8BITMODE 0x10
#define LCD_4BITMODE 0x00
#define LCD_2LINE 0x08
#define LCD_1LINE 0x00
#define LCD_5x8DOTS 0x00

// SN3193 Register definitions
#define SHUTDOWN_REG 0x00
#define BREATING_CONTROL_REG 0x01
#define LED_MODE_REG 0x02
#define LED_NORNAL_MODE 0x00
#define LED_BREATH_MODE 0x20

#define CURRENT_SETTING_REG 0x03
#define PWM_1_REG 0x04
#define PWM_2_REG 0x05
#define PWM_3_REG 0x06
#define PWM_UPDATE_REG 0x07

#define T0_1_REG 0x0A
#define T0_2_REG 0x0B
#define T0_3_REG 0x0C

#define T1T2_1_REG 0x10
#define T1T2_2_REG 0x11
#define T1T2_3_REG 0x12

#define T3T4_1_REG 0x16
#define T3T4_2_REG 0x17
#define T3T4_3_REG 0x18

#define TIME_UPDATE_REG 0x1C
#define LED_CONTROL_REG 0x1D
#define RESET_REG 0x2F


void i2c_setup(void);
void lcd_init(void);
void set_rgb(uint8_t red, uint8_t green, uint8_t blue);
void set_rgb_white(void);
void lcd_set_cursor(uint8_t row, uint8_t col);
void lcd_clear(void);
void lcd_clear_line(uint8_t row); // clear a row and move cursor to beginning of it
void lcd_print(const char *str);
void lcd_display_on(void);
void pwm_set_brightness(uint8_t brightness);
void pwm_set_mode(uint8_t mode); // normal mode is LED_NORMAL_MODE


#endif // LCD_I2C_16X2_HEADER_FILE_
