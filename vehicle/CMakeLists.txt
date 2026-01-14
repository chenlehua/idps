cmake_minimum_required(VERSION 3.15)

project(idps-vehicle C)

# C11 standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wextra -Werror -fPIC")
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -g -O0 -DDEBUG")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O2 -DNDEBUG")

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/src
)

# Find required libraries
find_package(OpenSSL 1.1.1 REQUIRED)
find_package(PkgConfig REQUIRED)

pkg_check_modules(JANSSON REQUIRED jansson>=2.13)
pkg_check_modules(LIBBPF REQUIRED libbpf>=0.7)

# Include library directories
include_directories(
    ${OPENSSL_INCLUDE_DIR}
    ${JANSSON_INCLUDE_DIRS}
    ${LIBBPF_INCLUDE_DIRS}
)

# Options
option(BUILD_TESTS "Build unit tests" ON)
option(BUILD_SHARED_LIBS "Build shared libraries" OFF)
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)

# Enable AddressSanitizer if requested
if(ENABLE_ASAN)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")
endif()

# Subdirectories
add_subdirectory(src/common)
add_subdirectory(src/connector)
add_subdirectory(src/network_probe)
add_subdirectory(src/firewall_probe)
add_subdirectory(src/host_probe)
add_subdirectory(src/daemon)

# Tests
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Install targets
install(TARGETS idps_daemon
    RUNTIME DESTINATION bin
)

# Install configuration files
install(FILES config/idps.conf.sample
    DESTINATION /etc/idps
    RENAME idps.conf
)

# Print summary
message(STATUS "========================================")
message(STATUS "IDPS Vehicle Build Configuration")
message(STATUS "========================================")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C Compiler: ${CMAKE_C_COMPILER}")
message(STATUS "C Flags: ${CMAKE_C_FLAGS}")
message(STATUS "OpenSSL version: ${OPENSSL_VERSION}")
message(STATUS "Build tests: ${BUILD_TESTS}")
message(STATUS "AddressSanitizer: ${ENABLE_ASAN}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "========================================")
