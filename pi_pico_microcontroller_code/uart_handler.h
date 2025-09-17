
#ifndef UART_HANDLER_H
#define UART_HANDLER_H

#endif // UART_HANDLER_H

#define UART_IN_BUF_SIZE 128
#define UART_ID uart1
#define BAUD_RATE 115200
#define DATA_BITS 8
#define STOP_BITS 1
#define PARITY    UART_PARITY_ODD
#define UART_TX_PIN 8
#define UART_RX_PIN 9

extern uint16_t rx_complete_length;
extern uint8_t uart_buffer[UART_IN_BUF_SIZE+5];

void init_uart(void);

// these functions start and stop interrupts
// which reads from the UART and fill the uart_buffer
void uart_int_start(void);
void uart_int_stop(void);

// used to resume UART input handling after a complete message was received
void uart_clear_rx_buffer(void);


