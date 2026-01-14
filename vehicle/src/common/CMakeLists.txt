# Common library
add_library(idps_common STATIC
    logging.c
    config.c
    network.c
    crypto.c
    utils.c
)

target_link_libraries(idps_common
    ${OPENSSL_LIBRARIES}
    ${JANSSON_LIBRARIES}
    pthread
)

target_include_directories(idps_common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
