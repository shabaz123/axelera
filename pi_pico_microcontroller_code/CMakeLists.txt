cmake_minimum_required(VERSION 3.16)
# set(PICO_BOARD pico_w)
include(pico_sdk_import.cmake)
include(pico_extras_import.cmake)

# set the project name (change to suit)
project(axelera_demo)

pico_sdk_init()

# add_subdirectory()

# include_directories()

# rest of the project
add_executable(${CMAKE_PROJECT_NAME}
        main.cpp
        lcd_i2c_16x2.cpp
        uart_handler.cpp
)

target_include_directories(${CMAKE_PROJECT_NAME}
        PRIVATE
            ${CMAKE_CURRENT_LIST_DIR}
        )

target_link_libraries(${CMAKE_PROJECT_NAME}
        pico_stdlib
        hardware_i2c
        hardware_uart
        )

target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE
        )

# adjust to enable stdio via usb, or uart
pico_enable_stdio_usb(${CMAKE_PROJECT_NAME} 1)
pico_enable_stdio_uart(${CMAKE_PROJECT_NAME} 0)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(${CMAKE_PROJECT_NAME})
