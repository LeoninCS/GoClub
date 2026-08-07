---
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
date: '{{ .Date }}'
draft: true
# 文件名含中文时必须填 slug，用纯小写英文，否则分享链接会变成一长串编码字符。
# 面经格式：投稿人-公司-岗位-轮次，例如 blocke-bytedance-1
# 其他页面：简短英文描述，例如 go-backend-roadmap
# slug: ""
---
