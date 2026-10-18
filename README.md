# yun-ds-fetch

把一篇微信公众号文章（`mp.weixin.qq.com` 链接）抓成干净的 Markdown，方便存档、做笔记，或者交给 AI 总结。

底层用的是 DeepSeek 官方的 Fetch 接口，抓回来以后脚本在本地再洗一遍：去掉多余的反斜杠、界面按钮文字和图表坐标，空页面直接拦下来不存。

## 它做什么

- 输入一个公众号链接，输出一篇带标题和来源链接的 Markdown。
- 本地清洗：
  - 去掉 Markdown 转义多出来的反斜杠，比如 `5000\+`、`https\:\/\/`
  - 去掉点赞、在看、分享、播放器按钮这类界面文字
  - 连续 4 行以上、很短、没有标点、一半以上带数字的行，多半是图片里图表的坐标文字，整段换成 `[图表]`
  - 去掉正文里重复出现的标题，顶部加上来源链接
- 已迁移、已删除、违规、需要验证的空页面，或者正文不到 150 字的，不写文件，直接告诉你抓不到。

## 安装

作为 agent skill 安装（Claude Code、Codex、Cursor 等支持 skills 的 agent）：

```bash
npx skills add Followhongyun/yun-ds-fetch
```

也可以只用脚本：只需要 Python 3，没有第三方依赖。

```bash
git clone https://github.com/Followhongyun/yun-ds-fetch.git
python3 yun-ds-fetch/scripts/wx2md.py --help
```

## 配置 DEEPSEEK_API_KEY

1. 到 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 创建 API Key。它和 DeepSeek 网页版会员是两回事，账户里需要有余额。
2. 在你自己的终端里设置环境变量：

```bash
export DEEPSEEK_API_KEY="你的 key"
```

想长期生效就写进 `~/.zshrc` 或 `~/.bashrc`。脚本只从环境变量读 key，不会打印，也不会写进任何文件。不要把 key 贴进聊天，也不要写进命令行参数。

## 用法

装成 skill 以后，直接跟 agent 说：

> 把这篇公众号存成 md：https://mp.weixin.qq.com/s/xxxx

手动跑脚本：

```bash
# 抓一篇，存成文件
python3 scripts/wx2md.py "https://mp.weixin.qq.com/s/xxxx" -o 文章.md

# 不加 -o 就输出到屏幕
python3 scripts/wx2md.py "https://mp.weixin.qq.com/s/xxxx"

# 手里已经有原始文本，只做清洗：不联网，不花钱
python3 scripts/wx2md.py --clean-only 原始.md -o 干净.md
```

一次只抓一篇，多篇请一篇一篇来。

## 退出码

| 退出码 | 含义 | 怎么办 |
| --- | --- | --- |
| `0` | 成功，Markdown 已写入（或已输出到屏幕），标准错误里有标题和字数 | 无 |
| `1` | 出错：没设置 `DEEPSEEK_API_KEY`，或接口报错 | 402 是余额不足，去充值；429 是超速，等几秒再试；403、404 换一个公开链接，别反复重试 |
| `2` | 抓到的是空页面（已迁移、已删除、违规、要验证），或正文不到 150 字 | 不写文件，这篇抓不到正文，不用重试 |

## 做不到的事

- **图片拿不到。** 返回的正文里没有图片，连图片链接都没有。要看图请打开原文。
- **搜不到公众号文章。** DeepSeek 的 Search 接口限定 `mp.weixin.qq.com` 基本是空结果，所以这个工具只适合你手里已经有链接的情况。
- **不能绕过登录、付费或验证。** 需要验证的页面会被当成空页面拦下来。

## 使用边界

只用于个人阅读、存档、做笔记和总结。

- 不批量抓取整个公众号
- 不把抓到的全文转发、转载或公开发布
- 引用时注明作者和原文链接

文章版权归原作者所有。

## 价格

DeepSeek 官方目前的说法是 Fetch 按成功请求计费，失败不收费。具体价格和限速**以官方文档为准**：<https://api-docs.deepseek.com/zh-cn/guides/search/>

## License

[MIT](LICENSE)
