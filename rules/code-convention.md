# 代码执行规范（业务模块开发）

开发任何业务功能时，模块组织与编码风格统一参照
`/Users/wangxiaolong/Desktop/github/nestjs-mall/src/modules/admin` 的风格，
并遵循下列约定（源自该项目 `database/id.md` 的接口开发规范，结合本项目调整）。

## 一、模块目录组织

- 所有业务模块放在 `src/modules/` 下。
- 采用「**主模块 / 子模块**」两级划分：`src/modules/<主模块>/<子模块>/`。
  - 主模块 = 一个业务大域（如 `user`）。
  - 子模块 = 该域下的具体功能（如 `auth`、`membership`、`coin`）。
- 本项目已规划的模块：
  - `src/modules/user/auth/`        —— 登录认证（Google/X/Discord/邮箱验证码）
  - `src/modules/user/membership/`  —— 会员订阅付费
  - `src/modules/user/coin/`        —— 金币充值与消费
- 新增其他功能时，按「归属哪个业务域」放到对应主模块下作为子模块；若是全新业务域，则新建主模块再加子模块。

## 二、每层文件职责与命名

参照 admin 模块，每个子模块包含：

- `<子模块>.controller.ts` —— 控制器，定义接口
- `<子模块>.service.ts`    —— 业务逻辑
- `dto/` —— 入参与出参 DTO（每个文件一个 DTO）
- 主模块下统一放：
  - `<主模块>.module.ts` —— 主模块，聚合所有子模块的 controller/service，并用 `TypeOrmModule.forFeature([...])` 注册本模块实体
  - `entities/` —— 本模块的 TypeORM 实体（`Xxx.entity.ts`）
- 主模块要被注册进 `src/modules/index.module.ts`（参照 admin 注册进 IndexModule 的方式）。

## 三、Controller 规范（重点）

1. **只用 `@Get`、`@Post`**：不使用 `@Put`、`@Delete` ，方法路径用语义化后缀：
   `create` / `list` / `detail` / `update` / `delete`。
2. **路径常量集中管理**：`@Controller()` 的路径用 `infrastructure/contants/paths.ts` 里的常量，不要硬编码字符串。
3. **Swagger 描述齐全**：
   - 类上加 `@ApiTags('中文模块名')`
   - 每个接口加 `@ApiOperation({ summary: '中文说明' })`
   - 返回值用 `@ApiOkDataResponse(XxxResponseDto)`（单对象）或 `@ApiOkPagesResponse(XxxResponseDto)`（分页），
     来自 `infrastructure/decorator/data.decorator.ts`；**因此每个接口都要提供对应的 response DTO 文件或明确的实体类**。
   - **禁止使用 `@ApiOkDataResponse(Object)` / `@ApiOkPagesResponse(Object)`**。Swagger 返回模型必须是具体类型，
     例如 `ScriptDetailResponseDto`、`ScriptListItemResponseDto` 或 `MmProject`，用于清晰表达接口文档字段结构。
4. **权限控制（按接口性质区分）**：
   - **后台 / 管理类接口**：用 `createPermission(PATH, '分组名')` 生成权限装饰器，给每个接口加
     `@XxxPermission(PERMISSIONS.CREATE, '中文说明')`，参照 admin/manage 各 controller；由 `PrivilegeGuard` 校验。
   - **C 端用户接口**（user 域大多属此类）：默认走登录态校验（`AuthGuard` + CLS 中的 user）；
     无需登录的接口（如登录、发验证码、OAuth 回调）加 `@Public()`。
     取当前用户用 `@User()` / `@UserId()` 装饰器。

## 四、装饰器使用规范

- **优先使用项目内置装饰器**：需要 Swagger 响应、权限、登录豁免、当前用户、缓存、锁、后置回调等能力时，优先使用
  `src/infrastructure/decorator/` 下已有装饰器，不要在业务代码里重复手写 `SetMetadata`、Swagger 包装、CLS 取用户、
  Redis 缓存 key、分布式锁等通用逻辑。
  - `data.decorator.ts`
    - `@ApiOkDataResponse(XxxResponseDto)`：单对象响应文档，返回结构为统一 `{ code, message, data }`。
    - `@ApiOkPagesResponse(XxxResponseDto)`：分页响应文档，`data.records` 使用指定 DTO 类型。
    - `@ApiOkDatasResponse(XxxResponseDto)`：数组响应文档。
    - Swagger 返回类型必须传具体 DTO / Entity / 基础类型，禁止传 `Object`。
  - `public.decorator.ts`
    - `@Public()`：接口不需要登录校验时使用，例如登录、验证码、公开健康检查、公开生成接口。
  - `user.decorator.ts`
    - `@User()`：从 CLS 获取当前登录用户对象。
    - `@User('id')` / `@UserId()`：获取当前用户 ID。Controller 中不要直接访问 CLS。
  - `permission.decorator.ts`
    - `createPermission(PATH, '分组名')`：后台/管理接口生成权限装饰器。
    - `PERMISSIONS`：接口权限动作枚举，优先使用 `READ` / `CREATE` / `UPDATE` / `DELETE` / `OPTION`，不要写散落字符串。
  - `cache.decorator.ts`
    - `@Cache(CachePrefixEnum.X, CacheTimeEnum.X)`：查询类方法缓存。
    - `@AfterWithCacheDel(CachePrefixEnum.X)`：写操作成功后删除对应缓存。
    - 新增缓存场景时先扩展 `CachePrefixEnum` / `CacheTimeEnum`，不要在业务方法里硬编码 Redis key。
  - `lock.decorator.ts`
    - `@Lock(key, ttl)`：并发敏感方法使用分布式锁，例如余额、会员、生成任务互斥等。
    - 锁 key 要可区分业务范围；如果 key 需要动态拼接且现有装饰器不能满足，再使用 `CacheService.lockCall`。
  - `after.decorator.ts`
    - `@After('methodName')`：方法执行成功后触发同类中的后置方法，适合轻量级后处理。
    - 后置逻辑复杂、跨模块或需要异步可靠投递时，不要滥用 `@After`，应使用 service 显式调用或事件机制。

## 五、Service 规范

- 用 `@InjectRepository(Entity)` 注入仓库。
- **分页参数用 `current`（当前页），不要用 `page`**；分页类型可复用 `infrastructure/types/PageParams` / `PageResponse`。
- 需要数据库事务时，优先使用 `typeorm-transactional` 的 `@Transactional()` 装饰器：
  `import { Transactional } from 'typeorm-transactional';`。业务方法内不要优先手写 `dataSource.transaction(...)`。
- 只有在必须动态控制事务边界、跨非标准连接、或装饰器无法覆盖的特殊场景，才使用 `DataSource` / `EntityManager` 手动事务，并在代码中说明原因。
- 涉及金币/会员余额等并发敏感操作，加分布式锁（`@Lock` 或 `CacheService.lockCall`）+ `@Transactional()`，见项目记忆中的金币/会员设计决策。

## 六、实体（Entity）规范

- 实体定义在**各自模块的 `entities/` 目录**下，命名 `Xxx.entity.ts`。
- **不要使用 `database/entities` 目录下的实体结构**（那里是空骨架/生成产物，不作为业务依赖）。
- 表名用 `@Entity('hb_xxx')`，与 `sql-migration` 规则的 `hb_` 前缀一致。
- 主键 `@PrimaryGeneratedColumn({ type: 'bigint', name: 'id' })`，类型声明为 `string`（bigint 映射为字符串）。
- 字段用 `@Column`，显式写 `name`（蛇形）、`comment`（中文）、`nullable`、`length` 等，与建表 SQL 对齐。

## 七、统一响应

- 接口直接返回数据对象/分页结果即可，全局 `LoggerInterceptor` 会用 `ResponseReturn.success()` 统一包装为 `{code,message,data}`；业务报错用 `ResponseReturn.error(msg)` 或抛 `HttpException`。

## 八、对照清单（动手前自检）

1. 模块是否放在正确的 `主模块/子模块` 路径下？
2. 是否全用  `@Get`、`@Post` + 语义化后缀？
3. 路径是否走 `paths.ts` 常量？
4. 每个接口是否有 `@ApiOperation` + `ApiOkDataResponse/ApiOkPagesResponse` + 具体 response DTO 或实体类，且没有使用 `Object`？
5. 权限/登录态是否按接口性质正确加上？
6. Swagger、权限、登录豁免、当前用户、缓存、锁等是否优先使用 `src/infrastructure/decorator/` 里的装饰器？
7. 需要事务的方法是否优先使用 `typeorm-transactional` 的 `@Transactional()`？
8. 分页是否用 `current`？
9. 实体是否在模块 `entities/` 下、`hb_` 表名、未依赖 `database/entities`？
10. 主模块是否注册进 `index.module.ts`、实体是否 `forFeature` 注册？

风格细节拿不准时，打开 `nestjs-mall/src/modules/admin` 下最接近的模块对照后再写。
