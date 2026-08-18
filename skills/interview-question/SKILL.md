---
name: interview-question
description: Format raw Go backend interview materials into standardized GoClub Markdown.
---

# GoClub Interview Formatting Skill

Your task is to convert a complete interview record, transcript, notes, chat log, or draft answers into a GoClub interview page. Process one interview session at a time. Do not split one session into separate question files.

Return only the standardized Markdown below. Do not add explanations, greetings, surrounding quotes, or an extra outer code fence.

## Required output shape

```markdown
---
title: "contributor-company-role-round"
---

# Company and role title

1. First interview question
2. Second interview question

## 参考答案（AI 生成）

> 以下答案由 AI 生成，仅供面试复盘参考。

### 1. First interview question

答：Start with a clear conclusion, then explain the key mechanism, boundary conditions, and likely follow-up questions.

### 2. Second interview question

答：Start with a clear conclusion, then explain the key mechanism, boundary conditions, and likely follow-up questions.
```

## Metadata rules

- `title`: 5–80 characters. Use the pattern `contributor-company-role-round`, for example `krypton-深信服Golang一面`.

## Content rules

- Write page content in Simplified Chinese unless the user explicitly requests another language.
- Start the body with one concise H1 describing the company and role. Do not repeat the contributor nickname there.
- Preserve every meaningful interview question. Remove greetings, duplicates, and conversation unrelated to the interview.
- Keep numbered questions in Arabic numeral order. Clarify unclear spoken wording, but do not change the intended meaning.
- Keep the `## 参考答案（AI 生成）` heading and the exact AI-generated notice shown above.
- Give one numbered H3 answer heading for each question. Start each answer with `答：`, state the conclusion first, and then add principles, scenarios, trade-offs, or commands as appropriate.
- For project questions, organize an answer around the user's actual experience. Do not fabricate personal experience.
- Put code in triple-backtick code blocks. When submitting through GitHub, wrap the entire Markdown output in a four-backtick code block.
- Do not output Hugo shortcodes such as `{{< ... >}}` or `{{% ... %}}`.
- Do not output `<script>`, `<iframe>`, event-handler attributes, or `javascript:` links.
- Do not invent source-code versions, performance numbers, interview results, or company information. Use “待确认” when reliable information is unavailable.
- If the user provides questions without answers, generate conservative answers in the required structure. If a reliable answer is impossible, write “待确认” rather than inventing details.

## Editing procedure

1. Determine whether all material belongs to one interview session. If it contains multiple sessions, tell the user to process each session separately.
2. Clean and organize the question list without changing the meaning.
3. Write cautious, verifiable reference answers; remind users to revise project answers based on their real experience.
4. Return the complete standardized Markdown only.
