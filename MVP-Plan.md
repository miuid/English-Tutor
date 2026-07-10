# English Tutor — MVP 规划

_定位:面向澳洲 Year 8–12 学生的课后英语提分助手(非替代学校)。第一个真实用户是一名 Year 8 学生,长期目标扩展为面向数百至数千人的产品。_

## 1. 范围决策(重要)

存在一个张力:既想要"MVP",又想 MVP 覆盖 8–12 全年级 + 所有能力板块。解法是把"设计范围"和"交付范围"分开:

- **设计范围(第一天就留好口子):** 数据模型、skill 框架、课程建模、LLM 适配层都按 Year 8–12 + 多能力板块设计,后续加内容不改架构。
- **交付范围(MVP 第一刀):** 只把 **Year 8 · QCAA · analytical/essay writing** 的内容深度灌满,并且反馈引擎专门优化学生当前两个短板:
  1. **词汇平**(flat / plain vocabulary)
  2. **结构弱**(段落与篇章结构)

先把一个年级 × 一个板块做到 A+ 深度,再横向扩年级、纵向扩板块。

## 2. MVP 核心循环(学生每天做什么)

一次 15–20 分钟的 session,直接对应 research 里的 VTLM / GRR「I do → we do → you do」:

1. **热身 retrieval** — 快速复习上次的手法/词汇。
2. **设定目标** — 生成 learning intention + "I can…" success criteria。
3. **示范 (I do)** — AI think-aloud 示范一个高质量分析段落(PEEL/TEEL)。
4. **引导 (we do)** — 师生共写,脚手架逐步撤下。
5. **独立 (you do)** — 学生独立写一个段落(MVP 聚焦"一段"而非整篇,降低启动阻力)。
6. **反馈复盘** — 只针对结构 + 词汇给 1–2 个最高杠杆改进点,学生做一次"重写循环"。

## 3. MVP 必要能力(agent skills)

每个都是独立、可版本化的 skill 文件,与具体 LLM 解耦:

| Skill | 作用 | 对应研究依据 |
|---|---|---|
| `set-success-criteria` | 生成学生友好的目标与 "I can…" 标准 | HITS 设定目标 |
| `model-response` | think-aloud 示范范文(I do) | GRR / VTLM 显性教学 |
| `guided-practice` | 半脚手架共写(we do) | GRR |
| `independent-task` | 布置独立写作(you do) | GRR |
| `check-structure` | 诊断 PEEL/TEEL 结构缺失(**短板 1**) | QCAA 文本结构 outcome |
| `elevate-vocabulary` | 标出平淡词,给分层升级建议 + 解释语义差别(**短板 2**) | 学术词 / metalanguage |
| `diagnose-errors` | 归类错误类型(论点弱/证据未分析/衔接差) | APST 评估素养 |
| `give-feedback` | 按 QCAA rubric 出分 + 最多 2 个 next step | APST Std 5 / HITS 反馈 |

## 4. 架构(Python + React,本地优先但可扩展)

```
React (Vite)  ──HTTP──►  FastAPI  ──►  Teaching Engine (skills)
                            │                   │
                            │                   ▼
                            │            LLM Adapter Layer
                            │          ┌─────────┼─────────┐
                            ▼          ▼         ▼         ▼
                        SQLite     Anthropic  OpenAI    Ollama(本地)
                     (→Postgres)
```

设计原则:

- **LLM 适配层:** 统一 `LLMProvider` 接口 + 各家适配器,provider 由配置切换。这就是需求里的"可换模型",且换模型不动业务逻辑。
- **教学逻辑 = 数据/文件,不是代码:** skill 描述、prompt、rubric 都是可版本化的配置文件,方便持续调教学质量。
- **本地 MVP:** FastAPI + SQLite + React,目标 `docker compose up` 一键跑起。
- **为生产留口子:** 表结构、认证、多用户从一开始就设计;SQLite → Postgres 只改连接串;无状态后端便于水平扩展。
- **可评测:** 把"一次教学互动"记录成可回放的结构化数据,支持日后做教学质量回归测试。

## 5. 数据模型草图

- `curriculum_outcome` — QCAA strands / outcomes / sub-elements(Year 8–12 全建模,MVP 先填 Year 8)
- `skill` — 文学手法、文本类型、词汇分层库(带标签挂到 outcome)
- `student` / `session` / `attempt` — 学生、每次 session、每次写作尝试
- `feedback` — rubric 打分 + inline 批注 + next steps(可回放)
- `rubric` — QCAA 风格评分配置文件(版本化)

## 6. 建议的分阶段构建(每阶段带验收标准)

| 阶段 | 内容 | 验收(success criteria) |
|---|---|---|
| P0 | 项目脚手架 + LLM 适配层 | 配置切换 Ollama ↔ Anthropic,同一调用都能返回 |
| P1 | 课程 + rubric 数据模型 | Year 8 essay outcomes 能加载,任务可打标签 |
| P2 | 教学 skills + 每日循环(单段) | I do/we do/you do 端到端跑通一次 |
| P3 | 反馈引擎(专攻结构 + 词汇) | 给一段平淡/松散的文字,能精准诊断结构缺失 + 给 ≤2 个 next step + 词汇升级建议 |
| P4 | React 前端(每日循环 UI) | 学生能在浏览器里完整走完一次 session |
| P5 | 互动日志 + 小型评测集 | 回放一段已评作文,评分稳定可复现 |

## 7. 延后(不进 MVP)

- **Beta/GA:** 动机层(streak、成就、AI 人设)、家长层(周报、目标、隐私边界)
- **最低优先级:** 语音口语、费曼式"教 AI"、角色审问等实验玩法

## 8. 待定 / 下一步需要确认

- ~~MVP 用哪个模型~~ **已定(2026-07-10):单一云端 Claude Sonnet 4.6,适配层可切换;本地 Ollama 与分级路由延后。**
- 是否需要用户登录(单用户 MVP 可先跳过,但表结构预留)
- QCAA outcomes 结构化数据的来源(你的 research 文件已有大量素材,可直接抽取)
