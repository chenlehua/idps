#!/bin/bash
# IDPS快速启动脚本

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_requirements() {
    print_header "检查系统要求"

    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    print_info "✓ Docker已安装: $(docker --version)"

    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    print_info "✓ Docker Compose已安装: $(docker compose --version)"

    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装，请先安装Python3"
        exit 1
    fi
    print_info "✓ Python3已安装: $(python3 --version)"
}

# 启动数据库服务
start_databases() {
    print_header "启动数据库服务"

    print_info "启动MySQL, ClickHouse, Redis..."
    docker compose up -d mysql clickhouse redis

    print_info "等待数据库服务就绪..."
    sleep 10

    # 检查服务状态
    if docker compose ps mysql | grep -q "Up"; then
        print_info "✓ MySQL服务已启动"
    else
        print_error "MySQL服务启动失败"
        exit 1
    fi

    if docker compose ps clickhouse | grep -q "Up"; then
        print_info "✓ ClickHouse服务已启动"
    else
        print_error "ClickHouse服务启动失败"
        exit 1
    fi

    if docker compose ps redis | grep -q "Up"; then
        print_info "✓ Redis服务已启动"
    else
        print_error "Redis服务启动失败"
        exit 1
    fi
}

# 初始化数据库
init_database() {
    print_header "初始化数据库"

    # 检查Python依赖
    if [ ! -d "venv" ]; then
        print_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi

    print_info "激活虚拟环境..."
    source venv/bin/activate

    print_info "安装Python依赖..."
    pip install -q -r cloud/requirements.txt

    print_info "运行数据库初始化脚本..."
    python scripts/init_db.py

    deactivate

    print_info "✓ 数据库初始化完成"
}

# 显示访问信息
show_info() {
    print_header "启动完成"

    echo ""
    print_info "数据库服务已启动:"
    print_info "  MySQL:      localhost:3306"
    print_info "  ClickHouse: localhost:9000 (Native), localhost:8123 (HTTP)"
    print_info "  Redis:      localhost:6379"

    echo ""
    print_info "默认管理员账号:"
    print_info "  用户名: admin"
    print_info "  密码:   Admin@123456"

    echo ""
    print_info "下一步:"
    print_info "  1. 启动云端服务: cd cloud/auth_service && python app.py"
    print_info "  2. 启动前端:     cd frontend && npm install && npm run dev"
    print_info "  3. 构建车端:     cd vehicle && ./build.sh"

    echo ""
    print_info "停止服务:"
    print_info "  docker compose down"

    echo ""
    print_info "查看日志:"
    print_info "  docker compose logs -f [service-name]"
}

# 主函数
main() {
    print_header "IDPS 开发环境快速启动"

    check_requirements
    start_databases
    init_database
    show_info

    print_header "启动完成！"
}

# 执行主函数
main
