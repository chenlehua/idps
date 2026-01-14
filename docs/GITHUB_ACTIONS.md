# GitHub Actions 配置指南

本文档提供从 GitLab CI/CD 迁移到 GitHub Actions 的完整指南，以及如何配置和使用 IDPS 项目的 GitHub Actions 工作流。

## 目录

- [主要变化](#主要变化)
- [工作流概览](#工作流概览)
- [配置步骤](#配置步骤)
- [Secrets 配置](#secrets-配置)
- [环境配置](#环境配置)
- [常见问题](#常见问题)

## 主要变化

### GitLab CI vs GitHub Actions 对比

| 功能 | GitLab CI | GitHub Actions |
|------|-----------|----------------|
| 配置文件 | `.gitlab-ci.yml` | `.github/workflows/*.yml` |
| 触发器 | `only`, `except` | `on` (push, pull_request, etc.) |
| 作业定义 | `job_name:` | `jobs: job_name:` |
| 镜像仓库 | GitLab Container Registry | GitHub Container Registry (ghcr.io) |
| Runner 标签 | `tags: [docker]` | `runs-on: ubuntu-latest` |
| 变量 | `variables:` | `env:` |
| 依赖关系 | `needs:` | `needs:` (相同) |
| 制品 | `artifacts:` | `actions/upload-artifact@v4` |
| 缓存 | `cache:` | `actions/cache@v3` 或内置缓存 |

## 工作流概览

### 1. Vehicle CI (车端)

**文件**: `.github/workflows/vehicle-ci.yml`

**触发条件**:
- Push 到 `main` 或 `develop` 分支，且 `vehicle/` 目录有变更
- 针对 `vehicle/` 目录的 Pull Request

**作业流程**:
```
lint (代码格式检查) ─┐
test (单元测试)     ─┼─> build (交叉编译构建)
```

**关键特性**:
- 使用 `gcc:11` Docker 容器运行
- 交叉编译到 ARM64 架构
- 生成构建产物并保存 7 天

### 2. Cloud Backend CI (云端后端)

**文件**: `.github/workflows/cloud-ci.yml`

**触发条件**:
- Push 到 `main` 或 `develop` 分支，且 `cloud/` 目录有变更
- 针对 `cloud/` 目录的 Pull Request

**作业流程**:
```
lint (代码检查) ─┐
test (单元测试) ─┼─> build-auth-service (构建认证服务)
                 ├─> build-rule-service (构建规则服务)
                 ├─> build-log-service (构建日志服务)
                 └─> build-vehicle-service (构建车辆管理服务)
```

**关键特性**:
- Python 3.11 环境
- 覆盖率报告上传到 Codecov
- 只在 push 事件时构建 Docker 镜像
- 镜像推送到 GitHub Container Registry (ghcr.io)
- 使用 GitHub Actions 缓存加速构建

### 3. Frontend CI (前端)

**文件**: `.github/workflows/frontend-ci.yml`

**触发条件**:
- Push 到 `main` 或 `develop` 分支，且 `frontend/` 目录有变更
- 针对 `frontend/` 目录的 Pull Request

**作业流程**:
```
lint (代码检查) ─┐
test (单元测试) ─┼─> build (构建应用) ─> build-docker (构建 Docker 镜像)
```

**关键特性**:
- Node.js 20 环境
- 使用 npm ci 和缓存加速安装
- 构建产物在作业间传递
- 覆盖率报告上传到 Codecov

### 4. Deploy (部署)

**文件**: `.github/workflows/deploy.yml`

**触发条件**:
- Push 到 `develop` 分支 → 部署到测试环境
- Push 到 `main` 分支 → 部署到生产环境
- 手动触发 (workflow_dispatch)

**作业流程**:
```
deploy-staging (测试环境部署)
deploy-production (生产环境部署)
```

**关键特性**:
- SSH 部署到远程服务器
- 环境保护和审批机制
- 部署后健康检查
- 支持手动触发指定环境部署

## 配置步骤

### 步骤 1: 准备 GitHub 仓库

1. 在 GitHub 上创建新仓库或使用现有仓库
2. 将代码推送到 GitHub

```bash
# 添加 GitHub 作为远程仓库
git remote add github https://github.com/your-org/idps.git

# 推送代码
git push github main
git push github develop
```

### 步骤 2: 配置 GitHub Container Registry 权限

1. 前往仓库设置 → Actions → General
2. 在 "Workflow permissions" 下选择 "Read and write permissions"
3. 勾选 "Allow GitHub Actions to create and approve pull requests"
4. 点击保存

### 步骤 3: 配置分支保护规则 (可选但推荐)

1. 前往仓库设置 → Branches
2. 为 `main` 和 `develop` 分支添加保护规则
3. 启用以下选项:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - 选择必需的检查: lint, test, build
   - ✅ Require conversation resolution before merging

### 步骤 4: 配置环境 (用于部署)

1. 前往仓库设置 → Environments
2. 创建 `staging` 环境
   - 可选: 添加保护规则和审批者
3. 创建 `production` 环境
   - ✅ Required reviewers: 添加审批者
   - ✅ Wait timer: 设置等待时间 (例如 5 分钟)

## Secrets 配置

### 必需的 Secrets

在仓库设置 → Secrets and variables → Actions 中添加以下 Secrets:

#### 部署 Secrets

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `SSH_PRIVATE_KEY` | SSH 私钥内容 | `-----BEGIN OPENSSH PRIVATE KEY-----\n...` |
| `STAGING_HOST` | 测试环境服务器地址 | `staging.idps.example.com` |
| `STAGING_USER` | 测试环境 SSH 用户 | `deploy` |
| `PRODUCTION_HOST` | 生产环境服务器地址 | `idps.example.com` |
| `PRODUCTION_USER` | 生产环境 SSH 用户 | `deploy` |

#### 生成 SSH 密钥对

```bash
# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ./deploy_key

# 将公钥添加到服务器
ssh-copy-id -i ./deploy_key.pub user@server

# 将私钥内容复制到 GitHub Secret
cat ./deploy_key
```

#### 可选: 第三方服务 Tokens

如果使用 Codecov、Sentry 等服务:

| Secret 名称 | 说明 |
|------------|------|
| `CODECOV_TOKEN` | Codecov 上传 token (私有仓库需要) |
| `SENTRY_AUTH_TOKEN` | Sentry 部署通知 token |
| `SLACK_WEBHOOK_URL` | Slack 通知 webhook |

### Environment Secrets

对于特定环境的 Secrets，可以在环境配置中添加:

1. 前往 Settings → Environments → [环境名称]
2. 在 "Environment secrets" 中添加仅该环境可用的 secrets

## 环境配置

### Docker 镜像推送权限

GitHub Actions 使用 `GITHUB_TOKEN` 自动认证到 GitHub Container Registry。无需额外配置。

推送的镜像地址格式:
```
ghcr.io/<github-username-or-org>/<repo-name>/<service-name>:<tag>
```

例如:
```
ghcr.io/myorg/idps/auth-service:latest
ghcr.io/myorg/idps/auth-service:abc1234
```

### 使镜像公开可访问

默认情况下，推送到 GHCR 的镜像是私有的。要使其公开:

1. 前往 https://github.com/users/YOUR_USERNAME/packages
2. 找到对应的包
3. Package settings → Danger Zone → Change visibility
4. 选择 "Public"

或者，在部署服务器上配置 Docker 登录:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

## 工作流管理

### 查看工作流运行

1. 前往仓库的 "Actions" 标签页
2. 查看所有工作流运行历史
3. 点击特定运行查看详细日志

### 手动触发部署

1. 前往 Actions → Deploy 工作流
2. 点击 "Run workflow"
3. 选择分支和目标环境
4. 点击 "Run workflow" 确认

### 重新运行失败的作业

1. 进入失败的工作流运行
2. 点击右上角 "Re-run jobs"
3. 选择 "Re-run failed jobs" 或 "Re-run all jobs"

### 取消运行中的工作流

1. 进入运行中的工作流
2. 点击右上角 "Cancel workflow"

## 常见问题

### Q1: Docker 镜像推送失败，提示权限错误

**解决方法**:
1. 检查仓库 Actions 设置中的 "Workflow permissions"
2. 确保选择了 "Read and write permissions"
3. 重新运行工作流

### Q2: 部署时 SSH 连接失败

**解决方法**:
1. 检查 SSH_PRIVATE_KEY secret 是否正确配置
2. 确保私钥格式正确 (包含 `-----BEGIN OPENSSH PRIVATE KEY-----`)
3. 验证公钥已添加到目标服务器的 `~/.ssh/authorized_keys`
4. 检查服务器的防火墙规则

### Q3: 工作流没有触发

**可能原因**:
1. 文件路径过滤器不匹配 - 检查 `paths` 配置
2. 分支保护规则阻止 - 检查分支保护设置
3. 工作流文件语法错误 - 查看 Actions 标签页的错误提示

### Q4: 如何调试工作流

**方法**:
1. 在步骤中添加调试输出:
   ```yaml
   - name: Debug
     run: |
       echo "Event: ${{ github.event_name }}"
       echo "Ref: ${{ github.ref }}"
       env
   ```

2. 启用调试日志:
   - 在仓库 Settings → Secrets 中添加:
     - `ACTIONS_STEP_DEBUG` = `true`
     - `ACTIONS_RUNNER_DEBUG` = `true`

### Q5: 缓存不生效

**解决方法**:
1. 检查缓存键 (key) 是否正确
2. 确保缓存的文件路径存在
3. GitHub Actions 缓存有 10GB 限制，旧缓存会被自动删除

### Q6: 如何限制并发运行

在工作流文件中添加:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## 最佳实践

### 1. 使用矩阵策略进行多版本测试

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### 2. 使用 if 条件控制作业执行

```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
```

### 3. 使用可复用的工作流

对于重复的逻辑，可以创建可复用的工作流:

```yaml
# .github/workflows/reusable-build.yml
on:
  workflow_call:
    inputs:
      service-name:
        required: true
        type: string
```

### 4. 添加状态徽章到 README

```markdown
![Vehicle CI](https://github.com/org/idps/actions/workflows/vehicle-ci.yml/badge.svg)
![Cloud CI](https://github.com/org/idps/actions/workflows/cloud-ci.yml/badge.svg)
![Frontend CI](https://github.com/org/idps/actions/workflows/frontend-ci.yml/badge.svg)
```

### 5. 定期更新 Actions 版本

使用 Dependabot 自动更新 Actions 版本:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## 迁移检查清单

- [ ] 创建 `.github/workflows/` 目录
- [ ] 转换所有 GitLab CI 作业到 GitHub Actions
- [ ] 配置 GitHub Container Registry 权限
- [ ] 添加所有必需的 Secrets
- [ ] 配置部署环境和保护规则
- [ ] 测试所有工作流
- [ ] 更新文档中的 CI/CD 说明
- [ ] 添加状态徽章到 README
- [ ] 通知团队成员新的 CI/CD 流程
- [ ] (可选) 删除或归档 `.gitlab-ci.yml`

## 参考资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [从 GitLab CI/CD 迁移到 GitHub Actions](https://docs.github.com/en/actions/migrating-to-github-actions/migrating-from-gitlab-cicd-to-github-actions)
- [GitHub Actions 市场](https://github.com/marketplace?type=actions)
- [GitHub Container Registry 文档](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 支持

如有问题，请:
1. 查看工作流运行日志
2. 参考本文档的常见问题部分
3. 在项目中创建 Issue
4. 联系 DevOps 团队
