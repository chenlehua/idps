# IDPS Vehicle - 车端入侵检测系统

## 概述

IDPS Vehicle 是车辆入侵检测系统的车端组件，负责在车辆端进行网络、防火墙和主机层面的入侵检测。

## 系统要求

- **操作系统**: Linux 5.10+
- **架构**: ARM64 (aarch64)
- **依赖库**:
  - OpenSSL 1.1.1+
  - libjansson 2.13+
  - libbpf 0.7+
  - Suricata 7.0+

## 构建

### 本地构建（ARM64平台）

```bash
./build.sh
```

### 交叉编译（x86_64平台）

```bash
# 安装交叉编译工具链
sudo apt-get install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu

# 交叉编译
./build.sh cross
```

### 构建选项

```bash
# 开发版本（带调试信息）
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON
make

# 发布版本
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make

# 运行测试
./build.sh . test
```

## 安装

```bash
cd build
sudo make install
```

安装后的文件位置：
- 主程序: `/usr/sbin/idps_daemon`
- 配置文件: `/etc/idps/idps.conf`
- eBPF程序: `/usr/lib/idps/bpf/`
- 日志文件: `/var/log/idps/`

## 配置

编辑配置文件 `/etc/idps/idps.conf`，主要配置项包括：

- **vehicle.vin**: 车辆识别码（VIN）
- **cloud.server_url**: 云端服务器地址
- **cloud.ca_cert**: CA证书路径
- **cloud.client_cert**: 客户端证书路径
- **cloud.client_key**: 客户端私钥路径

详细配置说明请参考 `config/idps.conf.sample`。

## 运行

### 启动服务

```bash
sudo systemctl start idps
```

### 停止服务

```bash
sudo systemctl stop idps
```

### 查看状态

```bash
sudo systemctl status idps
```

### 查看日志

```bash
sudo tail -f /var/log/idps/idps.log
```

## 目录结构

```
vehicle/
├── CMakeLists.txt          # CMake主配置文件
├── build.sh                # 构建脚本
├── cmake/                  # CMake工具链文件
│   └── toolchain-aarch64.cmake
├── config/                 # 配置文件
│   └── idps.conf.sample
├── include/                # 头文件
│   └── idps/
├── src/                    # 源代码
│   ├── common/            # 公共库（日志、配置、加密等）
│   ├── connector/         # 车云交互组件
│   ├── network_probe/     # 网络入侵检测探针
│   ├── firewall_probe/    # 防火墙探针（eBPF）
│   ├── host_probe/        # 主机入侵检测探针
│   └── daemon/            # 主守护进程
└── tests/                 # 单元测试
```

## 组件说明

### 1. 公共库 (common)

提供基础功能模块：
- **logging**: 日志管理（多级别、轮转、异步）
- **config**: 配置文件解析和管理
- **network**: HTTP/HTTPS网络通信
- **crypto**: 加密解密功能
- **utils**: 工具函数（UUID、Base64、时间等）

### 2. 车云交互组件 (connector)

负责与云端平台通信：
- **tcp_server**: TCP服务器（与探针通信）
- **auth**: 设备认证和Token管理
- **policy_sync**: 规则策略同步
- **log_upload**: 日志批量上报
- **heartbeat**: 心跳保活

### 3. 网络入侵检测探针 (network_probe)

基于Suricata的网络IDS：
- **suricata_manager**: Suricata进程管理
- **rule_manager**: 规则管理和热加载
- **eve_parser**: EVE JSON日志解析
- **log_forwarder**: 日志转发

### 4. 防火墙探针 (firewall_probe)

基于eBPF/XDP的包过滤：
- **xdp_firewall**: XDP防火墙程序（eBPF）
- **firewall_control**: 用户态控制程序
- **port_scan_detector**: 端口扫描检测
- **arp_monitor**: ARP监控

### 5. 主机入侵检测探针 (host_probe)

主机层面的入侵检测：
- **audit_monitor**: Linux Audit监控
- **file_monitor**: 文件完整性监控
- **process_monitor**: 进程监控
- **root_detector**: Root检测
- **perf_monitor**: 性能监控

## 开发指南

### 代码规范

- 遵循Linux内核编码规范
- 使用C11标准
- 函数命名：`模块_功能` (如 `log_init`, `config_load`)
- 变量命名：小写+下划线 (如 `conn_fd`, `rule_version`)

### 添加新模块

1. 在 `src/` 下创建模块目录
2. 编写 `CMakeLists.txt`
3. 在主 `CMakeLists.txt` 中添加 `add_subdirectory()`
4. 实现功能并添加单元测试

### 调试

使用GDB调试：

```bash
# 构建Debug版本
cmake .. -DCMAKE_BUILD_TYPE=Debug
make

# 使用GDB
sudo gdb ./idps_daemon
```

使用AddressSanitizer检测内存问题：

```bash
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_ASAN=ON
make
sudo ./idps_daemon
```

## 许可证

本项目采用私有许可证。与GPL组件（Suricata）通过进程隔离避免许可证传染。

## 联系方式

- 问题反馈: [Issues](https://gitlab.com/idps/vehicle/issues)
- 技术支持: support@idps.example.com
