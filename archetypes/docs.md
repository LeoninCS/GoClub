---
title: "{{ .Name | humanize | title }}"
weight: 1
# 文件名含中文时必须填 slug，用纯小写英文（字母、数字、连字符），
# 否则 URL 会被编码成一长串 %XX，分享出去很长。
#   面经：投稿人-公司-岗位-轮次，例如 blocke-bytedance-1
#   其他：简短英文描述，例如 go-backend-roadmap
# slug: ""
#
# 写完记得运行 python3 scripts/gen_shortlinks.py 补上 /s/ 分享短链，
# 它会自动写入 aliases 和 shortlink 字段，不用手写。
#
# bookFlatSection: false
# bookToc: true
# bookHidden: false
# bookCollapseSection: false
# bookComments: false
# bookSearchExclude: false
# bookHref: ''
# bookIcon: ''
---
