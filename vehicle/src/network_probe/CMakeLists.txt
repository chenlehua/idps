# Network Intrusion Detection Probe
add_library(idps_network_probe STATIC
    suricata_manager.c
    rule_manager.c
    eve_parser.c
    log_forwarder.c
)

target_link_libraries(idps_network_probe
    idps_common
    ${JANSSON_LIBRARIES}
    pthread
)

target_include_directories(idps_network_probe PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
