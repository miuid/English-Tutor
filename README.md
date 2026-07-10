# Prompt example

```
这是一个已有规划的项目(English-Tutor)。请先按顺序读 CLAUDE.md → MEMORY.md →
IMPLEMENTATION-PLAN.md 了解现状和约定,然后开始实现计划里第一个未打勾的步骤
「0.1 Repo scaffold + tooling」。

要求:
- 严格遵守 IMPLEMENTATION-PLAN.md 顶部的 locked tech choices 和 global definition of done。
- 只做 0.1 这一步,改动保持外科手术式,不要提前做后面的步骤。
- 满足该步骤的 "Done when" 判据(/health 返回 200、pytest 绿),并写上对应测试。
- 完成后:在 IMPLEMENTATION-PLAN.md 勾选 0.1,并在 MEMORY.md §11 追加一条会话日志。
- 动手前先简述你的计划,如有歧义先问我。
```