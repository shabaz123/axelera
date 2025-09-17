// ****************************************************************
// *  main.cpp for Axelera demo
// *  rev 1 - shabaz - July 2025
// ****************************************************************

#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "lcd_i2c_16x2.h"
#include "uart_handler.h"

#define FOREVER 1
#define BOARD_LED_PIN 25
#define BOARD_LED_ON gpio_put(BOARD_LED_PIN, 1)
#define BOARD_LED_OFF gpio_put(BOARD_LED_PIN, 0)

void board_init(void) {
    stdio_init_all();
    gpio_init(BOARD_LED_PIN);
    gpio_set_dir(BOARD_LED_PIN, GPIO_OUT);
    // blink the board LED 5 times, allows the user
    // time to connect up the USB serial terminal if desired
    for (int i = 0; i < 5; i++) {
        BOARD_LED_ON;
        sleep_ms(200);
        BOARD_LED_OFF;
        sleep_ms(400);
    }
    i2c_setup();
    init_uart();
    lcd_init();
    pwm_set_brightness(100); // applies for non-RGB backlights
    printf("*** Axelera ANPR-for-All ***\n");
    lcd_set_cursor(LINE_0, 0);
    lcd_print("Axelera ANPR4All");
}

int main(void)
{
    board_init();
    uart_int_start(); // start UART interrupt handler

    while(FOREVER) {
        // rx_complete_length is non-zero only if
        // a \n terminated string is received over UART
        if (rx_complete_length > 0) {
            printf("Received: %s\n", uart_buffer);
            if (strncmp((const char*)uart_buffer, "LED_ON", 6) == 0) {
                BOARD_LED_ON; // turn on the board LED
            } else if (strncmp((const char*)uart_buffer, "LED_OFF", 7) == 0) {
                BOARD_LED_OFF; // turn off the board LED
            }
            lcd_clear_line(LINE_1);
            lcd_print((const char*)uart_buffer); // display the received message on LCD
            uart_clear_rx_buffer(); // clear the message from the buffer
        }
        sleep_ms(10);
    }

    // never reached
    uart_int_stop(); // warning on this line is ok
    return (0);
}
