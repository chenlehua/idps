# Host Intrusion Detection Probe
add_library(idps_host_probe STATIC
    audit_monitor.c
    file_monitor.c
    process_monitor.c
    root_detector.c
    perf_monitor.c
)

target_link_libraries(idps_host_probe
    idps_common
    ${OPENSSL_LIBRARIES}
    pthread
)

target_include_directories(idps_host_probe PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
