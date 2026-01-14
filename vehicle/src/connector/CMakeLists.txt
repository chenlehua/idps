# Vehicle-Cloud Connector
add_library(idps_connector STATIC
    tcp_server.c
    connection.c
    protocol.c
    router.c
    auth.c
    policy_sync.c
    log_upload.c
    heartbeat.c
)

target_link_libraries(idps_connector
    idps_common
    ${OPENSSL_LIBRARIES}
    ${JANSSON_LIBRARIES}
    pthread
)

target_include_directories(idps_connector PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
