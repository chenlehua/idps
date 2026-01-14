#!/bin/bash
# IDPS 项目依赖检查脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}IDPS 项目依赖检查${NC}"
echo ""

MISSING_DEPS=()
WARNINGS=()

# 检查函数
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2: $($1 --version 2>&1 | head -1)"
    else
        echo -e "${RED}✗${NC} $2: 未安装"
        MISSING_DEPS+=("$2")
        if [ -n "$3" ]; then
            echo -e "  ${YELLOW}安装命令: $3${NC}"
        fi
    fi
}

# 检查 Docker
echo -e "${BLUE}基础工具${NC}"
check_command "docker" "Docker" "curl -fsSL https://get.docker.com | sh"
check_command "make" "Make" "sudo apt-get install build-essential"
check_command "git" "Git" "sudo apt-get install git"

# 检查 Docker Compose
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose: $(docker compose version --short)"
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker Compose: $(docker-compose --version)"
else
    echo -e "${RED}✗${NC} Docker Compose: 未安装"
    MISSING_DEPS+=("Docker Compose")
fi

echo ""
echo -e "${BLUE}Python 环境${NC}"
check_command "python3" "Python" "sudo apt-get install python3"

# 检查 uv
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓${NC} uv: $(uv --version)"
elif [ -f "$HOME/.local/bin/uv" ]; then
    echo -e "${GREEN}✓${NC} uv: $($HOME/.local/bin/uv --version)"
else
    echo -e "${RED}✗${NC} uv: 未安装"
    MISSING_DEPS+=("uv")
    echo -e "  ${YELLOW}安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
fi

echo ""
echo -e "${BLUE}Node.js 环境${NC}"
check_command "node" "Node.js" "使用 nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash && nvm install 20"
check_command "npm" "npm" "随 Node.js 一起安装"

echo ""
echo -e "${BLUE}车端开发工具${NC}"
check_command "gcc" "GCC" "sudo apt-get install build-essential"
check_command "cmake" "CMake" "sudo apt-get install cmake"

# 检查交叉编译工具链（可选）
if command -v aarch64-linux-gnu-gcc &> /dev/null; then
    echo -e "${GREEN}✓${NC} ARM64 交叉编译工具链: $(aarch64-linux-gnu-gcc --version | head -1)"
else
    echo -e "${YELLOW}○${NC} ARM64 交叉编译工具链: 未安装 (可选)"
    WARNINGS+=("ARM64 交叉编译需要: sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu")
fi

# 检查 clang-format（可选）
if command -v clang-format &> /dev/null; then
    echo -e "${GREEN}✓${NC} clang-format: $(clang-format --version | head -1)"
else
    echo -e "${YELLOW}○${NC} clang-format: 未安装 (可选)"
    WARNINGS+=("代码格式化需要: sudo apt-get install clang-format")
fi

echo ""
echo -e "${BLUE}系统库${NC}"

# 检查 pkg-config
if command -v pkg-config &> /dev/null; then
    echo -e "${GREEN}✓${NC} pkg-config: $(pkg-config --version)"
else
    echo -e "${RED}✗${NC} pkg-config: 未安装"
    MISSING_DEPS+=("pkg-config")
    echo -e "  ${YELLOW}安装命令: sudo apt-get install pkg-config${NC}"
fi

# 检查开发库（用于车端编译）
check_lib() {
    if pkg-config --exists "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $2: $(pkg-config --modversion $1)"
    else
        echo -e "${YELLOW}○${NC} $2: 未安装 (车端开发需要)"
        WARNINGS+=("$2: sudo apt-get install $3")
    fi
}

check_lib "openssl" "OpenSSL" "libssl-dev"
check_lib "jansson" "Jansson" "libjansson-dev"

# 总结
echo ""
echo -e "${BLUE}检查总结${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ 所有必需依赖已安装${NC}"
else
    echo -e "${RED}✗ 缺少 ${#MISSING_DEPS[@]} 个必需依赖:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo -e "${YELLOW}请先安装缺少的依赖再继续${NC}"
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}可选依赖 (${#WARNINGS[@]} 个):${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo "  - $warning"
    done
fi

echo ""
if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ 环境就绪！可以运行: make dev-up${NC}"
    exit 0
else
    echo -e "${RED}请先安装缺少的依赖${NC}"
    exit 1
fi
