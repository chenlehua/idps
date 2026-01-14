#!/bin/bash
# Build script for IDPS Vehicle

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if running on ARM64 or cross-compiling
ARCH=$(uname -m)
BUILD_DIR="build"

if [ "$1" == "cross" ]; then
    print_info "Cross-compiling for ARM64..."
    BUILD_DIR="build-aarch64"
    CROSS_COMPILE="-DCMAKE_TOOLCHAIN_FILE=../cmake/toolchain-aarch64.cmake"
elif [ "$ARCH" != "aarch64" ] && [ "$ARCH" != "arm64" ]; then
    print_warn "Not running on ARM64 architecture. Use './build.sh cross' for cross-compilation."
fi

# Create build directory
print_info "Creating build directory: $BUILD_DIR"
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# Run CMake
print_info "Running CMake configuration..."
cmake .. ${CROSS_COMPILE} \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTS=ON

# Build
print_info "Building IDPS Vehicle..."
make -j$(nproc)

# Run tests if requested
if [ "$2" == "test" ]; then
    print_info "Running tests..."
    ctest --output-on-failure
fi

print_info "Build completed successfully!"
print_info "Binary location: $BUILD_DIR/src/daemon/idps_daemon"
