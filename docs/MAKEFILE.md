# Makefile 使用指南

本文档提供 IDPS 项目 Makefile 构建系统的完整使用指南。

## 目录

- [概览](#概览)
- [快速开始](#快速开始)
- [全局命令](#全局命令)
- [车端构建](#车端构建)
- [云端后端构建](#云端后端构建)
- [前端构建](#前端构建)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 概览

项目使用 Make 作为统一的构建工具，提供简单一致的命令接口来构建、测试和部署各个模块。

### Makefile 结构

```
idps/
├── Makefile                 # 主 Makefile (管理所有模块)
├── vehicle/Makefile         # 车端构建
├── cloud/Makefile           # 云端后端构建
└── frontend/Makefile        # 前端构建
```

### 设计理念

- **简单易用**: 统一的命令接口
- **模块化**: 每个模块独立管理
- **彩色输出**: 清晰的视觉反馈
- **自说明**: 运行 `make help` 查看可用命令

## 快速开始

### 1. 查看帮助信息

```bash
# 查看主 Makefile 帮助
make help

# 查看车端帮助
cd vehicle && make help

# 查看云端后端帮助
cd cloud && make help

# 查看前端帮助
cd frontend && make help
```

### 2. 构建所有模块

```bash
# 在项目根目录
make build
```

这会依次构建：
- 车端二进制
- 云端后端 (安装依赖)
- 前端应用

### 3. 运行所有测试

```bash
make test
```

### 4. 运行所有代码检查

```bash
make lint
```

## 全局命令

在项目根目录运行这些命令来管理整个项目。

### 构建和测试

```bash
make all              # 构建所有模块
make build            # 构建所有模块
make test             # 运行所有测试
make lint             # 运行所有代码检查
make clean            # 清理所有构建产物
```

### Docker 操作

```bash
make docker-build     # 构建所有 Docker 镜像
make docker-push      # 推送所有 Docker 镜像
```

### 开发环境

```bash
make dev-up           # 启动开发环境 (Docker Compose)
make dev-down         # 停止开发环境
make dev-logs         # 查看开发环境日志
make dev-ps           # 查看开发环境状态
```

### 数据库

```bash
make db-init          # 初始化数据库
make db-migrate       # 运行数据库迁移
```

### 工具命令

```bash
make check-tools      # 检查必需工具是否已安装
make info             # 显示项目信息
make version          # 显示版本信息
```

### 模块特定命令

```bash
# 车端
make vehicle              # 构建车端
make vehicle-build        # 构建车端二进制
make vehicle-build-cross  # 交叉编译 (ARM64)
make vehicle-test         # 运行车端测试
make vehicle-lint         # 车端代码检查
make vehicle-clean        # 清理车端构建产物

# 云端后端
make cloud                # 构建云端后端
make cloud-build          # 安装云端依赖
make cloud-test           # 运行云端测试
make cloud-lint           # 云端代码检查
make cloud-docker         # 构建云端 Docker 镜像
make cloud-clean          # 清理云端构建产物

# 前端
make frontend             # 构建前端
make frontend-build       # 构建前端应用
make frontend-test        # 运行前端测试
make frontend-lint        # 前端代码检查
make frontend-docker      # 构建前端 Docker 镜像
make frontend-clean       # 清理前端构建产物
```

## 车端构建

进入 `vehicle/` 目录运行以下命令。

### 基本构建

```bash
make build            # 构建本地架构
make build-cross      # 交叉编译 ARM64
make build-debug      # 构建 Debug 版本
```

构建产物：
- 本地构建: `build/src/daemon/idps_daemon`
- 交叉编译: `build-aarch64/src/daemon/idps_daemon`
- Debug 构建: `build-debug/src/daemon/idps_daemon`

### 测试

```bash
make test             # 运行单元测试
make test-verbose     # 运行测试 (详细输出)
```

### 代码质量

```bash
make lint             # 代码格式检查
make format           # 格式化代码
make format-check     # 检查代码格式 (不修改)
make static-analysis  # 运行静态分析
```

### 安装

```bash
make install          # 安装到系统
make uninstall        # 从系统卸载
```

### 清理

```bash
make clean            # 清理构建产物
make clean-all        # 深度清理 (包括 CMake 缓存)
```

### 工具

```bash
make deps             # 检查依赖
make info             # 显示构建信息
make quick            # 快速构建和测试
make all              # 构建并测试
```

### 示例工作流

```bash
# 开发流程
cd vehicle
make clean            # 清理旧的构建
make build            # 构建
make test             # 测试
make lint             # 代码检查

# 快速构建和测试
make quick

# 交叉编译到 ARM64
make build-cross
```

## 云端后端构建

进入 `cloud/` 目录运行以下命令。

### 环境设置

```bash
make venv             # 创建虚拟环境
source venv/bin/activate  # 激活虚拟环境
make install          # 安装依赖
make install-dev      # 安装开发依赖
```

### 测试

```bash
make test             # 运行所有测试
make test-unit        # 运行单元测试
make test-integration # 运行集成测试
make test-coverage    # 生成覆盖率报告
```

覆盖率报告: `htmlcov/index.html`

### 代码质量

```bash
make lint             # 运行所有检查
make format           # 格式化代码 (black)
make format-check     # 检查代码格式
make flake8           # 运行 flake8
make mypy             # 运行类型检查
```

### Docker 操作

```bash
# 构建所有服务镜像
make docker-build

# 构建单个服务镜像
make docker-build-auth_service
make docker-build-rule_service
make docker-build-log_service
make docker-build-vehicle_service

# 推送镜像
make docker-push
make docker-push-auth_service
```

### 开发服务器

```bash
make dev-auth         # 启动认证服务
make dev-rule         # 启动规则服务
make dev-log          # 启动日志服务
make dev-vehicle      # 启动车辆管理服务
```

### 依赖管理

```bash
make freeze           # 导出当前依赖
make upgrade          # 升级所有依赖
```

### 清理

```bash
make clean            # 清理构建产物
make clean-all        # 深度清理 (包括 Docker 镜像)
make docker-clean     # 清理 Docker 镜像
```

### 示例工作流

```bash
# 初始设置
cd cloud
make venv
source venv/bin/activate
make install-dev

# 开发流程
make lint             # 代码检查
make test             # 运行测试

# 构建 Docker 镜像
make docker-build

# 快速测试
make quick
```

## 前端构建

进入 `frontend/` 目录运行以下命令。

### 安装依赖

```bash
make install          # 生产依赖 (npm ci)
make install-dev      # 开发依赖 (npm install)
```

### 构建

```bash
make build            # 构建生产版本
make build-dev        # 构建开发版本
```

构建产物: `dist/`

### 测试

```bash
make test             # 运行测试
make test-watch       # 监听模式
make test-coverage    # 生成覆盖率报告
```

覆盖率报告: `coverage/index.html`

### 代码质量

```bash
make lint             # ESLint 检查
make lint-fix         # 自动修复 ESLint 问题
make type-check       # TypeScript 类型检查
make format           # 格式化代码 (Prettier)
make format-check     # 检查代码格式
```

### 开发服务器

```bash
make dev              # 启动开发服务器
make dev-host         # 启动开发服务器 (允许外部访问)
make preview          # 预览生产构建
```

开发服务器默认运行在: http://localhost:3000

### Docker 操作

```bash
make docker-build     # 构建 Docker 镜像
make docker-push      # 推送 Docker 镜像
make docker-run       # 运行 Docker 容器
make docker-clean     # 清理 Docker 镜像
```

### 依赖管理

```bash
make update           # 更新依赖
make outdated         # 检查过期依赖
make audit            # 安全审计
make audit-fix        # 自动修复安全问题
```

### 清理

```bash
make clean            # 清理构建产物
make clean-all        # 深度清理 (包括 node_modules)
make clean-cache      # 清理 npm 缓存
```

### 工具

```bash
make analyze          # 分析构建产物大小
```

### 示例工作流

```bash
# 初始设置
cd frontend
make install

# 开发流程
make dev              # 启动开发服务器

# 构建流程
make lint             # 代码检查
make type-check       # 类型检查
make test             # 运行测试
make build            # 构建生产版本

# 快速测试
make quick

# 完整流程
make all
```

## 最佳实践

### 1. 使用 help 命令

在任何时候不确定可用命令时，运行 `make help`:

```bash
make help
cd vehicle && make help
cd cloud && make help
cd frontend && make help
```

### 2. 模块化开发

在开发特定模块时，进入对应目录使用该模块的 Makefile:

```bash
# 只开发车端
cd vehicle
make quick

# 只开发云端后端
cd cloud
make lint test
```

### 3. 并行构建

Make 支持并行任务，使用 `-j` 参数加速构建:

```bash
make -j4 build        # 4 个并行任务
make -j$(nproc) build # 使用所有 CPU 核心
```

### 4. 干跑 (Dry Run)

查看 Make 将执行的命令但不实际执行:

```bash
make -n build         # 干跑
make -n test          # 查看测试命令
```

### 5. 持续集成

在 CI/CD 中使用统一的 Make 命令:

```yaml
# GitHub Actions 示例
- name: Build
  run: make build

- name: Test
  run: make test

- name: Lint
  run: make lint
```

### 6. 开发环境标准化

使用 Make 确保团队成员使用相同的构建命令:

```bash
# 所有开发者都运行相同的命令
make install
make build
make test
```

### 7. 快速命令

使用预定义的快速命令提高效率:

```bash
make quick            # 清理、构建、测试
make all              # 完整构建流程
```

## 故障排除

### 问题 1: make: 命令未找到

**解决方法**:

```bash
# Ubuntu/Debian
sudo apt-get install make

# macOS
xcode-select --install

# 验证安装
make --version
```

### 问题 2: 权限错误

**解决方法**:

```bash
# 不要使用 sudo 运行 make
# 如果需要权限，只在特定命令使用 sudo
make build            # 正常构建
sudo make install     # 安装时使用 sudo
```

### 问题 3: 构建失败，依赖缺失

**解决方法**:

```bash
# 检查依赖
make check-tools      # 主目录
make deps             # 各子目录

# 车端依赖
sudo apt-get install cmake libssl-dev libjansson-dev

# 云端依赖
pip install -r cloud/requirements.txt

# 前端依赖
cd frontend && npm install
```

### 问题 4: 清理后无法构建

**解决方法**:

```bash
# 使用 clean-all 可能删除了必要文件
# 重新安装依赖

# 云端
cd cloud
make install

# 前端
cd frontend
make install
```

### 问题 5: Docker 构建失败

**解决方法**:

```bash
# 检查 Docker 是否运行
docker ps

# 登录到容器仓库
docker login ghcr.io

# 检查磁盘空间
df -h

# 清理旧镜像
docker system prune -a
```

### 问题 6: 并行构建错误

某些目标不支持并行构建，移除 `-j` 参数:

```bash
# 错误
make -j4 target

# 正确
make target
```

### 问题 7: 颜色输出不显示

**解决方法**:

```bash
# 确保终端支持颜色
# 或禁用颜色输出
make build 2>&1 | cat
```

## 进阶用法

### 变量覆盖

覆盖 Makefile 中的变量:

```bash
# 使用不同的 Python 版本
make test PYTHON=python3.10

# 使用不同的构建类型
cd vehicle
make build CMAKE_BUILD_TYPE=Debug

# 指定并行任务数
make build NPROC=8
```

### 链式命令

组合多个命令:

```bash
make clean && make build && make test
```

### 条件执行

只在上一个命令成功时执行下一个:

```bash
make build && make test || echo "Build or test failed"
```

### 查看变量值

```bash
# 查看 Makefile 变量
make -p | grep VERSION_TAG
```

### 忽略错误

继续执行即使某些命令失败:

```bash
make -i test         # 忽略错误继续
make -k test         # 失败后继续其他目标
```

## 自定义 Makefile

如果需要为项目添加自定义构建步骤，可以编辑对应的 Makefile:

1. 在 `.PHONY` 行添加新目标
2. 添加目标定义
3. 添加帮助文档 (使用 `##`)

示例:

```makefile
.PHONY: my-custom-target

my-custom-target: ## 我的自定义目标描述
	@echo "执行自定义任务"
	@# 你的命令
```

然后运行:

```bash
make my-custom-target
```

## 参考资源

- [GNU Make 手册](https://www.gnu.org/software/make/manual/)
- [Make 教程](https://makefiletutorial.com/)
- [项目主 Makefile](../Makefile)
- [GitHub Actions 配置](./GITHUB_ACTIONS.md)

## 总结

Make 提供了统一、简单的接口来管理 IDPS 项目的构建、测试和部署流程。

### 常用命令速查

```bash
# 帮助
make help

# 构建
make build
make vehicle-build
make cloud-build
make frontend-build

# 测试
make test
make vehicle-test
make cloud-test
make frontend-test

# 代码检查
make lint
make vehicle-lint
make cloud-lint
make frontend-lint

# 清理
make clean
make vehicle-clean
make cloud-clean
make frontend-clean

# Docker
make docker-build
make docker-push

# 开发
make dev-up
make dev-down
```

记住：当不确定时，运行 `make help`！
