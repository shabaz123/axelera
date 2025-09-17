/***************************************
* LCD I2C 16x2 Display Driver
* rev 1 - shabaz - July 2025
****************************************/

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/i2c.h"
#include "lcd_i2c_16x2.h"


// global variables
i2c_inst_t *i2c_port;
uint8_t function_flags;
uint8_t control_flags;

void i2c_setup(void) {
    if (I2C_PORT_SELECTED == 0) {
        i2c_port = &i2c0_inst;
    } else {
        i2c_port = &i2c1_inst;
    }
    i2c_init(i2c_port, 100 * 1000);
    gpio_set_function(I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(I2C_SDA_PIN);
    gpio_pull_up(I2C_SCL_PIN);
}

void lcd_command(uint8_t cmd) {
    uint8_t data[2];
    data[0] = 0x80;
    data[1] = cmd;
    i2c_write_blocking(i2c_port, LCD_ADDRESS, data, sizeof(data), false);
}

void lcd_write_data(uint8_t data) {
    uint8_t buffer[2];
    buffer[0] = 0x40;
    buffer[1] = data;
    i2c_write_blocking(i2c_port, LCD_ADDRESS, buffer, sizeof(buffer), false);
}

void rgb_set_register(uint8_t reg, uint8_t value) {
    uint8_t data[2];
    data[0] = reg;
    data[1] = value;
    i2c_write_blocking(i2c_port, RGB_ADDRESS, data, sizeof(data), false);
}

void set_rgb(uint8_t red, uint8_t green, uint8_t blue) {
    rgb_set_register(REG_RED, red);
    rgb_set_register(REG_GREEN, green);
    rgb_set_register(REG_BLUE, blue);
}

void set_rgb_white(void) {
    set_rgb(0xFF, 0xFF, 0xFF); // set backlight to white
}

void lcd_set_cursor(uint8_t row, uint8_t col) {
    uint8_t address;
    if (row == 0) {
        address = 0x80 + col; // first row
    } else {
        address = 0xC0 + col; // second row
    }
    lcd_command(address);
}

void lcd_clear(void) {
    lcd_command(LCD_CLEARDISPLAY);
    sleep_ms(2); // wait for the command to complete
}

void lcd_clear_line(uint8_t row) {
    lcd_set_cursor(row, 0);
    for (int i = 0; i < 16; i++) {
        lcd_write_data(' ');
    }
    lcd_set_cursor(row, 0);
}

void lcd_print(const char *str) {
    int num = 0;
    while (*str) {
        lcd_write_data(*str++);
        num++;
        if (num >= 16) { // limit to 16 characters per line
            break;
        }
    }
}

void lcd_display_on(void) {
    lcd_command(LCD_DISPLAYCONTROL | control_flags | LCD_DISPLAYON);
}

void pwm_set_register(uint8_t reg, uint8_t value) {
    uint8_t data[2];
    data[0] = reg;
    data[1] = value;
    i2c_write_blocking(i2c_port, SN3193_IIC_ADDRESS, data, sizeof(data), false);
}

void pwm_set_brightness(uint8_t brightness) {
#ifdef PWM_BACKLIGHT
    pwm_set_register(PWM_1_REG, brightness);
    sleep_ms(1);
    pwm_set_register(PWM_UPDATE_REG, 0x00);
#else
    printf("PWM_BACKLIGHT not defined, cannot set brightness.\n");
#endif
}

void pwm_set_mode(uint8_t mode) {
    uint8_t reg_value = (mode == LED_BREATH_MODE) ? LED_BREATH_MODE : LED_NORNAL_MODE;
    pwm_set_register(LED_MODE_REG, reg_value);
}

void lcd_init(void) {
    function_flags = LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS;
    control_flags = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF;

    lcd_command(LCD_FUNCTIONSET | function_flags);
    sleep_ms(5);
    lcd_command(LCD_FUNCTIONSET | function_flags);
    sleep_ms(5);
    lcd_command(LCD_FUNCTIONSET | function_flags);
    sleep_ms(5);
    lcd_command(LCD_FUNCTIONSET | function_flags);
    lcd_display_on();
    lcd_clear();
    lcd_command(LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT);
    sleep_ms(20); // just in case
    // backlight init
#ifdef RGB_BACKLIGHT
    rgb_set_register(REG_MODE1, 0x00);
    rgb_set_register(REG_OUTPUT, 0xFF);
    rgb_set_register(REG_MODE2, 0x20);
    set_rgb_white(); // set backlight to white
#endif
#ifdef PWM_BACKLIGHT
    pwm_set_register(SHUTDOWN_REG, 0x20);
    pwm_set_register(LED_MODE_REG, LED_NORNAL_MODE);
    pwm_set_register(CURRENT_SETTING_REG, 0x00);
    sleep_ms(1);
    pwm_set_register(PWM_1_REG, 0xFF);
    sleep_ms(1);
    pwm_set_register(PWM_UPDATE_REG, 0x00);
    pwm_set_register(T0_1_REG, 0x40);
    pwm_set_register(T0_2_REG, 0x40);
    pwm_set_register(T0_3_REG, 0x40);
    sleep_ms(1);
    pwm_set_register(T1T2_1_REG, 0x26);
    pwm_set_register(T1T2_2_REG, 0x26);
    pwm_set_register(T1T2_3_REG, 0x26);
    sleep_ms(1);
    pwm_set_register(T3T4_1_REG, 0x26);
    pwm_set_register(T3T4_2_REG, 0x26);
    pwm_set_register(T3T4_3_REG, 0x26);
    sleep_ms(1);
    pwm_set_register(LED_CONTROL_REG, 0x01);
    pwm_set_register(TIME_UPDATE_REG, 0x00);
    sleep_ms(1);
    pwm_set_mode(LED_NORNAL_MODE);
#endif
}
