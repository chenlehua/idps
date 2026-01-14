# uv Python 包管理指南

本文档介绍如何在 IDPS 项目中使用 uv 进行 Python 环境和依赖管理。

## 目录

- [什么是 uv](#什么是-uv)
- [安装 uv](#安装-uv)
- [快速开始](#快速开始)
- [常用命令](#常用命令)
- [依赖管理](#依赖管理)
- [项目配置](#项目配置)
- [与其他工具对比](#与其他工具对比)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 什么是 uv

[uv](https://github.com/astral-sh/uv) 是由 Astral（Ruff 的作者）开发的极速 Python 包管理器和项目管理工具，用 Rust 编写。

### 主要特性

- **极速**: 比 pip 和 pip-tools 快 10-100 倍
- **统一工具**: 替代 pip、pip-tools、pipx、poetry、pyenv 等
- **兼容性强**: 完全兼容 pip，可以直接替换
- **内置虚拟环境**: 自动管理虚拟环境
- **锁文件**: 自动生成和维护 uv.lock
- **Python 版本管理**: 内置 Python 版本下载和管理

### 性能对比

| 操作 | pip | poetry | uv |
|------|-----|--------|-----|
| 安装依赖 | 30s | 25s | **3s** |
| 解析依赖 | 10s | 15s | **1s** |
| 创建虚拟环境 | 5s | 8s | **0.5s** |

## 安装 uv

### Linux/macOS

```bash
# 使用安装脚本
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 验证安装

```bash
uv --version
# 输出: uv 0.4.x (或更新版本)
```

### 配置 shell

安装脚本会自动配置 shell，重新打开终端或运行：

```bash
source $HOME/.cargo/env
```

## 快速开始

### 1. 进入项目目录

```bash
cd cloud
```

### 2. 检查 uv 是否已安装

```bash
make check-uv
# 或
uv --version
```

### 3. 同步依赖（首次设置）

```bash
# 使用 Makefile
make sync

# 或直接使用 uv
uv sync --all-extras
```

这会：
- 创建虚拟环境（`.venv/`）
- 安装所有依赖
- 生成锁文件（`uv.lock`）

### 4. 运行命令

```bash
# 使用 uv run 在虚拟环境中运行
uv run python app.py

# 或使用 Makefile
make dev-auth

# 或激活虚拟环境
source .venv/bin/activate
python app.py
```

## 常用命令

### 基础命令

```bash
# 显示帮助
uv --help

# 显示版本
uv --version

# 初始化新项目
uv init

# 同步依赖（从 pyproject.toml）
uv sync

# 同步包括开发依赖
uv sync --all-extras
```

### Python 版本管理

```bash
# 列出可用的 Python 版本
uv python list

# 安装 Python 版本
uv python install 3.11
uv python install 3.12

# 查看已安装的 Python 版本
uv python list --only-installed

# 使用特定 Python 版本
uv venv --python 3.11
```

### 虚拟环境管理

```bash
# 创建虚拟环境
uv venv

# 指定 Python 版本
uv venv --python 3.11

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 停用虚拟环境
deactivate
```

### 运行命令

```bash
# 在虚拟环境中运行命令（无需激活）
uv run python app.py
uv run pytest
uv run black .

# 运行脚本
uv run --script my_script.py

# 使用 Makefile 封装
make test    # 实际运行: uv run pytest
make lint    # 实际运行: uv run black, uv run ruff, etc.
```

## 依赖管理

### 添加依赖

```bash
# 添加生产依赖
make add PKG=requests

# 或直接使用 uv
uv add requests

# 添加指定版本
uv add "requests>=2.31.0"

# 添加多个依赖
uv add requests flask sqlalchemy
```

### 添加开发依赖

```bash
# 添加开发依赖
make add-dev PKG=pytest

# 或直接使用 uv
uv add --dev pytest

# 添加多个开发依赖
uv add --dev pytest black ruff mypy
```

### 移除依赖

```bash
# 移除依赖
make remove PKG=requests

# 或直接使用 uv
uv remove requests

# 移除多个依赖
uv remove requests flask
```

### 升级依赖

```bash
# 升级所有依赖
make upgrade

# 或直接使用 uv
uv sync --upgrade

# 升级特定依赖
uv add --upgrade requests
```

### 查看依赖

```bash
# 显示依赖树
make tree

# 或直接使用 uv
uv tree

# 显示依赖详情
uv pip list

# 检查过期依赖
uv pip list --outdated
```

### 锁定依赖

```bash
# 生成/更新锁文件
make lock

# 或直接使用 uv
uv lock

# 从锁文件安装（精确版本）
uv sync --frozen
```

## 项目配置

项目使用 `pyproject.toml` 配置依赖和工具。

### pyproject.toml 结构

```toml
[project]
name = "idps-cloud"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "flask>=3.0.0",
    "sqlalchemy>=2.0.23",
    # ... 其他依赖
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "black>=23.12.1",
    # ... 开发依赖
]

[tool.uv]
dev-dependencies = [
    # uv 特定的开发依赖
]

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 配置说明

- `dependencies`: 生产环境依赖
- `optional-dependencies.dev`: 开发环境依赖
- `tool.*`: 各工具的配置（black, ruff, mypy, pytest）

## 与其他工具对比

### uv vs pip

| 特性 | pip | uv |
|------|-----|-----|
| 速度 | 慢 | 快 10-100x |
| 依赖解析 | 基础 | 高级 |
| 锁文件 | 需要 pip-tools | 内置 |
| 虚拟环境 | 需要 venv | 内置自动管理 |
| 兼容性 | - | 完全兼容 pip |

### uv vs poetry

| 特性 | poetry | uv |
|------|--------|-----|
| 速度 | 中等 | 极快 |
| 配置文件 | pyproject.toml | pyproject.toml |
| 锁文件 | poetry.lock | uv.lock |
| 构建系统 | 内置 | 可选 |
| 学习曲线 | 陡峭 | 平缓 |

### 迁移对照

```bash
# pip -> uv
pip install package    →  uv add package
pip uninstall package  →  uv remove package
pip list              →  uv pip list
pip freeze            →  uv pip freeze

# poetry -> uv
poetry add package     →  uv add package
poetry remove package  →  uv remove package
poetry install        →  uv sync
poetry update         →  uv sync --upgrade
poetry run cmd        →  uv run cmd
```

## 最佳实践

### 1. 使用 Makefile 封装

通过 Makefile 提供简单一致的接口：

```bash
make install-dev   # 安装依赖
make test          # 运行测试
make lint          # 代码检查
make add PKG=name  # 添加依赖
```

### 2. 提交锁文件

始终将 `uv.lock` 提交到 git：

```bash
git add uv.lock
git commit -m "Update dependencies"
```

这确保团队成员使用相同的依赖版本。

### 3. 使用 uv run

避免手动激活虚拟环境：

```bash
# 推荐
uv run pytest

# 而不是
source .venv/bin/activate
pytest
```

### 4. 固定 Python 版本

在 `pyproject.toml` 中固定 Python 版本：

```toml
[project]
requires-python = ">=3.11,<3.13"
```

### 5. 定期更新依赖

定期运行依赖更新：

```bash
# 每月一次
make upgrade
make test
git add uv.lock pyproject.toml
git commit -m "Update dependencies"
```

### 6. CI/CD 中使用 uv

在 GitHub Actions 中使用官方 action：

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4
  with:
    enable-cache: true

- name: Set up Python
  run: uv python install 3.11

- name: Install dependencies
  run: uv sync --frozen
```

### 7. 使用 .python-version

在项目根目录创建 `.python-version` 文件：

```
3.11
```

uv 会自动使用这个版本。

## 故障排除

### 问题 1: uv 命令未找到

**解决方法**:

```bash
# 重新安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 配置 PATH
source $HOME/.cargo/env

# 或使用 pip
pip install uv
```

### 问题 2: 权限错误

**解决方法**:

```bash
# 不要使用 sudo
# uv 会在用户目录安装

# 如果需要全局安装工具
uv tool install package-name
```

### 问题 3: 依赖解析失败

**解决方法**:

```bash
# 清理缓存
uv cache clean

# 重新同步
uv sync --reinstall

# 如果还是失败，检查依赖版本约束
uv pip compile pyproject.toml
```

### 问题 4: 虚拟环境位置

**解决方法**:

```bash
# 默认在 .venv/
# 如果需要自定义位置
export UV_VENV=path/to/venv
uv venv $UV_VENV
```

### 问题 5: 与 pip 冲突

**解决方法**:

```bash
# uv 完全兼容 pip
# 可以混合使用，但推荐只用 uv

# 如果需要使用 pip
uv pip install package-name
```

### 问题 6: 锁文件冲突

**解决方法**:

```bash
# git 合并冲突后
git checkout --theirs uv.lock  # 或 --ours
uv sync

# 或手动解决冲突后
uv lock --refresh
```

### 问题 7: 慢速镜像

**解决方法**:

```bash
# 使用国内镜像（中国用户）
export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置在 pyproject.toml
[tool.uv]
index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
```

## 高级用法

### 全局工具安装

```bash
# 安装全局工具（类似 pipx）
uv tool install black
uv tool install ruff

# 运行全局工具
uv tool run black .

# 列出全局工具
uv tool list

# 卸载全局工具
uv tool uninstall black
```

### 从 requirements.txt 迁移

```bash
# 从 requirements.txt 生成 pyproject.toml
uv add $(cat requirements.txt | grep -v "^#" | grep -v "^$")

# 或手动转换
# 然后运行
uv sync
```

### 多 Python 版本测试

```bash
# 测试多个 Python 版本
for version in 3.9 3.10 3.11 3.12; do
  echo "Testing with Python $version"
  uv venv --python $version .venv-$version
  uv sync --python-version $version
  uv run --python $version pytest
done
```

### 缓存管理

```bash
# 查看缓存大小
uv cache dir

# 清理缓存
uv cache clean

# 清理特定包的缓存
uv cache prune
```

## 参考资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [uv GitHub 仓库](https://github.com/astral-sh/uv)
- [Ruff 官方文档](https://docs.astral.sh/ruff/)
- [Python Packaging 用户指南](https://packaging.python.org/)
- [项目 Makefile 文档](./MAKEFILE.md)

## 常见命令速查

```bash
# 环境设置
uv venv                    # 创建虚拟环境
uv sync                    # 同步依赖
uv sync --all-extras       # 同步包括开发依赖

# 依赖管理
uv add package             # 添加依赖
uv add --dev package       # 添加开发依赖
uv remove package          # 移除依赖
uv sync --upgrade          # 升级依赖

# 运行命令
uv run python app.py       # 运行 Python
uv run pytest              # 运行测试
uv run black .             # 格式化代码

# 查看信息
uv tree                    # 依赖树
uv pip list                # 列出包
uv python list             # 列出 Python 版本

# Makefile 封装
make check-uv              # 检查 uv
make sync                  # 同步依赖
make install-dev           # 安装开发依赖
make add PKG=name          # 添加依赖
make remove PKG=name       # 移除依赖
make upgrade               # 升级依赖
make tree                  # 依赖树
```

## 总结

uv 为 IDPS 项目带来了：

1. **极速的依赖安装**: 比传统工具快 10-100 倍
2. **简化的工作流**: 统一的工具替代多个工具
3. **更好的依赖管理**: 自动锁文件和依赖解析
4. **CI/CD 优化**: 大幅减少构建时间
5. **开发体验提升**: 更快的迭代周期

通过 Makefile 封装，团队成员无需学习 uv 的所有细节，就能享受其带来的性能提升。
