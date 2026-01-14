# Firewall Probe (eBPF/XDP)
add_library(idps_firewall_probe STATIC
    firewall_control.c
    port_scan_detector.c
    arp_monitor.c
)

target_link_libraries(idps_firewall_probe
    idps_common
    ${LIBBPF_LIBRARIES}
    elf
    z
    pthread
)

target_include_directories(idps_firewall_probe PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Build eBPF program
add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/xdp_firewall.bpf.o
    COMMAND clang -O2 -g -target bpf -c ${CMAKE_CURRENT_SOURCE_DIR}/xdp_firewall.c -o ${CMAKE_CURRENT_BINARY_DIR}/xdp_firewall.bpf.o
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/xdp_firewall.c
    COMMENT "Compiling eBPF program"
)

add_custom_target(bpf_program ALL
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/xdp_firewall.bpf.o
)

# Install eBPF program
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/xdp_firewall.bpf.o
    DESTINATION /usr/lib/idps/bpf
)
