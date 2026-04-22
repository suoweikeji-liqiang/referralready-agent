# ReferralReady Agent 中文说明

ReferralReady 是一个面向 Agents Assemble 比赛的初始化项目：它不做“AI 医生”，而是做一个 **转诊资料包 Agent**。

它会从合成 FHIR-like 患者数据中抽取病史、化验、用药、检查、就诊记录，生成给专科医生看的转诊资料包，同时指出转诊前还缺哪些信息，并生成护理协调任务。

## 核心边界

- 只使用合成数据
- 不使用真实 PHI
- 不做诊断
- 不给治疗建议
- 所有输出都要求 clinician review

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_local_demo.py --patient SYN-CKD-001 --specialty nephrology
```

## 下一步

1. 接入 Prompt Opinion Marketplace
2. 确认 MCP server 能被平台调用
3. 录制 3 分钟以内 Demo 视频
4. 提交 Devpost
