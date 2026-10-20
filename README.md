# ixp-region-node-integration

信通院区域节点（区域算力互联互通平台 B）对接网关。我方作为区域服务中心（A）与资源汇聚 / 算力选择系统（C/D），向 B 提交实名认证、标识注册码申请，接收审批回调，并推送接口适配、商品、账单、资源开通、资源操作五类数据。

## 文档

- [API 分析](docs/api-analysis.md)：接口清单、鉴权、报文、枚举、文档问题
- [实施方案](docs/implementation-plan.md)：架构、选型、模块、分阶段计划、风险
- [待确认问题](docs/open-questions.md)：需向信通院确认的事项
- [原始对接文档 v1.2](docs/source/) 与业务流程图
- [工信部节点建设方案附件](docs/source/)：国家算力互联互通节点建设工作通知附件（公开文件）

本仓库只放对接网关的工程内容。ixp 并行平台的整体建设方案涉及申报材料，不放在仓库中。

## 目录

```
src/ixp_region_node/
  crypto.py          密码 AES 加密（已实现）
  core/              B 客户端、凭据、响应解析
  enums/             城市 / 行业 / 服务类型等码表与映射
  enterprise_auth/   实名认证 #1–#3
  ident_code/        标识注册码 #5
  callbacks/         审批回调 #4 #6
  sync/              数据同步 #7–#11（outbox + worker）
  reconcile/         轮询兜底与对账
tests/
```

## 开发

```bash
pip install -e .
cp .env.example .env   # 填入测试凭据
PYTHONPATH=src python -m unittest discover -s tests
```
