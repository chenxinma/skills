# Skills Repository

个人开发的 AI 助手技能（Skills）归集，方便在 opencode、claude code、openclaw 等环境进行安装部署。

## 技能列表

### 1. Email Assistant

**功能**: 智能邮件管理 API 交互技能

- 自然语言邮件查询和总结
- 邮件同步到本地数据库
- 支持 ag_ui 协议的 SSE 流式响应

**适用场景**: 需要与 Email Assistant API 交互，进行邮件查询、总结或同步操作

**文档**: [`skills/email-assistant/SKILL.md`](skills/email-assistant/SKILL.md)

---

### 2. Email Templater

**功能**: 批量邮件模板发送技能

- 支持 `{{占位符}}` 动态替换
- 按部门/收件人批量发送邮件
- 每个收件人对应固定附件
- 支持多种收件人格式

**适用场景**: 指标填报、数据提报、周期性数据收集等批量邮件通知场景

**文档**: [`skills/email-templater/SKILL.md`](skills/email-templater/SKILL.md)

---

### 3. ETF Grid Trading Optimizer

**功能**: ETF/股票网格交易参数优化

- 基于历史波动率计算网格参数
- 自动计算网格间距和网格数量
- 支持多种数据源（NetEase、AKShare、TuShare）

**适用场景**: 网格交易策略分析、ETF/股票投资参数优化

**文档**: [`skills/etf-grid-trading/SKILL.md`](skills/etf-grid-trading/SKILL.md)

---

## 安装方法

### opencode

在项目中创建或编辑 `.opencode/skills.json`：

```json
{
  "skills": [
    "path/to/skills/email-assistant",
    "path/to/skills/email-templater",
    "path/to/skills/etf-grid-trading"
  ]
}
```

### Claude Code

在项目根目录创建 `.claude/skills/` 目录，将需要的技能目录复制进去。

### OpenClaw

将技能目录复制到项目的 skills 目录中。

---

## 目录结构

```
skills/
├── email-assistant/
│   ├── SKILL.md              # 技能定义文档
│   ├── scripts/
│   │   └── email_client.py   # Python 客户端示例
│   └── references/
│       └── ag-ui.md          # ag_ui 协议参考文档
├── email-templater/
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── send_batch_emails.py
│   │   └── render_template.py
│   ├── test_skill.py
│   └── package_skill.py
└── etf-grid-trading/
    ├── SKILL.md
    ├── README.md
    └── references/
        ├── sample_symbols.md
        └── strategy_guide.md
```

---

## 开发说明

每个技能目录包含：
- `SKILL.md` - 技能定义和说明文档（必需）
- `scripts/` - 相关工具脚本
- `references/` - 参考文档
- `assets/` - 资源文件（如有需要）

## License

MIT
