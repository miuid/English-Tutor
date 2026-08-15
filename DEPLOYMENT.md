# 部署指南（Docker · 局域网服务器）

本文档描述如何把 English Tutor 完整部署到 LAN 内的一台主服务器上，让局域网内的任何设备（电脑 / 平板 / 手机）通过浏览器直接使用。

## 架构

```
LAN 设备浏览器
      │  http://<服务器IP>/
      ▼
┌─────────────────────────────────────────────┐
│ docker compose 网络                          │
│                                             │
│  frontend 容器（nginx, 端口 80 → 宿主机 80） │
│    ├─ 静态页面（React 生产构建）             │
│    └─ /api/* 反向代理 ──► backend 容器       │
│                          （FastAPI :8000，   │
│                           不对外暴露端口）   │
│                               │             │
│                    tutor-data 卷（SQLite）   │
│                    ./skills 只读挂载         │
└─────────────────────────────────────────────┘
```

- 对外只有一个端口（默认 80，可用 `WEB_PORT` 改）。
- 前端代码里 API 全部走相对路径 `/api`，由 nginx 同域代理，**无 CORS 问题**。
- LLM 调用可能耗时 30–60 秒，nginx 代理超时已放宽到 180 秒。

## 前置要求

- 服务器：任意 Linux 主机（群晖 / Ubuntu / Debian / Unraid 等均可），x86_64 或 ARM64。
- 已安装 **Docker Engine 20.10+** 和 **Docker Compose v2**（`docker compose version` 能输出版本号即可）。
- 一个 LLM API Key（默认 DeepSeek；Anthropic 改配置即可）。

## 部署步骤

### 1. 把项目拷贝到服务器

```bash
# 在开发机上打包（排除无关大目录）
tar --exclude=node_modules --exclude=.git --exclude=dist \
    --exclude='*.db' --exclude=__pycache__ \
    -czf english-tutor.tar.gz english-tutor/

# 传到服务器并解压
scp english-tutor.tar.gz user@<服务器IP>:~/
ssh user@<服务器IP>
tar -xzf english-tutor.tar.gz && cd english-tutor
```

也可以用 git clone / rsync / SMB 共享，随意。

### 2. 配置 LLM API Key

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

最小配置（Kimi/Moonshot，默认）：

```ini
APP_ENV=production
LLM_PROVIDER=kimi
LLM_MODEL=kimi-k3
LLM_API_KEY=sk-你的真实key
```

换 DeepSeek / Anthropic 只需改三行：`LLM_PROVIDER=deepseek|anthropic`、`LLM_MODEL=deepseek-chat|claude-sonnet-4-6`、`LLM_API_KEY=...`。业务代码零改动（adapter 层设计）。

> ⚠️ `docker compose` 启动时要求 `backend/.env` 必须存在，缺少会直接报错。

### 3. 构建并启动

```bash
docker compose up -d --build
```

首次构建约 3–8 分钟（下载基础镜像 + pip/npm 安装依赖）。之后日常启动只要几秒。

### 4. 验证

```bash
# 容器状态
docker compose ps          # 两个服务都应是 running

# 后端健康检查（经 nginx 代理）
curl http://localhost/health   # {"status":"ok"}
```

### 5. 局域网访问

在任意 LAN 设备浏览器打开：

```
http://<服务器IP>/
```

查看服务器 IP：`ip addr`（Linux）或在路由器后台查。如果 80 端口被占用：

```bash
WEB_PORT=8080 docker compose up -d   # 然后访问 http://<服务器IP>:8080/
```

如需防火墙放行（以 ufw 为例）：`sudo ufw allow 80/tcp`。

## 日常运维

| 操作 | 命令 |
|---|---|
| 查看日志 | `docker compose logs -f backend` / `frontend` |
| 停止 | `docker compose down`（数据保留在卷里） |
| 停止并清空数据 | `docker compose down -v` ⚠️ 删除所有学生数据 |
| 更新代码后重启 | `docker compose up -d --build` |
| 修改 skills 后生效 | `docker compose restart backend`（skills 是只读挂载，改文件即生效，重启触发重新同步） |

### 数据备份

所有学生数据都在名为 `english-tutor_tutor-data` 的 Docker 卷里的一个 SQLite 文件：

```bash
# 备份（服务器上执行）
docker run --rm -v english-tutor_tutor-data:/data -v "$PWD":/backup alpine \
    tar -czf /backup/tutor-data-$(date +%F).tar.gz -C /data .

# 恢复
docker compose down
docker run --rm -v english-tutor_tutor-data:/data -v "$PWD":/backup alpine \
    tar -xzf /backup/tutor-data-YYYY-MM-DD.tar.gz -C /data
docker compose up -d
```

建议把备份命令放进服务器的 cron，每天一次。

## 环境变量一览

| 变量 | 位置 | 说明 | 默认值 |
|---|---|---|---|
| `LLM_API_KEY` | `backend/.env` | LLM 密钥（必填） | 无 |
| `LLM_PROVIDER` | `backend/.env` | `kimi` / `deepseek` / `anthropic` / `fake` | `kimi` |
| `LLM_MODEL` | `backend/.env` | 模型名 | `kimi-k3` |
| `APP_ENV` | `backend/.env` | 运行环境标记 | `development` |
| `DATABASE_URL` | compose 覆盖 | 容器内固定指向 `/data` 卷 | `sqlite:////data/english_tutor.db` |
| `SKILLS_DIR` | compose 覆盖 | 容器内 skills 路径 | `/skills` |
| `SESSION_TIME_LIMIT_MINUTES` | `backend/.env` | 每节课每日软性时长（分钟）。到时自动收尾并暂停，没上完的环节第二天继续 | `15` |
| `WEB_PORT` | compose 环境 | 对外 Web 端口 | `80` |

## 故障排查

| 症状 | 排查 |
|---|---|
| `docker compose up` 报 `.env` 找不到 | 确认 `backend/.env` 存在（不是 `.env.example`） |
| 后端启动即退出 | `docker compose logs backend` — 多半是 `LLM_API_KEY` 为空或拼写错误 |
| 页面能开但提交后一直转圈/报错 | LLM 调用失败：`docker compose logs -f backend` 看是 key 无效、额度不足还是服务器无法访问外网 API |
| 浏览器打不开 | 确认 `docker compose ps` 端口映射、服务器防火墙、访问的是服务器 IP 而非 localhost |
| 构建时 npm/pip 下载慢 | 服务器需要能访问外网拉镜像和依赖；可在 Dockerfile 里换国内镜像源 |

## 安全边界（LAN 部署）

- 应用当前**没有登录认证**，默认信任局域网内所有设备 —— 适合家庭内网，**不要直接暴露到公网**。如需公网访问，先加反向代理 + Basic Auth 或等 P2 之后的多用户/auth 版本。
- `LLM_API_KEY` 只存在于服务器 `backend/.env`，不会进入前端镜像或浏览器。
- 学生数据不出局域网；唯一的出站流量是服务器到 LLM API 的 HTTPS 请求。
