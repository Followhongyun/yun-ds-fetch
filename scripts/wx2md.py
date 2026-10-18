#!/usr/bin/env python3
"""公众号文章 -> 干净 Markdown。调用 DeepSeek 官方 Fetch 接口，再做本地清洗。
用法: python3 wx2md.py <公众号链接> [-o 文章.md]
      python3 wx2md.py --clean-only 原始.md [--url 原文链接]   # 只清洗已有文本，不联网
密钥: 环境变量 DEEPSEEK_API_KEY（不打印、不写文件）
退出码: 0 成功；1 未设置密钥或接口报错；2 空页面/占位页，不写文件；3 本地文件读不到
"""
import argparse, json, os, re, sys, urllib.request, urllib.error

API = "https://api.deepseek.com/v1/tools/fetch"
PLACEHOLDERS = ["该公众号已迁移", "该内容已被发布者删除", "此内容因违规无法查看", "内容已删除",
                "此内容被投诉且经审核涉嫌侵权", "环境异常", "完成验证后即可继续访问", "参数错误",
                "该公众号已被封禁", "此帐号已被屏蔽", "链接已过期"]
UI_NOISE = {"视频", "小程序", "赞", "在看", "分享", "留言", "收藏", "听过", "：", "，", "。",
            "，轻点两下取消赞", "，轻点两下取消在看", "微信扫一扫", "关注该公众号", "继续滑动看下一个",
            "轻触阅读原文", "向上滑动看下一个", "知道了", "取消", "允许", "预览时标签不可点", "刷新",
            "视频详情", "播放", "暂停", "全屏", "退出全屏", "视频加载失败，请刷新页面再试"}
ESC = re.compile(r"\\([\\`*_{}\[\]()#+\-.!:/|>~=<&%?@$'\"^,;])")
PUNCT = re.compile(r"[。！？；，、.!?;,]")


def fetch(url):
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("没有设置环境变量 DEEPSEEK_API_KEY")
    req = urllib.request.Request(API, data=json.dumps({"url": url}).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        hint = {402: "余额不足", 403: "被安全策略拒绝", 404: "抓不到可用正文", 429: "超过限速，稍后再试"}
        raise RuntimeError(f"HTTP {e.code} {hint.get(e.code, '')}".strip())


def is_short(s):
    s = s.strip()
    return bool(s) and len(s) <= 24 and not PUNCT.search(s)


def drop_charts(lines):
    """连续 4 行以上、短、无标点、一半以上带数字：多半是图片里图表的坐标文字。"""
    out, i = [], 0
    while i < len(lines):
        if is_short(lines[i]) and not lines[i].lstrip().startswith(("#", "-", "*", ">", "|", "!")):
            j, run = i, []
            while j < len(lines) and (is_short(lines[j]) or not lines[j].strip()):
                if lines[j].strip():
                    run.append(lines[j])
                j += 1
            if len(run) >= 4 and sum(bool(re.search(r"\d", x)) for x in run) * 2 >= len(run):
                out.append("[图表]")
                i = j
                continue
        out.append(lines[i])
        i += 1
    return out


def clean(text, title=""):
    lines = [l.rstrip() for l in ESC.sub(r"\1", text).replace("\r\n", "\n").split("\n")]
    lines = [l for l in lines if l.strip() not in UI_NOISE]
    lines = [re.sub(r"([。！？”])\s*\d{1,4}$", r"\1", l) for l in lines]
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(drop_charts(lines))).strip()
    if title:  # 正文里重复的标题
        body = re.sub(r"^(作者：[^\n]*\n+)?#\s*" + re.escape(title) + r"\s*\n+", r"\1", body)
    return body


def problem(title, body):
    hit = next((p for p in PLACEHOLDERS if p in title or p in body[:300]), None)
    if hit:
        return f"占位页（{hit}），没有正文"
    n = len(re.sub(r"[\s#*>\-\[\]()图表]", "", body))
    return f"正文只有 {n} 字，可能没抓到" if n < 150 else None


def main():
    ap = argparse.ArgumentParser(description="公众号文章 -> 干净 Markdown（DeepSeek Fetch + 本地清洗）")
    ap.add_argument("src", help="公众号文章链接；用 --clean-only 时是本地原始文本文件")
    ap.add_argument("-o", "--out", help="输出文件；不写则输出到屏幕")
    ap.add_argument("--clean-only", action="store_true", help="只清洗本地文件，不联网、不收费")
    ap.add_argument("--url", help="配合 --clean-only，写进来源行的原文链接")
    a = ap.parse_args()
    if a.clean_only:
        try:
            with open(a.src, encoding="utf-8") as f:
                raw = f.read()
        except OSError as e:
            print(json.dumps({"ok": False, "error": f"读不到文件：{e.strerror}"}, ensure_ascii=False))
            return 3
        m = re.match(r"#\s*(.+)\n", raw)
        title, content, url = (m.group(1).strip() if m else ""), (raw[m.end():] if m else raw), a.url
    else:
        try:
            res = fetch(a.src)
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
            return 1
        title, content, url = (res.get("title") or "").strip(), res.get("content") or "", a.src
    body = clean(content, title)
    bad = problem(title, body)
    if bad:
        print(json.dumps({"ok": False, "title": title, "problem": bad}, ensure_ascii=False))
        return 2
    md = f"# {title}\n\n" + (f"来源：{url}\n\n" if url else "") + f"{body}\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        sys.stdout.write(md)
    print(json.dumps({"ok": True, "title": title, "chars": len(body), "saved_to": a.out}, ensure_ascii=False), file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
