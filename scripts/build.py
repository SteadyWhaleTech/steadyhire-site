"""生成稳聘的公开页面：首页、隐私政策、用户协议、帮助中心。

用法：python3 -I scripts/build.py <SteadyHire 仓库路径>
隐私政策和用户协议直接从 App 的 ios/SteadyHire/Application/LegalDocuments.swift 读取，保证网页和 App 内一字不差。
帮助中心来自本仓库的 support.md。
"""
import html, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
swift = (Path(sys.argv[1]) / "ios/SteadyHire/Application/LegalDocuments.swift").read_text()

def const(name):
    return re.search(rf'static let {name} = "([^"]*)"', swift).group(1)

OP, EMAIL, VERSION, DATE = const("operatorName"), const("contactEmail"), const("version"), const("effectiveDate")
SUPPORT_URL = "support.html"

def sections(kind):
    block = re.search(rf"static let {kind}: \[LegalSection\] = \[(.*?)\n    \]\n", swift, re.S).group(1)
    out = []
    for heading, paras in re.findall(r'LegalSection\(heading: "([^"]+)", paragraphs: \[(.*?)\]\)', block, re.S):
        texts = [p.replace("\\(op)", OP) for p in re.findall(r'"((?:[^"\\]|\\.)*)"', paras)]
        out.append((heading, texts))
    return out

def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text

CSS = """
:root { --teal: #178c85; --ink: #17212e; --muted: #5f6b78; --line: #e3e8ee; --bg: #f4f6f8; }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.75 -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; color: var(--ink); background: var(--bg); }
header { background: #fff; border-bottom: 1px solid var(--line); }
.bar { max-width: 760px; margin: 0 auto; padding: 14px 20px; display: flex; gap: 18px; align-items: center; flex-wrap: wrap; }
.bar a { color: var(--muted); text-decoration: none; font-size: 15px; }
.bar a.brand { color: var(--teal); font-weight: 700; font-size: 18px; margin-right: auto; }
.bar a.on { color: var(--ink); font-weight: 600; }
main { max-width: 760px; margin: 0 auto; padding: 28px 20px 60px; }
article, .card { background: #fff; border: 1px solid var(--line); border-radius: 16px; padding: 22px 24px; margin: 0 0 18px; }
h1 { font-size: 28px; line-height: 1.3; margin: 0 0 6px; }
h2 { font-size: 20px; line-height: 1.4; margin: 0 0 10px; }
h3 { font-size: 17px; margin: 20px 0 6px; }
.meta { color: var(--muted); font-size: 14px; margin: 0 0 22px; }
p { margin: 0 0 12px; }
ul, ol { padding-left: 22px; margin: 0 0 12px; }
table { width: 100%; border-collapse: collapse; margin: 6px 0 14px; font-size: 15px; }
th, td { border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: var(--bg); }
code { background: var(--bg); padding: 1px 5px; border-radius: 4px; }
a { color: var(--teal); }
.toc a { display: block; padding: 4px 0; }
footer { max-width: 760px; margin: 0 auto; padding: 0 20px 40px; color: var(--muted); font-size: 14px; }
"""

def page(name, title, body):
    nav = [("index.html", "首页"), ("support.html", "帮助中心"), ("privacy.html", "隐私政策"), ("terms.html", "用户协议")]
    links = "".join(f'<a href="{href}"{" class=\"on\"" if href == name else ""}>{label}</a>' for href, label in nav)
    doc = f"""<!doctype html>
<html lang="zh-Hans">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · 稳聘</title>
<style>{CSS}</style>
</head>
<body>
<header><nav class="bar"><a class="brand" href="index.html">稳聘</a>{links}</nav></header>
<main>
{body}
</main>
<footer>{html.escape(OP)} · 联系邮箱 <a href="mailto:{EMAIL}">{EMAIL}</a></footer>
</body>
</html>
"""
    (ROOT / name).write_text(doc)

def contact():
    return f"""<h3>联系我们</h3>
<p>运营者：{html.escape(OP)}<br>邮箱：<a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="{SUPPORT_URL}">稳聘帮助中心</a></p>"""

def legal(name, title, kind):
    parts = [f"<article><h1>{title}</h1><p class=\"meta\">版本 {VERSION} · 生效日期 {DATE}</p>"]
    for heading, texts in sections(kind):
        parts.append(f"<h3>{inline(heading)}</h3>")
        parts += [f"<p>{inline(t)}</p>" for t in texts]
    parts.append(contact() + "</article>")
    page(name, title, "\n".join(parts))

def markdown_blocks(lines):
    """support.md 用到的几种写法：段落、无序/有序列表、表格、粗体、行内代码。"""
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], [r for r in rows[2:]]
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
            continue
        m_ul, m_ol = re.match(r"- (.*)", line), re.match(r"\d+\. (.*)", line)
        if m_ul or m_ol:
            tag, pat = ("ul", r"- (.*)") if m_ul else ("ol", r"\d+\. (.*)")
            items = []
            while i < len(lines) and re.match(pat, lines[i]):
                items.append(re.match(pat, lines[i]).group(1)); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        out.append(f"<p>{inline(line)}</p>"); i += 1
    return "\n".join(out)

def support():
    text = (ROOT / "support.md").read_text()
    articles = re.split(r"\n---\n", text)[1:]
    toc, bodies = [], []
    for chunk in articles:
        lines = chunk.strip().splitlines()
        title = re.sub(r"^## (\d+\. )?", "", lines[0])
        meta, last = {}, 0
        for n, l in enumerate(lines[1:8], start=1):
            m = re.match(r"- (分类|链接标识|最后更新)：(.*)", l)
            if m: meta[m.group(1)] = m.group(2); last = n
        slug = meta["链接标识"].strip("`")
        toc.append(f'<a href="#{slug}">{inline(title)}</a>')
        bodies.append(f'<article id="{slug}"><h2>{inline(title)}</h2><p class="meta">最后更新：{meta["最后更新"]}</p>\n{markdown_blocks(lines[last + 1:])}</article>')
    body = ('<div class="card"><h1>稳聘帮助中心</h1><p class="meta">适用于稳聘 iOS 1.0.0</p><nav class="toc">' + "".join(toc) + "</nav></div>\n"
            + "\n".join(bodies)
            + f'<div class="card"><h2>仍需帮助？</h2><p>发邮件到 <a href="mailto:{EMAIL}">{EMAIL}</a>，写明 App 版本（「我的」页底部可以看到）、哪一页和具体问题。请不要在邮件里发送身份证号、银行卡号、密码或验证码。</p></div>')
    page("support.html", "帮助中心", body)

def index():
    body = f"""<div class="card">
<h1>稳聘</h1>
<p class="meta">打工人的求职工具箱 · iPhone · 免费</p>
<p>算清到手工资和加班费，每天记工时，把看过的岗位记下来比一比，入职前做一次防骗自查。</p>
<ul>
<li><strong>算工资</strong>：到手工资、加班费、折合时薪。</li>
<li><strong>记工时</strong>：每天记上班和加班，按月预估工资。</li>
<li><strong>岗位本</strong>：记下自己了解到的岗位，按折合时薪比较，有风险会提醒。</li>
<li><strong>防骗维权</strong>：防骗自查、劳动权益速查、12333 / 96110 / 110 一键拨号。</li>
</ul>
<p>不用注册，不需要定位、相机、通讯录权限，记录只保存在你的手机上。稳聘不发布岗位，不提供招聘或职业中介服务。</p>
</div>
<div class="card toc">
<a href="support.html">帮助中心</a>
<a href="privacy.html">隐私政策</a>
<a href="terms.html">用户协议</a>
</div>"""
    page("index.html", "打工人的求职工具箱", body)

legal("privacy.html", "稳聘隐私政策", "privacy")
legal("terms.html", "稳聘用户协议", "terms")
support()
index()
print("ok")
