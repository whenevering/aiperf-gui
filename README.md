# AIPerf GUI

中文 | [English](README.en.md) | [Francais](README.fr.md) | [Deutsch](README.de.md) | [Espanol](README.es.md)

AIPerf GUI 是一个基于 Docker 的 AIPerf Web 控制台。它把 NVIDIA AIPerf 0.12.0 封装成一个本地可访问的页面，便于对 OpenAI-compatible 模型服务进行吞吐、延迟和并发压测。

![AIPerf GUI 截图](docs/screenshot.png)

## 功能

- 基于 `nvcr.io/nvidia/ai-dynamo/aiperf:0.12.0`
- Web GUI 默认端口 `8080`
- 支持 `chat` 和 `completions` endpoint
- 支持手动输入模型名，也支持通过 `/models` 拉取模型列表
- 支持并发 sweep，例如 `1,2,4,8,16`
- 支持 Input tokens、Output tokens、Requests、Warmup、Timeout
- 支持 Streaming、固定输出长度、服务端指标开关
- 支持 HTTP/HTTPS 代理和 No Proxy 列表
- Result 区展示 TTFT、Request P99、ITL、Output TPS、RPS、输出长度和曲线
- Run Status 区展示实时日志和启动 Banner
- 帮助页支持中文、英文、法文、德文、西班牙文

## 快速开始

```bash
./build.sh
./run.sh
```

打开：

```text
http://127.0.0.1:8080
```

## 常用配置

```text
Base URL: https://apihub.agnes-ai.com/v1
Model: agnes-2.0-flash
Endpoint: chat
Concurrency: 1,2,4,8
Input: 128
Output: 32
Requests: 1
Warmup: 1
Timeout: 120
```

默认代理地址：

```text
http://192.168.1.1:8080
```

代理开关默认关闭。只有目标模型服务需要通过代理访问时才需要打开。

## 健康检查

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/aiperf-info
```

## 离线导出

构建完成后：

```bash
./export-image.sh
```

在离线机器导入并运行：

```bash
./import-and-run.sh aiperf-0.12.0-gui1.tar
```

## 许可证

本项目使用 GNU General Public License v3.0。详见 [LICENSE](LICENSE)。
