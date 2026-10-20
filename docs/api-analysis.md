# 区域节点 API 对接文档分析

> **2026-10-20 更正：** 已确认湖北要建设的是区域算力互联互通平台（B，含运行安全监测 E）本身，即这些接口的**服务端**。本文的接口分析仍然适用；“我方作为 A + C/D 调用方”的视角已由 [建设需求方案](platform-requirements.md) 取代，网关设计可作为接入方联调工具或测试桩参考。

> 分析对象：《区域节点API对接接口文档》v1.2（信通院，修订人孟凡磊，文件最后修改 2026-10-13）。
> 文档里的请求/响应示例都放在 Word 文本框中，常规转换会丢失；本分析已逐个提取并核对。

## 1. 参与方与角色

流程图《国家算力互联互通（区域）节点-业务交互流程》共 6 条泳道：

| 代号 | 系统 | 在对接中的位置 |
| --- | --- | --- |
| — | 国家算力互联网服务平台 | 二级审核、下发企业 ID / 标识注册码，B 的上级 |
| **B** | 区域算力互联互通平台（信通院区域节点，本文档提供方） | 一级审核；接收各类同步数据 |
| **C / D** | 算力资源汇聚系统 / 算力选择系统 | 对接云商生命周期接口，向 B 推送接口适配、账单、开通、操作 |
| **A** | 国家算力互联网（区域）服务中心 | 服务商注册认证、标识申请、商品上架；向 B 推送商品 |
| — | 区域算力调度服务平台 | 用户下单入口之一，经 C 开通资源 |
| — | 区域算力资源提供商平台 | 云商（如天翼云），提供生命周期接口、上报算力标识 |

**默认假设：我方建设 A + C/D 侧，即"调用方/推送方"，B 是被调用方。** 推送响应里的 `source` 也印证了这一点：商品推送回 `"source":"A"`，其余回 `"source":"CD"`。

## 2. 业务环节与接口映射

| 环节 | 流程图中的动作 | 对应接口 | 方向 |
| --- | --- | --- | --- |
| 1 算力服务商实名认证 | A 认证 → B 一级审核 → 国家平台二级审核 → 下发企业 ID → B → A 完成认证 | #1 #2 #3 #4 | A→B，B→A 回调 |
| 2 算力标识注册码申请 | 提供商发起 → B 一级 → 国家平台二级 → 下发注册码 → B → A | #5 #6 | A→B，B→A 回调 |
| 3 算力标识上报 | 资源提供商平台 → B 接收/解析/校验/存储 → 国家平台存储 | **文档无接口** | 提供商→B |
| 4 应用接口打通 | 提供商提供接口 → C 对接 → 完成服务接入 → B → 国家平台 | #7 | C→B |
| 5 算力商品上报 | A 商品上架 → B 接收 → 国家平台展示 | #8 | A→B |
| 6 商品检索 / 7 资源规格检索 | A 或调度平台 → C/D 检索 → 返回 | 不涉及 B（我方内部） | — |
| 8 算力交易 | A / 调度平台下单支付生成账单，提供商生成资源账单 → C 汇总 → B → 国家平台 | #9 | C→B |
| 9 任务调度 | 支付 → 发起开通 → C 处理 → 提供商开通 → C 接收结果 → B → 国家平台 | #10 | C→B |
| 10 资源操作 | 用户发起操作 → C 处理 → 反馈 A / 调度平台 | #11 | C→B（流程图未画到 B，接口文档有） |

## 3. 接口清单

| # | 接口 | Method | Path | 鉴权 | 关键标识 |
| --- | --- | --- | --- | --- | --- |
| 1 | 企业实名认证提交 | POST | `/api/v1/enter/auth/` | 2.2.1 | 返回 `sn`（如 `QYRZ20250326000031`） |
| 2 | 企业实名认证重提 | PUT | `/api/v1/enter/auth/{sn}/` | 2.2.1 | `sn` |
| 3 | 查询审批结果 | GET | `/api/v1/enter/auth/{sn}/` | 2.2.1 | `sn`；通过后返回 `provider_code`、`ak`、`sk` |
| 4 | 实名认证审核回调 | POST | 我方 `callback_url` | **未定义** | `sn` + `status` |
| 5 | 算力标识注册码申请 | POST | `/api/v1/code/register/` | 2.2.1 | 返回 `sn`（如 `BMZC…`）与 `code`（如 `20001tc1101501`） |
| 6 | 标识注册码审批回调 | POST | 我方 `callback_url` | **未定义** | `sn` + `status` + `code` |
| 7 | 接口适配同步 | POST | `/api/v1/integration/interface-adaptations/` | 2.2.2 | `capability_id`（C 侧 uuid4） |
| 8 | 商品同步 | POST | `/api/v1/integration/products/` | 2.2.2 | `product_id`（来源方定义） |
| 9 | 账单同步 | POST | `/api/v1/integration/bills/` | 2.2.2 | `bill_id`（C 侧 UUID） |
| 10 | 资源开通同步 | POST | `/api/v1/integration/resource-activations/` | 2.2.2 | `activation_id`（uuid4，同一开通的状态流转共用） |
| 11 | 资源操作同步 | POST | `/api/v1/integration/resource-operations/` | 2.2.2 | `operation_id`（uuid4） |

测试环境：`http://apps.hbhlht.com:8081/stag--open-cnc/`，需在 hosts 中把 `paas.hbhlht.com bkpaas.hbhlht.com apps.hbhlht.com hlht.hbhlht.com hbhlht.com bkuser.hbhlht.com` 指向 `223.76.234.135`。生产地址未提供。

## 4. 通用约定

### 4.1 鉴权

两套凭据，都放在请求头里（不是 OAuth2 换 token 流程，而是静态头）：

| 头部 | 必填 | 说明 |
| --- | --- | --- |
| `X-CLIENT-ID` | 是 | client_id |
| `X-CLIENT-SECRET` | 是 | client_secret |
| `Content-Type` | 否 | `application/json` |

- **2.2.1 客户端凭据**：调度服务商在算力互联互通平台注册获得，用于业务调用（推断用于 #1–#5）。
- **2.2.2 Sync clients 凭据**：推送方系统的凭据需在接收方系统注册，用于系统间同步（推断用于 #7–#11）。
- 文档未写明两者与接口的对应关系，也未说明是否双向（B 回调我方时用什么凭据）。

### 4.2 密码加密

实名认证接口的 `password` 必须加密传输：

- 算法：AES-CBC，PKCS#7 填充；
- 密钥：`client_secret` 的**前 32 位**（即 AES-256）；
- IV：每次随机 16 字节；
- 输出：`base64(IV ‖ 密文)`。

文档给出 Go 和 Python 示例。Python 示例有语法错误（`password := "Aa@123456"`），且依赖 pycryptodome；本仓库用 `cryptography` 重写并附测试（`src/ixp_region_node/crypto.py`）。

### 4.3 响应信封与状态码

```json
{ "data": { ... }, "result": true, "code": 0, "message": "OK" }
```

- `result`：true 成功 / false 失败；失败示例 `code: 1`，`code` 其他取值未列出。
- HTTP 400：参数不正确；HTTP 401：认证失败。
- 我方回调接口也必须按此格式返回（成功 `result:true, code:0`；失败 `result:false, code:1`）。

### 4.4 同步接口的幂等与仲裁（disposition）

#7–#11 的响应：

```json
{ "data": { "source_id": "<原样回显的业务主键>", "disposition": "created", "source": "CD" },
  "result": true, "code": 0, "message": "OK" }
```

| disposition | 含义 | 我方处理 |
| --- | --- | --- |
| `created` | 首次同步成功 | 标记已同步 |
| `duplicate` | 内容完全相同，重推安全 | 标记已同步（重试场景的正常结果） |
| `updated` | 已按最新报文覆盖 | 标记已同步 |
| `stale` | 报文版本比服务端旧，被忽略 | 告警；检查时间字段是否随业务推进 |

结论：B 端按业务主键去重、按时间字段判断新旧，**推送可以安全重试**，适合"至少一次"投递 + 本地 outbox。

## 5. 接口详解

### 5.1 #1 企业实名认证提交 `POST /api/v1/enter/auth/`

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| apply_enterprise | 是 | String | 申请企业 |
| city | 是 | String | 城市编码（附录，4 位） |
| uscc | 是 | String | 统一社会信用代码 |
| mobile | 是 | String | 手机号 |
| provider_code | 否 | Integer | 企业编码，平台统一生成，经回调或查询返回 |
| callback_url | 否 | String | 回调地址；不传需自行轮询 #3 |
| contacts / email | 否 | String | 联系人 / 邮箱 |
| legal_person | 是 | String | 法定代表人 |
| id_type | 否 | String | 机构证件类型，默认 1 |
| id_images | 是 | Array[File] | 营业执照照片，base64 |
| industry | 是 | String | 行业编码（附录，2 位字母） |
| found_date / expire_date | 是 | Datetime | `yyyy-MM-dd HH:mm:ss` |
| unit_prop | 是 | String | 单位性质：军队 / 政府机关 / 事业单位 / 企业 |
| id_num | 是 | String | 机构证件号码，与 uscc 相同 |
| unit_clis | 是 | String | 集团类型：电信业务经营者 / 公益性互联网络单位 / 其他 / 前置单位 |
| contacts_id_type / contacts_id_num | 是 | String | 经办人证件类型 / 号码 |
| access_type | 是 | String | 入网类型，默认 1 |
| business_license | 是 | Array[File] | 营业执照附件 |
| contacts_fid_image / contacts_bid_image | 是 | Array[File] | 经办人身份证正 / 反面 |
| contacts_auth_file | 是 | Array[File] | 经办人授权委托书 |
| e_type | 是 | String | 服务商类型：算力提供商 / 算力调度服务商 |
| username / password | 是 | String | 企业登录账号 / 密码（密码按 4.2 加密） |

文件字段示例写作 `[file] or "base64"`，base64 形如 `data:image/png,iVBOR...`（注意缺少标准 data URI 的 `;base64`）。

响应 `data` 关键字段：`sn`（工单号）、`status`（`un_approval`）、`current_node`（审批节点 ID）、`comment`、`approver`、`provider_code`（创建时为 null）、`ak` / `sk`（创建时为 null）、`auth_info`（username、user_id）、`scheduler`（调度方标识）。

### 5.2 #2 企业实名认证重提 `PUT /api/v1/enter/auth/{sn}/`

字段与 #1 相同，差异：`id_images` 变为非必填；示例把 `uscc` 写成了 `social_credit_code`。用于被驳回后修改重提。

### 5.3 #3 查询审批结果 `GET /api/v1/enter/auth/{sn}/`

返回与 #1 同结构。审批通过时 `status: approved`，并带回 `provider_code`（如 `20227`）、`ak`、`sk`、`approver`、`comment`。**`ak/sk` 是敏感凭据，需加密保存。**

### 5.4 #4 实名认证审核回调（B → 我方）

B 在工单审批通过后调用我方 `callback_url`。

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| sn | 是 | String | 工单编号 |
| task_id | 否 | String | 任务 id |
| status | 是 | String | `un_approval` 待审批 / `approving` 审批中 / `approved` 已审批 / `rejected` 拒绝 / `withdrawn` 撤回 |
| comment | 是 | String | 审批意见 |
| provider_code | 是 | Integer | 企业编码 |
| ak / sk | 否 | String | 访问密钥 |

我方返回 `{"result":true,"code":0,"message":"OK"}`。

### 5.5 #5 算力标识注册码申请 `POST /api/v1/code/register/`

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| provider_code | 是 | Integer | 企业编码（#3/#4 获得，5 位、以 2 开头） |
| city | 是 | String | 城市编码 |
| compute_amount | 是 | String | 资源规模 |
| resource_type | 是 | String | 资源类型：401 超算 / 402 智算 / 403 通用计算 |
| constructor | 否 | String | 建设主体（表格中字段名缺失，据示例补全） |
| callback_url | 否 | String | 回调地址 |
| operator | 否 | String | 运营主体 |
| data_center | 是 | Integer | 可用区编码 501–599 |
| industry | 是 | String | 行业编码 |
| service_type | 是 | Array | 服务类型 6 位编码列表，如 `[601001, 602001]` |
| apply_enterprise | 是 | String | 申请企业 |

响应 `data`：`sn`（如 `BMZC20250312000009`）、`status`、`current_node`、`code`（注册码，如 `20001tc1101501` = 企业编码 20001 + 行业 tc + 城市 1101 + 可用区 501）。

### 5.6 #6 标识注册码审批回调（B → 我方）

字段：`sn`、`task_id`（否）、`status`（同 #4 枚举）、`comments`（审批意见，注意与 #4 的 `comment` 拼写不同）、`code`（注册码，表中写 Integer，但示例是含字母的字符串）。

### 5.7 #7 接口适配同步 `POST /api/v1/integration/interface-adaptations/`

C 完成某云商某服务某生命周期动作的对接后，同步给 B。

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| capability_id | 是 | string | C 侧 uuid4，唯一标识 |
| status | 是 | string | `normal` / `abnormal` |
| action | 是 | string | `create` / `start` / `stop` / `reboot` / `release` |
| provider_name | 是 | string | 算力提供商名称 |
| service_type | 是 | string | `ecs` 弹性云主机 / `ebm` 裸金属 |
| integrated_at | 是 | string | 接入完成时间，示例 `2026-10-11T09:30:00.000000` |

粒度推断：一条记录 = 提供商 × 服务类型 × 动作。

### 5.8 #8 商品同步 `POST /api/v1/integration/products/`

A 的商品新增或更新时**实时**同步。

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| product_id | 是 | String | 来源方商品唯一标识 |
| product_name | 是 | string | 商品名称 |
| status | 是 | string | `on_shelf` / `off_shelf` |
| cpu_cores / memory_gb | 是 | integer | CPU 核数 / 内存 GB |
| gpu_model / gpu_config / interconnect | 否 | string | GPU 型号 / 配置 / 互联协议（NVLink、NVSwitch、PCIe、IB） |
| extra_params | 否 | object | 扁平扩展参数，≤16 个键，总大小 ≤8KB |
| region_id / region_name | 否 | string | 地域 |
| provider_name | 是 | string | 提供商名称 |
| resource_type / service_type | 是 | string | `ecs` / `ebm` |
| bill_mode | 是 | string | 计费方式编码（示例 `subscription`） |
| price | 是 | string | 价格，格式由来源方定（示例 `15000.00 元/月`） |
| model_type | 否 | string | 模型类型 |
| scenarios | 否 | array[string] | 适配场景 |

下架通过 `status: off_shelf` 推送，没有删除接口。**报文没有更新时间字段**，B 如何判 `stale` 不明。

### 5.9 #9 账单同步 `POST /api/v1/integration/bills/`

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| bill_id | 是 | string | C/D 系统账单 UUID |
| amount | 是 | string | 实付金额 |
| bill_cycle | 是 | string | 账期 `yyyyMM` |
| bill_type | 是 | string | 1 新购 / 2 续订 / 3 变更 / 4 退订 / 5 退款降级 / 6 其他 / 7 使用 |
| bill_date | 是 | string | 账单日期 `yyyy-MM-dd` |
| resource_type | 是 | string | `ecs` / `ebm` |
| bill_mode | 是 | string | `on_demand` 按量 / `subscription` 包年包月 |
| dispatch_client_name | 是 | string | 调度服务商名称 |
| price | 是 | string | 官网原价 |
| product_name / provider_name | 是 | string | 产品 / 提供商名称 |
| created_at | 是 | String | 来源账单创建时间 |

账单来源有两路：A / 调度平台产生的消费账单，以及资源提供商产生的资源账单，都由 C 汇总后推送。

### 5.10 #10 资源开通同步 `POST /api/v1/integration/resource-activations/`

同一 `activation_id` 随状态流转多次推送（处理中 → 成功 / 失败），B 以 `updated_at` 判断新旧。

| 字段 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| activation_id | 是 | String | C 侧 uuid4 |
| status_code | 是 | integer | 1 处理中 / 2 成功 / 3 失败 |
| provider_name / dispatch_client_name | 是 | string | 提供商 / 调度服务商名称 |
| resource_type / service_type | 是 | string | `ecs` / `ebm` |
| region_id / region_name / zone_id / zone_name | 否 | string | C 系统对外唯一标识（示例为 UUID） |
| charge_type | 否 | string | `on_demand` / `subscription` |
| duration / order_count | 否 | integer | 订购时长（月）/ 数量 |
| created_at / updated_at | 是 | string | 创建时间 / C 侧最近更新时间 |
| instances | 是 | array[object] | 见下表 |

`instances[]`：`upstream_instance_id`（必填，平台对外实例 ID）、`provider_instance_id`（云商实例 ID，成功后回填，进行中可为空串）、`instance_status_code`（1/2/3）、`error_message`、`completed_at`。示例在顶层也带了 `completed_at`，表格未列。

### 5.11 #11 资源操作同步 `POST /api/v1/integration/resource-operations/`

字段与 #10 基本相同，区别：主键 `operation_id`；`action` 为 `start` / `stop` / `reboot` / `release`；`status` 为字符串 `success` / `failed`（无"处理中"，即只在终态推送）；无 `charge_type`、`duration`、`order_count`。

## 6. 枚举附录摘要

| 枚举 | 编码规则 | 用于 |
| --- | --- | --- |
| 城市 | 4 位，省 2 位 + 市 2 位（北京 1101、武汉 4201） | #1 #2 #5 city |
| 行业 | 2 位字母（tc 电讯业、is 信息传输软件和信息技术服务业…共 41 项） | #1 #2 #5 industry |
| 企业 | 以 2 开头的 5 位数字，国家服务中心分配 | provider_code |
| 资源类型 | 401 超算 / 402 智算 / 403 通用计算；标识中 K1=全量、K2=可用 | #5 resource_type |
| 可用区 | 501–599 | #5 data_center |
| 服务类型 | 6 位：601xxx 计算、602 容器、603 存储、604 数据库、605 网络、606 大数据、607 智算超算、608 算力、609 其他 | #5 service_type |
| 单位性质 | 军队 / 政府机关 / 事业单位 / 企业（中文原值） | unit_prop |
| 集团类型 | 电信业务经营者 / 公益性互联网络单位 / 其他 / 前置单位（中文原值） | unit_clis |

注意两套编码并存：申请环节（#5）用数字编码（`403`、`601001`），同步环节（#7–#11）用字符串编码（`ecs`、`ebm`），需维护映射表。

## 7. 文档问题与不一致

| # | 位置 | 问题 |
| --- | --- | --- |
| 1 | #1/#2 示例 | 仍带 `province`，但 v1.2 已声明删除 |
| 2 | #1/#2 示例 | `city: "110100"` 为 6 位，附录城市编码为 4 位；#3 响应里又是 `"1101"` |
| 3 | #2 示例 | `uscc` 写成 `social_credit_code` |
| 4 | #1/#2 示例 | 出现表中没有的 `cloud_platform`；#1 必填的 `id_images` 示例里没有 |
| 5 | #1/#2 | 文件字段是 multipart 还是 JSON base64 不明；base64 前缀 `data:image/png,` 缺 `;base64`；单文件大小上限未给 |
| 6 | #1/#2 | `password` 说明抄成了"登录的账号"；`username/password` 是哪个平台的账号未说明（文档批注也提了） |
| 7 | #1/#2 | `e_type` 取值一处写"算力调度服务商"，一处写"算力调度商" |
| 8 | #1/#2 | `id_type`、`contacts_id_type`、`access_type` 只给了默认值 1，无完整枚举 |
| 9 | #5 | 表格有一行字段名为空（据示例为 `constructor`）；`callback_url` 说明被截断 |
| 10 | #4 #6 | 标为 `params`，但 Method 是 POST，参数在 query 还是 JSON body 不明 |
| 11 | #4 vs #6 | 审批意见字段一个叫 `comment`，一个叫 `comments` |
| 12 | #6 | `code` 标为 Integer，实际注册码含字母（`20001tc1101501`） |
| 13 | #4 #6 | 描述为"审批通过之后"回调，但状态含 rejected / withdrawn，驳回是否回调不明 |
| 14 | #4 #6 | 回调没有任何鉴权或签名约定 |
| 15 | #5 | 注册码没有查询接口（批注："有没有主动查询审批结果接口？"），也没有重提接口 |
| 16 | 时间格式 | 申请类用 `yyyy-MM-dd HH:mm:ss`，同步类用 ISO 8601 带微秒，均无时区 |
| 17 | #8 | 无更新时间字段，`stale` 判定依据不明 |
| 18 | #10 #11 | 示例顶层有 `completed_at`，表格没有；region_id 示例为 UUID，#8 示例为 `420100` |
| 19 | 环节 4、9 | 正文提到"配置变更"，但 `action` 枚举和接口都没有配置变更 |
| 20 | 环节 3 | 流程图有"算力标识上报"，文档没有对应接口 |
| 21 | 2.2 | 两套凭据分别用于哪些接口未写明 |
| 22 | 2.3 | `code` 失败码只给了 1，没有错误码表 |
| 23 | 测试环境 | 仅 HTTP，凭据和 ak/sk 明文传输 |
