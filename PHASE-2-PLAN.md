# English Tutor — Phase 2 规划:技能深度扩展 + Beta

> 承接 `IMPLEMENTATION-PLAN.md`(MVP P0–P5,已完成)。本文件是第二阶段的**规划文档**,不是施工清单——确认方向与决策点后,再把它拆成可勾选的实施步骤(沿用原 resume protocol)。
> 两条工作线:**A. 技能深度扩展**(Year 9–12、persuasive/imaginative);**B. Beta 功能**(从 1 个学生走向 5–10 个真实家庭)。

Last updated: 2026-07-31(规划稿,待 owner 确认决策点)

---

## 0. 现状盘点(规划的出发点)

**已具备(MVP):**
- 8 个 v1 skills,`year_level` / `text_type` 已是标准输入(契约留了口子),但**内容深度全部锚定 Year 8 · analytical**(rubric、词汇分层、register、范例)。
- 数据模型为多年级/多课程留了缝(`curriculum_outcome.curriculum` 列),种子数据只有 Year 8 analytical。
- Eval harness 支持按 skill 跑 fixture;live eval 8/8 PASS(DeepSeek)。
- 每日循环 API + UI + 进度视图 + 交互日志 + 数据删除 + docker compose。

**缺口:**
- 没有任何 persuasive / imaginative 的教学内容深度;`check-structure` 只会 PEEL/TEEL。
- 没有 Year 9–12 的 rubric 标准描述、词汇天花板、任务规格、课程种子。
- `diagnose-errors` 的路由表只有两个教练技能,没有议论文/记叙文专项教练。
- MEMORY §8 "Later" 里列的 `fix-mechanics`、spaced-review(热身 retrieval)、元认知教练未建。
- 单用户硬编码路径:没有学生档案概念(年级、主攻文本类型存不住),第二个家庭无法上车。
- 动机层、家长层、周测(weekly timed mock)仍是 PRD 里的承诺,未交付。

---

## 1. 需要先拍板的 4 个决策点

| # | 决策 | 建议 | 备选 |
|---|---|---|---|
| D1 | **Beta 分发模式** | **每户本地单租户**(docker compose,与 MVP 一致)。隐私故事不变、零运维成本、无需建 auth 基础设施;"多家庭"= 多份本地部署 | 托管多租户(原 GA 计划)——工作量大:auth、Postgres、部署、合规,建议仍留 GA |
| D2 | **Year 11–12 时机** | 本阶段只建**框架 + 种子结构**(QCE IA1/IA2/IA3/EA 仪器建模),内容深度等 Beta 家庭里有 senior 学生再灌 | 现在就全做——研究成本最高、无真实用户验证,性价比低 |
| D3 | **家长可见边界** | 家长默认看**趋势/等级/时长/目标**,不看作文全文;学生可一键分享单篇。保护练习安全感(MEMORY §4 主题5 的"safe practice space") | 全透明——可能抑制学生真实练习意愿 |
| D4 | **扩展顺序** | **先纵深保护现有用户**(Y9 analytical,孩子 2027 年 2 月升 Year 9),再横向补文本类型,最后 Beta 功能 | 先 Beta 功能——但没有 Y9 深度,第一个用户明年 2 月就"毕业"出产品 |

---

## 2. Track A — 技能深度扩展(P6–P10)

### 架构核心:Reference Pack(参考资料包)机制

技能逻辑保持通用,**内容深度全部下沉为按 (text_type × year_band) 组织的参考文件**,executor 按输入组合只注入匹配的那一个包(控 token、控质量):

```
skills/<skill>/
  SKILL.md                       # 通用方法,引用"匹配的 pack"
  references/
    shared/                      # 跨类型通用(如 PEEL 通则)
    analytical/year-8/           # 现有内容迁移于此
    analytical/year-9-10/
    analytical/year-11-12/
    persuasive/year-8-10/        # rubric、修辞手法库、论证结构、任务规格
    imaginative/year-8-10/       # rubric、叙事结构、意象/声音、任务规格
```

Year band 只分三档:`year-8`、`year-9-10`、`year-11-12`(QCAA 标准描述在 9/10 连续变化,senior 换 ISMG 体系,按年做文件是浪费)。

### P6 — 技能框架泛化(M ilestone,L,~2 sessions)

1. **6.1 Pack 目录约定 + loader/executor 改造**:loader 递归收集 references;executor 按 `(text_type, year_band)` 选择注入的 pack;无匹配时落到 `shared/` + 最近档,并在输出中标注降级。现有 Year 8 内容原样迁移,行为不变(回归保护)。
   - Done when: pytest 全绿;live eval 8/8 仍 PASS;一个"不存在的组合"请求返回降级标注而非报错。
2. **6.2 学生档案 + session 上下文**:DB 增加 student profile 字段(`year_level`、`focus_text_types`);`POST /api/sessions` 从档案自动带 `year_level`/`text_type`(可覆盖);前端创建/编辑档案。
   - Done when: 两个不同档案的 student 开 session,prompt 里注入不同的 year_level;测试覆盖。
3. **6.3 Eval fixture 矩阵**:eval harness 支持一个 skill 多个 fixture(按 `sample-NN` 编号 + frontmatter 标注 band/text_type);scorecard 按组合分组。
   - Done when: 同一 skill 跑 2 个不同 band 的 fixture 并分组出分。

### P7 — Persuasive 深度,Year 8–10(L,~2 sessions)

4. **7.1 Persuasive reference packs**(研究驱动):论证结构(thesis → 3 argument blocks → rebuttal → conclusion)、修辞手法库(ethos/pathos/logos、rhetorical question、tricolon、anaphora…按 band 分层)、QCAA persuasive A–E 标准描述、任务规格。出处:`reaserch.md` + `Queensland English Tutoring Blueprint.md`,每条声明可溯源。
5. **7.2 新技能 `strengthen-argument`**(第 9 个 skill):诊断论证链薄弱点(claim 无理由 / reason 无证据 / 缺 rebuttal),教练式修复,遵守全部 6 条全局 guardrails + 黄金 examples。
   - Done when: 按 `skills/README.md` 约定成包;`diagnose-errors` 路由表加入;live eval PASS。
6. **7.3 种子 + 循环接线**:Year 8–10 persuasive outcomes 入 `curriculum_outcome`;`model-response`/`guided-practice`/`independent-task`/`give-feedback` 的 persuasive pack 就位后,全循环以 persuasive 跑通一次端到端。
   - Done when: 以 text_type=persuasive 走完整 daily loop;rubric_score 落库;eval 全绿。

### P8 — Imaginative 深度,Year 8–10(L,~2 sessions)

7. **8.1 Imaginative reference packs**:叙事结构(orientation → complication → climax → resolution)、人物/场景/视角、show-don't-tell 与感官意象、QCAA imaginative 标准描述。
8. **8.2 新技能 `craft-voice`**(第 10 个 skill):诊断 telling-vs-showing、意象单薄、视角漂移;教练式修复。
9. **8.3 种子 + 循环接线**:同 P7.3,text_type=imaginative 端到端。
   - Done when 同 P7 结构。

### P9 — Year 9–10 analytical 深度(M,~1–1.5 sessions)⏰ 2027 年 2 月前必须就位

10. **9.1 Year 9–10 analytical packs**:各 skill 的 9–10 档 rubric(A/B = discerning/purposeful…)、词汇天花板抬升、任务规格(更长篇幅、 unseen text)、register 从 Year 8 语气平滑过渡。
11. **9.2 种子 + fixture**:Year 9–10 QCAA analytical outcomes 入库;每核心 skill 加一个 year-9-10 fixture;live eval 扩展后仍全绿。
    - Done when: year_level=9 的 session 全循环跑通,A–E 判定引用 Year 9 标准描述。

### P10 — Year 11–12 senior 框架(L,择机)

12. **10.1 QCE 仪器建模**:Units 1–4 / IA1(analytical written)/ IA2(persuasive)/ IA3(imaginative)/ EA(external exam)建模进 `curriculum_outcome`;ISMG 判分维度与 A–E 的映射策略写成研究笔记。
13. **10.2 senior pack 骨架 + IA1 深度**:analytical/year-11-12 pack 先做 IA1(分析性论文),其余留空档等真实用户。
    - Done when: IA1 任务能以 senior 标准跑通反馈;映射笔记入库。

---

## 3. Track B — Beta 功能(B1–B6)

**Beta 定义:** 5–10 个 QLD 真实家庭(Year 8–10),每户本地部署,跑 8–12 周,验证留存与成绩趋势。

### B1 — Beta 分发与学生档案(M)

- 依 D1:每户一份本地部署。打磨 `docker compose up` 首跑体验(首次启动向导:创建学生档案、选年级、贴学校任务)。
- 学生档案:年级、主攻文本类型、弱项标签(来自 B2 baseline);数据**导出/备份**功能(本地 JSON 导出,换机/升级不丢进度)。
- Done when: 一台干净机器按 README 15 分钟内完成首 session;导出→删除→导入后进度无损。

### B2 — 入学诊断 baseline(M)

- 新技能 `baseline-assessment`(第 11 个):一次 15 分钟限时写作 → rubric 初评 → 生成学生档案(弱项排序、起始 A–E 基线、推荐主攻循环)。
- Done when: 新学生第一次使用即完成 baseline,档案写入;基线 rubric_score 出现在进度视图第 0 天。

### B3 — 补完教学循环(L)

- **新技能 `fix-mechanics`**(第 12 个):语法/拼写/标点教练——MVP 刻意没做(避免反馈摊大饼),Beta 作为 `diagnose-errors` 的第三条路由,仍受"≤2 next steps"约束。
- **新技能 `spaced-review`**(第 13 个):从 interaction_log + rubric_score 生成 2–3 题热身 retrieval(上周的手法/词汇),成为循环第 1 步(MVP-Plan §2 承诺过的"热身 retrieval"补交)。
- **每周限时模考**:`independent-task` 已有 assessment conditions;orchestrator 加 weekly-mock 模式(完整 QCAA 条件、完整 A–E summative 反馈),PRD §3 的承诺兑现。
- Done when: 日常循环 = retrieval → 目标 → I/we/you do → 反馈;每周一次 mock;A–E 趋势图区分日常与 mock 数据点。

### B4 — 动机层(M)

- **轻量 streak**:连续练习天数 + 每周目标(默认 4 sessions/周),断签不惩罚(温和恢复提示)。
- **等级升级庆祝**:rubric criterion 跨档(如 C→B)时的具体化表扬("你的 analysis 从概括升级到了机制解释")。
- **AI 人设语气设置**:档案里可选教练语气(温和/严格/幽默),写进 system prompt 而非改 skill 逻辑。
- 克制原则:不做积分商城/排行榜——动机服务于练习,不成 distraction。
- Done when: streak 与 level-up 事件有持久化 + UI;语气切换对同一输入产生可感知但不改变教学契约的输出。

### B5 — 家长层(M)

- **每周家长报告**:应用内视图 + 可打印 PDF( sessions 数、时长、各 criterion 趋势、本周亮点、下周建议);依 D3 默认不含作文全文。
- **目标协作**:家长与学生共设周目标(写进档案,循环开局时引用)。
- Done when: 家长视图独立于学生视图;PDF 生成;隐私边界有测试断言(家长接口不返回 attempt 全文)。

### B6 — Beta 运营就绪(M)

- **成本控制**:per-stage 模型路由——重判断阶段(diagnose/coach/feedback)用强模型,轻阶段(set-criteria/retrieval)用 cheap 档(DeepSeek flash 级);adapter 层按 loop_stage 选模型。
- **隐私安全的 telemetry**:本地聚合使用指标(不上报内容),beta 家庭一键导出"反馈包"发给开发者。
- **Beta 手册**:安装指南、家长 onboarding 一页纸、问题反馈渠道、每周 check-in 模板。
- Done when: 模型路由 config 化并有测试;一次 beta 家庭问题从反馈包到定位 <10 分钟。

---

## 4. 建议执行顺序(可调整)

```
P6 框架泛化 ──► P9 Y9–10 analytical ──► P7 persuasive ──► P8 imaginative
      │                                                    │
      └──► B1 分发+档案 ──► B2 baseline ──► B3 补完循环 ──► B4 动机 ──► B5 家长 ──► B6 运营 ──► 招募 5–10 家庭
                                                                                          │
                                                              P10 senior 框架 ◄── 按 beta 家庭构成择机
```

理由:P6 是一切的地基;P9 保护第一个用户 2027 年 2 月的连续性(最硬的死线);P7/P8 补文本类型后产品对 beta 家庭才"完整";Beta 功能做完 B1–B3 即可小步招募(前 2–3 个家庭),B4/B5 边跑边补;P10 等有真实 senior 用户再深入。

## 5. Beta 成功指标

- **North Star 不变**:各 criterion A–E 趋势上行。
- **留存**:8 周内周均 ≥3 sessions 的家庭占比 ≥60%。
- **有效性**:baseline vs 第 8 周 mock 的 criterion 中位数提升 ≥1 档(如 D→C)的学生 ≥50%。
- **家长**:周报告打开率;期末家长访谈 NPS。

## 6. 明确不做(本阶段)

- 托管多租户、真实账号体系、支付(→ GA)。
- NESA/其他州课程(`test-context.md` 备着,QLD 验证后再说)。
- 语音口语、费曼教 AI、角色审问(黑白天鹅清单最低优先级,继续压后)。
- 积分商城/排行榜式重度游戏化。

## 7. 开放问题(待 owner)

1. D1–D4 四个决策点确认(§1)。
2. Beta 招募渠道:朋友家庭?学校家长群?决定 B6 手册的写法。
3. Year 9–12 的 QCAA 标准描述文本:从 `reaserch.md` 抽取够用,还是需要补官方 syllabus PDF 原件?
