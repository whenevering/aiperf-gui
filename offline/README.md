# AIPerf GUI 离线迁移包说明

本文用于把 `aiperf-gui` 从 GitHub 迁移到完全离线的 Gitea 与流水线环境。默认路径和地址都是示例，进入内网后按实际情况替换。

## 包内内容

```text
aiperf-gui-offline-migration-2026-08-30/
├── README.md
├── source/
│   ├── aiperf-gui.git.bundle
│   ├── aiperf-gui-source.zip
│   └── aiperf-gui-local-repo.tar.gz
├── images/
│   ├── aiperf-base-0.12.0.tar.gz
│   ├── aiperf-base-0.12.0.sha256
│   ├── aiperf-gui-0.12.0-2026-08-30.tar.gz
│   └── aiperf-gui-0.12.0-2026-08-30.sha256
├── pipeline/
│   ├── gitea-actions-docker-build.yml
│   ├── woodpecker.yml
│   └── drone.yml
├── config/
│   ├── env.example
│   ├── gitea-app.ini.example
│   ├── act-runner-config.yaml.example
│   └── docker-daemon.json.example
└── scripts/
    ├── import-gitea.sh
    ├── load-images.sh
    ├── push-images.sh
    └── verify-offline.sh
```

## 离线环境需要准备

- Gitea 服务：已初始化管理员账号，能创建空仓库。
- 流水线服务：Gitea Actions、Woodpecker CI 或 Drone CI 至少一种。
- Runner 节点：Linux x86_64，能访问 Gitea 和内网 Docker Registry。
- Docker Engine：Runner 节点与部署节点均需可用。
- 内网 Docker Registry：例如 `registry.intra.local`、Harbor、Gitea Packages 或 `registry:2`。
- 可选：如果内网 Registry 使用自签名证书，需要把 CA 证书加入 Docker 信任，或在测试环境配置 insecure registry。

可以把 `config/env.example` 复制为 `config/env`，并在里面写入内网 Gitea、Registry、账号等地址；脚本会自动读取该文件。也可以不创建 `config/env`，直接在执行脚本前用 `export` 设置变量。

## 迁移源码到 Gitea

### 方式 A：命令行导入，最稳

1. 在 Gitea 创建空仓库，例如：

```text
http://gitea.intra.local/ai/aiperf-gui.git
```

2. 解压离线包后执行：

```bash
export GITEA_REPO_URL="http://gitea.intra.local/ai/aiperf-gui.git"
./scripts/import-gitea.sh
```

脚本会从 `source/aiperf-gui.git.bundle` 克隆完整 Git 仓库，然后推送到 Gitea。

### 方式 B：Fork / GitKraken 图形化导入

1. 解压 `source/aiperf-gui-local-repo.tar.gz`。
2. 在 Fork 或 GitKraken 中选择打开本地仓库。
3. 把远端地址改成 Gitea 空仓库地址：

```text
http://gitea.intra.local/ai/aiperf-gui.git
```

4. Push `main` 分支和 tags。

### 方式 C：只导入源码，不保留 Git 历史

1. 解压 `source/aiperf-gui-source.zip`。
2. 在 Fork/GitKraken 中初始化新仓库。
3. 添加 Gitea 远端并推送。

## 导入 Docker 镜像到内网

先校验文件：

```bash
cd aiperf-gui-offline-migration-2026-08-30
sha256sum -c images/aiperf-base-0.12.0.sha256
sha256sum -c images/aiperf-gui-0.12.0-2026-08-30.sha256
```

加载镜像：

```bash
./scripts/load-images.sh
```

推送到内网 Registry：

```bash
export REGISTRY="registry.intra.local"
export NAMESPACE="ai"
export REGISTRY_USER="your-user"
export REGISTRY_PASSWORD="your-password"
./scripts/push-images.sh
```

推送后内网应有：

```text
registry.intra.local/ai/aiperf:0.12.0
registry.intra.local/ai/aiperf-gui:0.12.0-2026-08-30
registry.intra.local/ai/aiperf-gui:latest
```

## 配置流水线

### Gitea Actions

1. 确认 Gitea 开启 Actions。参考 `config/gitea-app.ini.example`。
2. 注册并启动 act runner。参考 `config/act-runner-config.yaml.example`。
3. 把 `pipeline/gitea-actions-docker-build.yml` 复制为仓库里的：

```text
.gitea/workflows/docker-build.yml
```

本项目源码中已经包含该文件。

4. 如果内网 Gitea Actions 不能访问外部 `actions/checkout@v4`，需要在内网镜像该 action，或改用 Woodpecker/Drone。
5. 在 Gitea 仓库的 Actions secrets 中设置：

```text
REGISTRY_USER
REGISTRY_PASSWORD
```

如果 Registry 允许匿名推送，可以不设置。

### Woodpecker CI

把 `pipeline/woodpecker.yml` 复制为仓库根目录：

```text
.woodpecker.yml
```

本项目源码中已经包含该文件。

### Drone CI

把 `pipeline/drone.yml` 复制为仓库根目录：

```text
.drone.yml
```

本项目源码中已经包含该文件。

## 流水线构建关键点

项目 Dockerfile 支持内网基础镜像参数：

```bash
docker build \
  --build-arg AIPERF_BASE_IMAGE=registry.intra.local/ai/aiperf:0.12.0 \
  -t registry.intra.local/ai/aiperf-gui:latest .
```

如果不传 `AIPERF_BASE_IMAGE`，默认仍使用：

```text
nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0
```

离线环境必须传内网镜像，或者确保内网 DNS/Registry 已经镜像了该地址。

## 离线部署验证

```bash
export REGISTRY="registry.intra.local"
export NAMESPACE="ai"
./scripts/verify-offline.sh
```

验证成功后打开：

```text
http://部署机器IP:8080
```

## 常见问题

- `pull access denied`：基础镜像没有先导入内网 Registry，或流水线没有使用 `AIPERF_BASE_IMAGE`。
- `x509: certificate signed by unknown authority`：内网 Registry 证书没有被 Docker 信任。
- `Cannot connect to the Docker daemon`：Runner 没有挂载 `/var/run/docker.sock`，或 Docker daemon 未启动。
- Gitea Actions 卡在 checkout：离线环境没有镜像 `actions/checkout`，建议镜像 action 或使用 Woodpecker/Drone。
- 页面能打开但 AIPerf 不可用：运行的是 `Dockerfile.offline` 诊断镜像，而不是正式 AIPerf 镜像。
