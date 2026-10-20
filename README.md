# ixp-region-node-integration

湖北区域算力互联互通平台（国家算力互联互通区域节点中的算力标识管理系统 B 与运行安全监测系统 E）建设仓库。平台按信通院《区域节点API对接接口文档》对服务中心（A）、资源汇聚 / 算力选择系统（C/D）提供认证审核、标识注册和业务数据接收接口，并对接国家节点。

## 文档

- [建设需求方案](docs/platform-requirements.md)：建设背景、平台边界、业务 / 功能 / 接口 / 非功能需求、分期计划
- [API 分析](docs/api-analysis.md)：接口清单、鉴权、报文、枚举、文档问题
- [接入方实施方案](docs/implementation-plan.md)：早先按接入方视角写的方案，可作联调参考
- [待确认问题](docs/open-questions.md)：需向信通院确认的事项
- [原始对接文档 v1.2](docs/source/) 与业务流程图

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
