# Packaging Skills for Multiple Agents

This document describes how to package a "skill" (Agent Skill) inside
`SKILL-LIB/` so it works across different CLIs/agents — Claude Code, Codex,
OpenCode, Claude Agent SDK, Managed Agents — without rewriting it for each one.

## 1. What Agent Skills are

**Agent Skills** is an open spec created by Anthropic, not tied to Claude Code
specifically. It's used across Claude API (Managed Agents), Claude Agent SDK,
claude.ai, and has been adopted by other tools using the same convention —
including **OpenCode** and **OpenAI Codex**, per the [Agent Skills
spec](https://agentskills.io/home), now supported by 40+ AI tools. Core idea:

- A skill is **a folder**, not a single loose file.
- It must contain a `SKILL.md`.
- The agent only loads what it needs, in 3 tiers, to save context:
  1. **Tier 1 (startup)** — only `name` + `description` from the frontmatter go
     into the system prompt (~100 tokens/skill).
  2. **Tier 2 (when triggered)** — the full Markdown body of `SKILL.md` is
     loaded into context.
  3. **Tier 3 (on demand)** — supporting files (scripts, templates, reference
     docs) are only read when the agent actually opens them.

Because each surface (Claude Code / Codex / OpenCode / SDK / Managed Agents)
manages its own storage location and discovery mechanism, a skill doesn't
automatically show up in another tool — it has to be placed correctly or
symlinked. But if the shared core is packaged correctly, the skill's content
is fully reusable as-is.

## 2. Standard folder structure (portable)

```
skill-name/
├── SKILL.md          # Required
├── scripts/           # Optional — repeatable executable code (Python/bash...)
├── references/        # Optional — detailed docs, read only when needed
├── assets/            # Optional — templates, images, fonts, sample data
└── agents/            # Optional — config SPECIFIC to one agent (see section 4)
    └── openai.yaml     #   Read by Codex; other agents ignore it, unaware of it
```

This is the exact structure used both by Anthropic's original Agent Skills
docs and by Codex — not a coincidence, both follow the same community
convention. OpenCode reads this same structure natively too.

## 3. `SKILL.md` — required rules

```markdown
---
name: skill-name
description: State clearly what this skill does AND when it should be used.
---

# Skill name

Content: purpose, workflow, constraints, how to use files under scripts/,
references/, assets/ (if any).
```

Rules for `name` and the folder name:

- Lowercase letters, digits, hyphens (`-`) — no spaces, no capitals.
- Max 64 characters.
- The folder name and the `name` field in frontmatter must match.

Rules for `description`:

- Must answer both **what this skill does** and **when the agent should use
  it** (keywords, situations, phrases a user might say...). The agent relies
  solely on this line (at Tier 1) to decide whether to trigger the skill — a
  vague description means the skill never fires at the right moment.
- Write in English if the skill needs to run reliably across multiple
  agents/locales, but it's fine to include Vietnamese keywords in quotes if
  the skill serves Vietnamese-speaking users (see
  `technext-daily-report/SKILL.md` as an example).

## 4. Extended frontmatter — keep it in `agents/`, never in `SKILL.md`

Some agents have their own behavior-configuration fields, e.g.:

| Agent | Field/file | Purpose |
|---|---|---|
| Claude Code | `allowed-tools`, `user-invocable`, `model`, `append-system-prompt` (frontmatter) | Pre-approve tools, who can call `/skill-name`, force a model, inject system prompt |
| Codex | `agents/openai.yaml` (separate file) | Invocation policy, interface |
| OpenCode | (native skill tool reads only `name`/`description`; unknown frontmatter keys are ignored) | — |

**Don't** put fields like `allowed-tools` directly into `SKILL.md`'s
frontmatter if you want the skill to be reusable elsewhere. Most agents will
silently ignore unknown YAML keys (no error), but to keep meaning
unambiguous across agents, put agent-specific config in an `agents/` folder
instead. `SKILL.md` itself should carry only the two standard fields: `name`,
`description`.

## 5. Scripts / references / assets — write them neutrally

- **`scripts/`**: code must run with common tooling (standard Python/bash), and
  must not call an MCP tool or internal integration that only exists in one
  specific agent.
- **`references/`**: longer reference material the agent only reads when
  needed — don't repeat what's already in `SKILL.md`.
- **`assets/`**: templates/sample data. If it's an HTML/template reused across
  runs (like the two TechNext skills), keep the asset file self-contained —
  no hardcoded OS paths or tool-specific dependencies.
- Only add these folders when actually needed — don't create a `README.md` or
  duplicate documentation without a specific reason to.

## 6. One source of truth, deployed via symlink

Each agent scans skills from its own location:

| Agent | Personal/global location | Project location |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| Codex | `~/.codex/skills/<name>/` or `$CODEX_HOME/skills/<name>/` | (version-dependent) |
| OpenCode | `~/.config/opencode/skills/<name>/` | `.opencode/skills/<name>/` — **and it also reads `.claude/skills/` and `.agents/skills/` directly**, so if a project already has `.claude/skills/`, OpenCode picks it up with zero extra setup |

Recommended approach: keep the canonical copy in `SKILL-LIB/<name>/`, then
**symlink** (don't copy) it into the locations above. Edit once, every agent
sees the latest version — avoids drift between copies.

```bash
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.claude/skills/technext-daily-report
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.codex/skills/technext-daily-report
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.config/opencode/skills/technext-daily-report
```

Since OpenCode reads `.claude/skills/` natively, if the target project already
has a `.claude/skills/` folder, you often don't need a separate OpenCode
symlink at all for *project*-scoped skills — only for the global/personal
`~/.config/opencode/skills/` location.

## 7. What about OpenCode + DeepSeek (or any other backing model)?

Skill packaging is a **harness-level** mechanism, not a model-level one. In
OpenCode's case, skills are exposed to the model as a native "skill" tool: the
model sees the `name`/`description` list, decides to call the tool, and the
harness then injects the full `SKILL.md` body into context. This layer sits
*above* the model — it works the same way regardless of which model backend
OpenCode is configured with (GLM, DeepSeek, GPT, Claude, etc., including the
`agentrouter/glm-5.3` setup in this project's `opencode.json`).

Practical implications when the backing model is DeepSeek (or any
OpenAI-compatible model reached through a router like AgentRouter):

- **No packaging changes needed.** The same `SKILL.md` + `assets/` folder
  used for Claude Code/Codex works unmodified — OpenCode's skill tool doesn't
  care what model is downstream.
- **Tool-calling reliability matters more than usual.** OpenCode's skill
  mechanism depends on the model correctly calling the "load skill" tool.
  Function/tool-calling quality varies across DeepSeek model variants and
  provider implementations — if skills seem to never trigger, first verify
  the model actually supports OpenAI-style tool calling reliably through
  that provider, independent of the skill's packaging.
- **`description` quality matters even more.** Since Tier 1 is the *only*
  signal a smaller/cheaper model gets to decide whether to invoke a skill,
  a vague or overly clever description is more likely to fail silently with
  a weaker model than with a stronger one. Keep it literal and keyword-rich.
- **No frontmatter is DeepSeek-specific.** There is no `agents/deepseek.yaml`
  convention (unlike Codex's `agents/openai.yaml`) — DeepSeek is just a model
  choice inside OpenCode's config, not a distinct "agent surface" with its
  own skill discovery rules.

## 8. Validate before shipping

- Codex has a built-in convention: `scripts/quick_validate.py path/to/skill-name`.
- Claude Code has no equivalent validator — check by hand:
  - `name` ≤ 64 chars, lowercase + hyphens.
  - `description` states both "what" and "when".
  - No stray fields in `SKILL.md` frontmatter (moved to `agents/` if needed).
- For OpenCode specifically: `SKILL.md` must be spelled in **all caps**
  exactly, and skill names must be unique across every location OpenCode
  scans (`.opencode/skills`, `~/.config/opencode/skills`, `.claude/skills`,
  `.agents/skills`) — a duplicate name in two locations can hide one copy.

## 9. Real example in this repo

```
SKILL-LIB/
├── technext-daily-report/
│   ├── SKILL.md              # only name + description
│   └── assets/
│       └── report-template.html
└── technext-morning-plan/
    ├── SKILL.md              # only name + description
    └── assets/
        └── plan-template.html
```

Both are packaged in a fully portable way: no `allowed-tools`/`agents/`
overrides, because the content doesn't depend on any one agent's internal
mechanism — the Google Drive/local-folder references in the body are
**business context**, not agent-specific syntax, so they carry over as long
as the target agent has an equivalent way to reach those destinations.

## 10. Summary checklist

1. One skill = one folder, containing `SKILL.md`.
2. `SKILL.md` frontmatter has only `name` + `description`.
3. `description` states both the function and the trigger conditions.
4. Agent-specific fields/config → live under `agents/`, never in the shared
   frontmatter.
5. `scripts/`, `references/`, `assets/` are added only when truly needed, and
   written neutrally (not tied to one agent).
6. One canonical source (`SKILL-LIB/`), deployed to each agent via symlink.
7. OpenCode reads `.claude/skills/` directly — check before assuming you need
   a separate OpenCode copy.
8. The backing model (Claude, GLM, DeepSeek, GPT...) doesn't change how a
   skill is packaged — only how reliably it gets *triggered*, which is a
   `description`-quality and tool-calling-reliability concern, not a
   packaging-format one.
9. Validate before calling it done — name, length, description, clean
   frontmatter, and (for OpenCode) unique names across all scanned locations.

---

# Đóng gói Skill dùng chung cho nhiều Agent

Tài liệu này mô tả cách đóng gói một "skill" (Agent Skill) trong `SKILL-LIB/`
sao cho dùng được ở nhiều CLI/agent khác nhau — Claude Code, Codex, OpenCode,
Claude Agent SDK, Managed Agents — mà không phải viết lại cho từng nơi.

## 1. Agent Skills là gì

**Agent Skills** là một spec mở của Anthropic, không ràng buộc vào riêng
Claude Code. Nó được dùng xuyên suốt Claude API (Managed Agents), Claude Agent
SDK, claude.ai, và đã được các tool khác áp dụng theo cùng quy ước — bao gồm cả
**OpenCode** và **OpenAI Codex**, theo [spec Agent
Skills](https://agentskills.io/home), hiện được hỗ trợ bởi hơn 40 AI tool. Ý
tưởng cốt lõi:

- Một skill là **một thư mục**, không phải một file rời.
- Bên trong bắt buộc có `SKILL.md`.
- Agent chỉ nạp phần cần thiết theo 3 tầng, để không tốn context:
  1. **Tầng 1 (lúc khởi động)** — chỉ `name` + `description` trong frontmatter
     được đưa vào system prompt (~100 token/skill).
  2. **Tầng 2 (khi được kích hoạt)** — toàn bộ nội dung Markdown của
     `SKILL.md` được nạp vào ngữ cảnh.
  3. **Tầng 3 (khi thật sự cần)** — các file phụ trợ (script, template, tài
     liệu tham khảo) chỉ được đọc khi agent chủ động mở tới.

Vì mỗi "surface" (Claude Code / Codex / OpenCode / SDK / Managed Agents) tự
quản lý nơi lưu và cách khám phá skill riêng, một skill không tự động xuất
hiện ở tool khác — phải đặt đúng chỗ hoặc symlink. Nhưng nếu đóng gói đúng
phần lõi chung, nội dung skill thì dùng lại được nguyên vẹn.

## 2. Cấu trúc thư mục chuẩn (dùng chung được)

```
skill-name/
├── SKILL.md          # Bắt buộc
├── scripts/           # Tùy chọn — code thực thi lặp lại (Python/bash...)
├── references/        # Tùy chọn — tài liệu chi tiết, đọc khi cần
├── assets/            # Tùy chọn — template, ảnh, font, dữ liệu mẫu
└── agents/            # Tùy chọn — cấu hình RIÊNG từng agent (xem mục 4)
    └── openai.yaml     #   Codex đọc; agent khác bỏ qua vì không biết tới
```

Đây chính là cấu trúc mà cả tài liệu Agent Skills gốc của Anthropic lẫn Codex
đều dùng — không phải trùng hợp, mà vì cả hai theo cùng một quy ước cộng
đồng. OpenCode cũng đọc trực tiếp đúng cấu trúc này.

## 3. `SKILL.md` — quy tắc bắt buộc

```markdown
---
name: skill-name
description: Nêu rõ skill làm gì VÀ khi nào nên dùng nó.
---

# Tên skill

Nội dung: mục đích, quy trình, ràng buộc, cách dùng các file trong scripts/,
references/, assets/ (nếu có).
```

Quy tắc cho `name` và tên thư mục:

- Chữ thường, số, dấu gạch ngang (`-`) — không khoảng trắng, không hoa.
- Tối đa 64 ký tự.
- Tên thư mục và `name` trong frontmatter phải khớp nhau.

Quy tắc cho `description`:

- Phải trả lời được cả hai câu hỏi: **skill này làm gì** và **khi nào agent
  nên dùng nó** (từ khóa, tình huống, câu nói của user...). Agent chỉ dựa vào
  dòng này (ở tầng 1) để quyết định có kích hoạt skill hay không — mô tả mơ
  hồ = skill không bao giờ được gọi đúng lúc.
- Nên viết bằng tiếng Anh nếu skill cần chạy tốt trên nhiều agent/locale khác
  nhau, nhưng có thể chứa từ khóa tiếng Việt trong ngoặc kép nếu skill phục vụ
  người dùng nói tiếng Việt (xem ví dụ `technext-daily-report/SKILL.md`).

## 4. Frontmatter mở rộng — chỉ để trong `agents/`, không nhét vào `SKILL.md`

Một số agent có field cấu hình hành vi riêng, ví dụ:

| Agent | Field/file riêng | Mục đích |
|---|---|---|
| Claude Code | `allowed-tools`, `user-invocable`, `model`, `append-system-prompt` (frontmatter) | Duyệt trước tool, ai được gọi `/skill-name`, ép model, chèn system prompt |
| Codex | `agents/openai.yaml` (file riêng) | Chính sách gọi skill, giao diện |
| OpenCode | (native skill tool chỉ đọc `name`/`description`; field lạ bị bỏ qua) | — |

**Không** nhét các field như `allowed-tools` thẳng vào frontmatter của
`SKILL.md` nếu muốn skill dùng chéo được — dù phần lớn agent thường bỏ qua
field lạ (YAML parser không lỗi), nhưng để rõ ràng và tránh hiểu nhầm ngữ
nghĩa field giữa các agent, hãy tách cấu hình riêng đó ra thư mục `agents/`.
`SKILL.md` chỉ giữ đúng 2 field chuẩn: `name`, `description`.

## 5. Nội dung script/reference/asset — viết trung lập

- **`scripts/`**: code phải tự chạy được bằng công cụ phổ thông
  (Python/bash chuẩn), không gọi tool/MCP nội bộ chỉ có ở một agent cụ thể.
- **`references/`**: tài liệu tham khảo dài, agent chỉ đọc khi cần — không
  lặp lại nội dung đã có trong `SKILL.md`.
- **`assets/`**: template/dữ liệu mẫu. Nếu là HTML/template dùng lại nhiều
  lần (như 2 skill TechNext), giữ file asset độc lập, không gắn cứng đường
  dẫn hệ điều hành hay tool riêng.
- Chỉ thêm các thư mục này khi thực sự cần — không tạo `README.md` hay tài
  liệu trùng lặp nếu không có yêu cầu cụ thể.

## 6. Một nguồn duy nhất, deploy bằng symlink

Mỗi agent quét skill từ vị trí riêng của nó:

| Agent | Vị trí cá nhân/global | Vị trí theo project |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| Codex | `~/.codex/skills/<name>/` hoặc `$CODEX_HOME/skills/<name>/` | (tùy version) |
| OpenCode | `~/.config/opencode/skills/<name>/` | `.opencode/skills/<name>/` — **và cũng đọc trực tiếp `.claude/skills/` lẫn `.agents/skills/`**, nên nếu project đã có `.claude/skills/`, OpenCode nhận luôn không cần setup thêm |

Cách khuyến nghị: giữ bản gốc trong `SKILL-LIB/<name>/`, rồi **symlink**
(không copy) vào các vị trí trên. Sửa một chỗ, mọi agent đều thấy bản mới
nhất — tránh tình trạng lệch bản giữa các nơi.

```bash
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.claude/skills/technext-daily-report
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.codex/skills/technext-daily-report
ln -s "/path/to/SKILL-LIB/technext-daily-report" ~/.config/opencode/skills/technext-daily-report
```

Vì OpenCode đọc trực tiếp `.claude/skills/`, nếu project đích đã có sẵn thư
mục `.claude/skills/`, thường **không cần** symlink riêng cho OpenCode ở cấp
project nữa — chỉ cần symlink cho vị trí cá nhân/global
`~/.config/opencode/skills/` mà thôi.

## 7. Còn OpenCode + DeepSeek (hoặc model backend bất kỳ) thì sao?

Đóng gói skill là cơ chế ở **tầng harness** (công cụ CLI), không phải tầng
model. Với OpenCode, skill được đưa cho model dưới dạng một native tool
"skill": model thấy danh sách `name`/`description`, quyết định gọi tool đó, và
harness sẽ nạp toàn bộ nội dung `SKILL.md` vào ngữ cảnh. Lớp này nằm *phía
trên* model — hoạt động giống hệt nhau bất kể OpenCode đang cấu hình chạy
model nào (GLM, DeepSeek, GPT, Claude...), kể cả setup
`agentrouter/glm-5.3` đang có trong `opencode.json` của project này.

Những điều cần lưu ý thực tế khi model backend là DeepSeek (hoặc bất kỳ model
tương thích OpenAI nào chạy qua router như AgentRouter):

- **Không cần đổi cách đóng gói.** Cùng một `SKILL.md` + `assets/` dùng cho
  Claude Code/Codex vẫn chạy nguyên vẹn — cơ chế skill của OpenCode không
  quan tâm model phía sau là gì.
- **Độ tin cậy của tool-calling quan trọng hơn bình thường.** Cơ chế skill
  của OpenCode phụ thuộc vào việc model gọi đúng tool "load skill". Chất
  lượng function/tool-calling khác nhau tùy biến thể DeepSeek và cách nhà
  cung cấp triển khai — nếu thấy skill không bao giờ được kích hoạt, hãy
  kiểm tra trước xem model có thực sự hỗ trợ tool calling kiểu OpenAI ổn
  định qua provider đó không, tách biệt với việc đóng gói skill có đúng hay
  không.
- **Chất lượng `description` càng quan trọng hơn.** Vì tầng 1 là tín hiệu
  **duy nhất** mà một model nhỏ/rẻ hơn có để quyết định có gọi skill hay
  không, một description mơ hồ hoặc viết kiểu "khôn khéo" dễ âm thầm thất
  bại với model yếu hơn so với model mạnh. Viết thẳng, nhiều từ khóa.
- **Không có frontmatter riêng cho DeepSeek.** Không tồn tại quy ước kiểu
  `agents/deepseek.yaml` (khác với `agents/openai.yaml` của Codex) — DeepSeek
  chỉ là một lựa chọn model trong cấu hình của OpenCode, không phải một
  "agent surface" riêng có luật khám phá skill của riêng nó.

## 8. Validate trước khi phát hành

- Codex có sẵn quy ước: `scripts/quick_validate.py path/to/skill-name`.
- Claude Code không có script chuẩn hóa tương đương — tự kiểm tra bằng tay:
  - `name` ≤ 64 ký tự, đúng định dạng chữ thường + gạch ngang.
  - `description` nêu rõ "làm gì" + "khi nào dùng".
  - Không có field lạ trong frontmatter `SKILL.md` (đã chuyển hết qua
    `agents/` nếu cần).
- Riêng với OpenCode: tên file `SKILL.md` phải viết **đúng hoa toàn bộ**
  chính xác như vậy, và tên skill phải **duy nhất** trên mọi vị trí OpenCode
  quét (`.opencode/skills`, `~/.config/opencode/skills`, `.claude/skills`,
  `.agents/skills`) — trùng tên ở hai nơi có thể khiến một bản bị ẩn đi.

## 9. Ví dụ thực tế trong repo này

```
SKILL-LIB/
├── technext-daily-report/
│   ├── SKILL.md              # chỉ name + description
│   └── assets/
│       └── report-template.html
└── technext-morning-plan/
    ├── SKILL.md              # chỉ name + description
    └── assets/
        └── plan-template.html
```

Cả hai đóng gói đúng chuẩn portable: không có `allowed-tools`/`agents/` riêng
vì nội dung không phụ thuộc cơ chế riêng của một agent cụ thể — phần liên
quan tới Google Drive/local folder trong nội dung là **bối cảnh nghiệp vụ**,
không phải cú pháp đặc thù, nên vẫn dùng chéo được miễn agent đích có cách
truy cập tương đương.

## 10. Tóm tắt quy tắc

1. Một skill = một thư mục, có `SKILL.md`.
2. `SKILL.md` frontmatter chỉ có `name` + `description`.
3. `description` phải nêu rõ chức năng và thời điểm dùng.
4. Field/cấu hình riêng của từng agent → để trong `agents/`, không nhét vào
   frontmatter chung.
5. `scripts/`, `references/`, `assets/` chỉ thêm khi thật sự cần, viết trung
   lập không phụ thuộc 1 agent.
6. Một nguồn gốc duy nhất (`SKILL-LIB/`), deploy ra các agent bằng symlink.
7. OpenCode đọc trực tiếp `.claude/skills/` — kiểm tra trước khi giả định
   cần một bản copy riêng cho OpenCode.
8. Model backend (Claude, GLM, DeepSeek, GPT...) không thay đổi cách đóng
   gói skill — chỉ ảnh hưởng độ tin cậy của việc *kích hoạt* skill, vốn là
   vấn đề chất lượng `description` và tool-calling, không phải vấn đề format
   đóng gói.
9. Validate lại trước khi coi là "xong" — tên, độ dài, description,
   frontmatter sạch, và (với OpenCode) tên duy nhất trên mọi vị trí quét.
