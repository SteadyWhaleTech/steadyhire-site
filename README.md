# 稳聘公开页面

稳聘 iOS 的首页、帮助中心、隐私政策和用户协议，用 GitHub Pages 发布。App Store Connect 里的支持网址和隐私政策网址指向这里。

| 页面 | 来源 |
| --- | --- |
| `privacy.html`、`terms.html` | 由脚本从 App 的 `ios/SteadyHire/Application/LegalDocuments.swift` 生成，和 App 内一字不差 |
| `support.html` | 本仓库的 `support.md` |
| `index.html` | `scripts/build.py` 里的模板 |

App 里的协议改了，或者要改帮助文章：

```bash
python3 -I scripts/build.py <SteadyHire 仓库路径>
```

生成后提交推送，Pages 会自动更新。不要直接改 `.html`，下次生成会被覆盖。
