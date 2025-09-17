/******************************************
 * uart_handler.cpp
 * rev 1 - shabaz - July 2025
 * ****************************************/

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/uart.h"
#include "hardware/irq.h"
#include "uart_handler.h"

// defines
#define UART_TICK_PERIOD_US 100000

//************* global variables *************
uint8_t uart_buffer[UART_IN_BUF_SIZE+5];
uint16_t uart_buffer_index;
uint8_t do_echo;
repeating_timer_t uart_tick_timer;
uint16_t rx_complete_length;
int uart_irq;

// ******** function prototypes ********
void on_uart_rx(void);

// ************ functions *************
void
init_uart(void) {
    // initialize UART
    do_echo = 0; // set to 1 if you want to echo received characters
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_baudrate(UART_ID, BAUD_RATE);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);
    uart_set_fifo_enabled(UART_ID, false); // so we can process char-by-char
    uart_irq = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(uart_irq, on_uart_rx);
    uart_buffer_index = 0;
    rx_complete_length = 0;
}

void
handle_uart_char(uint8_t c) {
    uint16_t num_bytes = 0;
    if (rx_complete_length > 0) {
        // if we already have a complete message, do not read more
        return;
    }
    if ((c == 8) || (c==127)) { // backspace pressed
        if (uart_buffer_index > 0) {
            uart_buffer_index--;
            if (do_echo) {
                uart_putc(UART_ID, 8);
                uart_putc(UART_ID, ' ');
                uart_putc(UART_ID, 8);
            }
        }
        return;
    }
    if (c == 13) {
        num_bytes = uart_buffer_index;
        uart_buffer[uart_buffer_index] = '\0';
        uart_buffer_index = 0;
        if (do_echo) {
            uart_putc(UART_ID, '\n');
            uart_putc(UART_ID, '\r');
        }
        rx_complete_length = num_bytes;
        return;
    }
    uart_buffer[uart_buffer_index] = (uint8_t) c;
    if (do_echo) {
        uart_putc(UART_ID, c);
    }
    uart_buffer_index++;
    if (uart_buffer_index >= UART_IN_BUF_SIZE) {
        uart_buffer_index = 0;
    }
}

void on_uart_rx(void) {
    while (uart_is_readable(UART_ID)) {
        uint8_t c = uart_getc(UART_ID);
        handle_uart_char(c);
    }
}

void uart_int_start() {
    irq_set_enabled(uart_irq, true);
    uart_set_irq_enables(UART_ID, true, false);
}

void uart_int_stop() {
    uart_set_irq_enables(UART_ID, false, false);
    irq_set_enabled(uart_irq, false);
    uart_clear_rx_buffer();
    rx_complete_length = 0;
}

void uart_clear_rx_buffer() {
    uart_buffer_index = 0;
    rx_complete_length = 0;
}