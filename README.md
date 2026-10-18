# yun-ds-fetch

把一篇微信公众号文章（`mp.weixin.qq.com` 链接）抓成干净的 Markdown，用来存档、做笔记或交给 AI 总结。

抓取用 DeepSeek 官方的 Fetch 接口，抓回后在本地清洗：去掉多余的反斜杠、界面按钮文字和图表坐标。已迁移、已删除、要验证的空页面，或正文不到 150 字的，不写文件。

## 安装

作为 agent skill（Claude Code、Codex、Cursor 等支持 skills 的工具）：

```bash
npx skills add Followhongyun/yun-ds-fetch
```

只用脚本也可以，需要 Python 3.8 以上，没有第三方依赖：

```bash
git clone https://github.com/Followhongyun/yun-ds-fetch.git
python3 yun-ds-fetch/scripts/wx2md.py --help
```

## 配置

到 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 创建 API Key，账户里要有余额（网页版会员不算）。然后在终端设置：

```bash
export DEEPSEEK_API_KEY="你的 key"
```

要长期生效，写进 `~/.zshrc` 或 `~/.bashrc`。脚本只从环境变量读 key，不打印，也不写文件。

## 用法

装成 skill 后，对 agent 说：

> 把这篇公众号存成 md：https://mp.weixin.qq.com/s/xxxx

直接跑脚本：

```bash
python3 scripts/wx2md.py "https://mp.weixin.qq.com/s/xxxx" -o 文章.md   # 存成文件
python3 scripts/wx2md.py "https://mp.weixin.qq.com/s/xxxx"              # 输出到屏幕
python3 scripts/wx2md.py --clean-only 原始.md -o 干净.md                # 只清洗，不联网
```

一次抓一篇。

| 退出码 | 含义 |
| --- | --- |
| `0` | 成功 |
| `1` | 没设置 `DEEPSEEK_API_KEY` 或接口报错。402 余额不足，429 超速，403/404 换公开链接 |
| `2` | 空页面或正文太短，没写文件 |
| `3` | `--clean-only` 的本地文件读不到 |

## 限制

- 拿不到图片，也没有图片链接。
- Search 接口基本搜不到公众号文章，只适合已有链接的情况。
- 不能绕过登录、付费或验证。

只用于个人阅读、存档和笔记。不批量抓取整个公众号，不转载全文，引用时注明作者和原文链接。文章版权归原作者。

Fetch 按成功请求计费，价格和限速见[官方文档](https://api-docs.deepseek.com/zh-cn/guides/search/)。

## License

[MIT](LICENSE)
