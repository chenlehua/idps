# Main daemon executable
add_executable(idps_daemon
    main.c
    daemon.c
    signal_handler.c
)

target_link_libraries(idps_daemon
    idps_common
    idps_connector
    idps_network_probe
    idps_firewall_probe
    idps_host_probe
    pthread
    dl
)

target_include_directories(idps_daemon PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Install daemon
install(TARGETS idps_daemon
    RUNTIME DESTINATION /usr/sbin
)
