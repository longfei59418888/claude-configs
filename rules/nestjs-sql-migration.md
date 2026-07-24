# SQL 脚本 / 数据库迁移规则

当需要**创建或修改 SQL 脚本（建表、初始化数据、数据库迁移）**时，必须按本规则描述的迁移脚本风格完成。规则已内置认证、商品、促销、优惠券、推荐位等初始化脚本的写法要求，不依赖外部示例目录。

## 文件位置与命名

- 所有迁移脚本统一放在本项目的 `database/migration/` 目录下。
- 文件名格式：`V<时间戳>__<描述>.sql`
  - 时间戳格式：`yyyyMMddHHmm`（当前时间的年月日时分），例如 `V202507151525`
  - 描述用小写下划线，语义为「动作_模块」，例如 `init_auth`、`init_product`
  - 完整示例：`V202507151525__init_auth.sql`

## 数据库访问配置

- 当需要访问数据库时，必须读取项目内 `scripts/config/.env.dev` 中的 MySQL 配置。
- 查询版本表、检查表是否存在、检查字段是否存在、核对数据库现状，都使用该配置连接数据库。
- 不要凭空猜测数据库 host、port、user、password、database；如果 `scripts/config/.env.dev` 不存在或缺少 MySQL 配置，停止操作并要求用户补充配置。

## 修改已有脚本前必查（强约束）

**修改任何已存在的迁移脚本之前，必须先查询数据库版本表，判断该脚本是否已被执行入库。版本表名同样要从项目已有迁移脚本中识别；如果无法确认版本表名，停止操作并要求用户提供。**

```sql
select version from <version_table> where version = '<脚本文件名去掉.sql后缀>';
-- 例：select version from <version_table> where version = 'V202606171000__init_chat';
```

- **若该脚本已在版本表中（已执行）**：**禁止修改该脚本**。必须**新建一个迁移脚本**（按命名规范取新的时间戳），把变更（`alter table`、补字段、初始化数据等）写在新脚本里。
- **若该脚本不在版本表中（未执行）**：可以直接修改该脚本本身。

> 补充判断：版本表只记录迁移工具执行过的脚本，可能与实际库结构不同步。因此除查版本表外，还必须查该脚本涉及的**表/字段是否已真实存在**（`show tables like 'xxx'`、`show columns from xxx`）。只要目标表已存在于数据库，就视为「数据库现状」，一律新建迁移脚本，禁止改原脚本。

> 原因：已入库的脚本代表数据库现状，迁移工具不会重跑它；直接改它会造成「脚本与实际库结构不一致」，且对已部署环境无效。

## 建表规范

- 表名必须使用项目自己的统一前缀，不能写死为某个固定值。
- 创建新表前，必须先检查 `database/migration/` 目录下已有迁移脚本中的表名，识别项目当前使用的表名前缀。
- 常见识别方式：从 `create table <prefix>xxx`、`alter table <prefix>xxx`、`insert into <prefix>xxx` 中统计一致前缀。
- 如果已有脚本中没有可识别的表名前缀，或存在多个前缀且无法判断主前缀，必须停止操作，并要求用户明确输入表名前缀。
- 识别到前缀后，本文中的 `<prefix>` 一律替换为该项目实际前缀，例如 `<prefix>admin`、`<prefix>product`。
- 表名主体使用蛇形命名（snake_case），与 TypeORM `SnakeNamingStrategy` 对齐。
- 主键固定为：`id bigint not null auto_increment` + 末尾 `primary key (id)`。
- 字段命名用蛇形命名（如 `create_time`、`nick_name`、`admin_id`）。
- **每个字段都要写中文 `comment` 注释**说明含义；状态类字段在注释里列出取值，例如
  `status int(1) default 1 comment '帐号启用状态：0->禁用；1->启用'`。
- 时间字段统一用 `datetime`，命名如 `create_time`、`login_time`、`start_time`、`end_time`。
- 关联字段命名为 `<表名单数>_id`，类型 `bigint`，例如 `admin_id`、`role_id`、`recommend_id`。
- 排序字段用 `sort int default 0`。
- SQL 关键字使用小写（`create table`、`bigint`、`primary key` 等）。

## 脚本风格要求

- 每个脚本围绕一个业务域初始化，例如认证、商品、促销、优惠券、推荐位。
- 多张相关表写在同一个初始化脚本中，先写主表，再写关系表、日志表、明细表。
- 表定义使用如下排版：

```sql
create table <prefix>xxx
(
   id                   bigint not null auto_increment,
   name                 varchar(64) comment '名称',
   status               int(1) default 1 comment '启用状态：0->禁用；1->启用',
   create_time          datetime comment '创建时间',
   primary key (id)
);
```

- 复杂业务表前使用块注释说明用途：

```sql
/* 用于存储优惠券信息，需要注意不同使用类型的适用范围。 */
create table <prefix>coupon
(
   ...
);
```

- 字段排列优先按业务含义组织：主键、关联 ID、核心名称/编码、状态、数量/金额、时间、备注、排序。
- 字段对齐保持整齐，类型与 `comment` 尽量纵向对齐，方便审阅。
- 关系表命名使用 `<主表>_<关联表>_relation` 或 `<主表>_<关联表>`，字段使用双方 ID，例如 `coupon_id`、`product_id`。
- 日志表命名使用 `<业务表>_log` 或 `<业务表>_history`，包含业务主体 ID、操作时间、状态、快照字段。
- 初始化数据写在对应表后面，使用大写 `INSERT INTO` 或已有脚本风格中的 `insert into` 均可，但同一个脚本内保持一致。
- 每个脚本末尾写入版本记录：

```sql
insert into <version_table> (version) values ('VyyyyMMddHHmm__description');
```

## 内置案例风格

### 认证初始化案例：`init_auth`

适用于初始化后台账号、角色、菜单、权限关系和登录日志。

应包含的表：

- `<prefix>admin`：管理员账号表，包含 `username`、`password`、`icon`、`email`、`nick_name`、`note`、`create_time`、`login_time`、`status`。
- `<prefix>role`：角色表，包含 `name`、`description`、`admin_count`、`create_time`、`status`、`sort`。
- `<prefix>admin_role`：管理员与角色关系表，包含 `admin_id`、`role_id`。
- `<prefix>menu`：菜单表，包含 `parent_id`、`title`、`level`、`sort`、`name`、`icon`、`hidden`。
- `<prefix>menu_role`：菜单与角色关系表，包含 `role_id`、`menu_id`。
- `<prefix>permission_role`：权限与角色关系表，包含 `role_id`、`resource_id`。
- `<prefix>admin_login_log`：管理员登录日志表，包含 `admin_id`、`create_time`、`ip`、`address`、`user_agent`。

初始化数据风格：

- 初始化超级管理员账号，`id` 固定为 `1`。
- 初始化超级管理员角色，`id` 固定为 `1`。
- 初始化管理员与角色关系。
- 时间字段使用 `NOW()`。

示例片段：

```sql
create table <prefix>admin
(
   id                   bigint not null auto_increment,
   username             varchar(64) comment '用户名',
   password             varchar(64) comment '密码',
   icon                 varchar(500) comment '头像',
   email                varchar(100) comment '邮箱',
   nick_name            varchar(200) comment '昵称',
   note                 varchar(500) comment '备注信息',
   create_time          datetime comment '创建时间',
   login_time           datetime comment '最后登录时间',
   status               int(1) default 1 comment '帐号启用状态：0->禁用；1->启用',
   primary key (id)
);

INSERT INTO <prefix>admin (id,username,password,icon,email,nick_name,note,create_time,login_time,status) VALUES (
  1,
  'admin',
  '<bcrypt-password>',
  'https://example.com/avatar.png',
  'admin@example.com',
  '超级管理员',
  '系统初始化创建的管理员账号',
  NOW(),
  NOW(),
  1
);
```

### 商品初始化案例：`init_product`

适用于初始化商品中心的大量基础表、属性表、关系表、SKU、价格和评论体系。

应包含的表：

- `<prefix>product_category`：商品分类，包含父级、层级、商品数量、单位、导航显示、显示状态、排序、图标、关键词、描述。
- `<prefix>brand`：品牌，包含名称、首字母、排序、制造商状态、显示状态、商品数量、评论数量、logo、专区大图、品牌故事。
- `<prefix>product_attribute_category`：商品属性分类，包含属性数量、参数数量。
- `<prefix>product_attribute`：商品属性，包含属性分类、选择类型、录入方式、可选值、筛选样式、检索类型、关联状态、手动新增状态、属性类型。
- `<prefix>product_attribute_value`：商品属性值，包含商品 ID、属性 ID、自定义值。
- `<prefix>product_category_attribute_relation`：商品分类与属性关系，包含分类 ID、属性 ID。
- `<prefix>product`：商品主表，包含品牌、分类、运费模板、属性分类、名称、图片、货号、删除/上架/新品/推荐/审核状态、价格、库存、积分、详情、促销时间、促销类型等字段。
- `<prefix>sku_stock`：SKU 库存，包含商品 ID、SKU 编码、价格、库存、预警库存、规格属性、图片、销量、促销价、锁定库存。
- `<prefix>product_ladder`：阶梯价格，包含商品 ID、满足数量、折扣、折后价格。
- `<prefix>product_full_reduction`：满减信息，包含商品 ID、满足金额、减少金额。
- `<prefix>member_price`：会员价格，包含商品 ID、会员等级、会员价、会员等级名称。
- `<prefix>comment`：商品评论，包含商品、会员昵称、星级、IP、创建时间、显示状态、购买属性、图片、内容、回复数等。
- `<prefix>comment_replay`：评论回复，包含评论 ID、会员昵称、头像、内容、创建时间、评论人员类型。

风格要点：

- 大业务域可以一个脚本创建多张表。
- 每个复杂表前用 `/* ... */` 注释说明业务用途。
- 状态字段注释必须列出枚举含义，例如 `0->未删除；1->已删除`。
- 金额字段使用 `decimal(10,2)`。
- 商品详情类长文本使用 `text`。

示例片段：

```sql
/* 产品分类 */
create table <prefix>product_category
(
   id                   bigint not null auto_increment,
   parent_id            bigint comment '上级分类的编号：0表示一级分类',
   name                 varchar(64) comment '名称',
   level                int(1) comment '分类级别：0->1级；1->2级',
   product_count        int comment '商品数量',
   product_unit         varchar(64) comment '商品单位',
   nav_status           int(1) comment '是否显示在导航栏：0->不显示；1->显示',
   show_status          int(1) comment '显示状态：0->不显示；1->显示',
   sort                 int comment '排序',
   icon                 varchar(255) comment '图标',
   keywords             varchar(255) comment '关键字',
   description          text comment '描述',
   primary key (id)
);
```

### 促销初始化案例：`init_promotion`

适用于初始化限时购活动、场次、活动商品关系和预约日志。

应包含的表：

- `<prefix>promotion`：限时购活动，包含标题、开始日期、结束日期、上下线状态、创建时间。
- `<prefix>promotion_session`：限时购场次，包含活动 ID、场次名称、每日开始/结束时间、启用状态、创建时间。
- `<prefix>promotion_product_relation`：限时购商品关系，包含场次 ID、商品 ID、限时购价格、限时购数量、每人限购数量、排序。
- `<prefix>promotion_log`：会员预约记录，包含会员 ID、商品 ID、会员电话、商品名称、订阅时间、发送时间。

风格要点：

- 活动日期使用 `date`，每日场次时间使用 `time`，记录时间使用 `datetime`。
- 活动商品关系表使用 `decimal(10,2)` 表达活动价格。
- 日志表记录用户、商品和通知时间。

示例片段：

```sql
/* 用于存储限时购活动的信息，包括开始时间、结束时间以及上下线状态。 */
create table <prefix>promotion
(
   id                   bigint not null auto_increment,
   title                varchar(200) comment '标题',
   start_date           date comment '开始日期',
   end_date             date comment '结束日期',
   status               int(1) comment '上下线状态',
   create_time          datetime comment '创建时间',
   primary key (id)
);
```

### 优惠券初始化案例：`init_coupon`

适用于初始化优惠券、领取使用记录、优惠券与商品/分类关系。

应包含的表：

- `<prefix>coupon`：优惠券主表，包含类型、名称、平台、数量、金额、每人限领、使用门槛、使用时间、使用类型、发行数量、使用数量、领取数量、领取日期、优惠码、会员类型。
- `<prefix>coupon_history`：优惠券领取与使用记录，包含优惠券 ID、会员 ID、订单 ID、券码、领取人昵称、获取类型、创建时间、使用状态、使用时间、订单号。
- `<prefix>coupon_product_relation`：优惠券与商品关系，包含优惠券 ID、商品 ID、商品名称、商品条码。
- `<prefix>coupon_product_category_relation`：优惠券与商品分类关系，包含优惠券 ID、分类 ID、分类名称、父分类名称。

风格要点：

- 使用类型字段必须在注释中说明 `0->全场通用；1->指定分类；2->指定商品`。
- 金额和门槛使用 `decimal(10,2)`。
- 关系表保留名称快照字段，便于历史展示。

示例片段：

```sql
/* 用于存储优惠券信息，需要注意的是优惠券的使用类型：0->全场通用；1->指定分类；2->指定商品，不同使用类型的优惠券使用范围不一样 */
create table <prefix>coupon
(
   id                   bigint not null auto_increment,
   type                 int(1) comment '优惠卷类型；0->全场赠券；1->会员赠券；2->购物赠券；3->注册赠券',
   name                 varchar(100) comment '名称',
   platform             int(1) comment '使用平台：0->全部；1->移动；2->PC',
   count                int comment '数量',
   amount               decimal(10,2) comment '金额',
   per_limit            int comment '每人限领张数',
   min_point            decimal(10,2) comment '使用门槛；0表示无门槛',
   start_time           datetime comment '开始使用时间',
   end_time             datetime comment '结束使用时间',
   use_type             int(1) comment '使用类型：0->全场通用；1->指定分类；2->指定商品',
   primary key (id)
);
```

### 推荐位初始化案例：`init_recommend`

适用于初始化首页推荐位、品牌推荐、商品推荐和轮播广告。

应包含的表：

- `<prefix>recommend`：推荐位主表，包含类型、推荐位名称、描述、code、链接。
- `<prefix>recommend_brand`：品牌推荐，包含品牌 ID、品牌名称、推荐状态、排序、推荐位 ID。
- `<prefix>recommend_product`：商品推荐，包含商品 ID、商品名称、推荐状态、排序、推荐位 ID。
- `<prefix>recommend_adv_banner`：轮播广告，包含名称、图片、开始/结束时间、上下线状态、点击数、下单数、链接地址、备注、排序、推荐位 ID。

风格要点：

- 推荐位主表承载统一入口，具体推荐内容拆到品牌、商品、广告表。
- 推荐状态、上下线状态必须写清 `0` 和 `1` 的含义。
- 广告图片和跳转链接使用较长 `varchar(500)`。

示例片段：

```sql
create table <prefix>recommend
(
   id                   bigint not null auto_increment,
   type                 int(1) comment '类型：0->品牌推荐；1->商品推荐；2->banner广告位',
   name                 varchar(64) comment '推荐位名称',
   description          varchar(64) comment '推荐位描述',
   code                 varchar(32) comment '推荐位code',
   link                 varchar(32) comment '推荐位链接',
   primary key (id)
);
```

## 初始化数据

- 如需初始化数据，紧跟在对应建表语句之后用 `INSERT INTO ... VALUES (...)`。
- 时间值用 `NOW()`。

## 完整初始化表结构同步

本项目维护一份基于所有 `database/migration/` 迁移脚本叠加后的最终表结构快照：

- `database/V202607061139__init_murder_mystery_full.sql`

当任何迁移脚本会导致最终表结构发生变化时（例如 `create table`、`alter table add/modify/drop column`、`drop table`、新增/删除索引等），必须同步更新
`database/V202607061139__init_murder_mystery_full.sql`，使其始终表示“从空库一次性创建当前最终结构”的干净 SQL。

同步规则：

- 迁移脚本仍按前文规则放在 `database/migration/` 下；完整初始化 SQL 不能替代迁移脚本。
- 已执行过的迁移脚本仍然禁止修改；需要变更时新建迁移脚本，同时更新完整初始化 SQL。
- 完整初始化 SQL 只保留最终有效的 `create table`、`create index` 等结果，不写迁移过程中的 `alter table`、`drop table`，也不保留已经删除或废弃的表/字段/索引。
- 如果迁移新增字段或修改字段类型/注释/默认值，完整初始化 SQL 中对应 `create table` 字段定义也要同步成最终状态。
- 如果迁移删除表或字段，完整初始化 SQL 中必须直接移除，不要用注释说明或额外 `drop` 语句表达。

## 注意事项

- 不要凭空发明新的命名风格或结构；遇到不确定的写法，优先按本规则中最接近的内置案例风格编写。
- 修改已有脚本前，先按上文「修改已有脚本前必查」查项目版本表，并确认目标表/字段是否已真实存在：已入库或表已存在则新建脚本，不得改原脚本；两者都没有才可直接改，且修改时保持原有缩进与排版风格。
- 开发中只能创建和修改迁移脚本，切记不要执行迁移脚本
