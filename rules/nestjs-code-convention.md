# 代码执行规范（业务模块开发）

开发任何业务功能时，模块组织、接口定义、文件命名与编码风格统一采用本规则。规则来自现有后台业务模块的实践提炼，不在业务代码或文档中直接引用本地绝对路径。

## 一、模块目录组织

业务模块采用「入口模块 / 业务域模块 / 功能子模块」结构。

```text
src/modules/
└── <入口模块>/
    ├── <入口模块>.module.ts
    ├── <业务域模块>/
    │   ├── <业务域模块>.module.ts
    │   ├── entities/
    │   │   └── Xxx.entity.ts
    │   └── <功能子模块>/
    │       ├── <功能子模块>.controller.ts
    │       ├── <功能子模块>.service.ts
    │       └── dto/
    │           ├── CreateXxx.dto.ts
    │           ├── UpdateXxx.dto.ts
    │           ├── ListXxx.dto.ts
    │           └── XxxResponse.dto.ts
    └── <独立功能模块>/
        ├── <独立功能模块>.module.ts
        ├── <独立功能模块>.controller.ts
        ├── <独立功能模块>.service.ts
        └── dto/
            └── Xxx.dto.ts
```

目录划分规则：

- `<入口模块>.module.ts` 只负责聚合下级模块，不直接承载业务 controller/service。
- `<业务域模块>` 表示一个业务大域，例如商品、权限、营销等。
- `<功能子模块>` 表示业务域下的具体功能，例如品牌、分类、属性、角色、菜单等。
- 同一业务域的实体统一放在该业务域的 `entities/` 目录，不分散到各功能子模块中。
- 简单且独立的功能可以直接拥有自己的 module/controller/service/dto；如果后续扩展成多个功能，应拆成业务域模块加功能子模块。

## 二、文件命名规范

### Module 文件

- 入口模块：`<入口模块>.module.ts`
- 业务域模块：`<业务域模块>.module.ts`
- 模块类名使用 PascalCase，并以 `Module` 结尾，例如 `AdminProductModule`、`ManageModule`、`AuthModule`。
- 模块文件名通常使用小写或 camelCase，与目录名保持一致。

### Controller 文件

- 文件名：`<功能名>.controller.ts`
- 类名：`<功能名PascalCase>Controller`
- 示例：
  - `brand.controller.ts` -> `BrandController`
  - `menu.controller.ts` -> `MenuController`
  - `attributeCategory.controller.ts` -> `ProductAttributeCategoryController`

### Service 文件

- 文件名：`<功能名>.service.ts`
- 类名：`<功能名PascalCase>Service`
- 示例：
  - `brand.service.ts` -> `BrandService`
  - `menu.service.ts` -> `MenuService`

### DTO 文件

DTO 文件每个文件只放一个 DTO 类。常见命名：

- `CreateXxx.dto.ts`：创建接口入参。
- `UpdateXxx.dto.ts`：更新接口入参。
- `ListXxx.dto.ts`：列表查询入参。
- `GetXxx.dto.ts`：详情或条件查询入参。
- `DeleteXxx.dto.ts`：删除接口入参。
- `XxxResponse.dto.ts`：接口响应结构。
- 组合型返回 DTO 可按业务语义命名，例如 `RoleMenusResponse.dto.ts`、`MallAdminInfoResponse.dto.ts`。

DTO 类名与文件名保持一致并使用 PascalCase，例如 `CreateBrandDto`、`ListProductDto`、`BrandResponseDto`。

### Entity 文件

- 文件名：`Xxx.entity.ts`
- 类名：`Xxx`
- 实体类名使用业务表的 PascalCase 形式，例如 `MallBrand`、`MallProductCategory`、`MallAdminLoginLog`。
- 实体放在所属业务域模块的 `entities/` 目录。

## 三、每类文件职责

### `<入口模块>.module.ts`

负责聚合下级模块。

- `imports` 中引入业务域模块或独立功能模块。
- `controllers` 通常为空。
- `providers` 通常为空。
- `exports` 按实际跨模块需要配置，默认可以为空。

### `<业务域模块>.module.ts`

负责注册该业务域内的实体、controller、service 和基础设施依赖。

- 使用 `TypeOrmModule.forFeature([...])` 注册本业务域需要的实体。
- `controllers` 中注册该业务域下所有功能子模块 controller。
- `providers` 中注册对应 service。
- 需要 Redis、缓存等基础设施时，在 `imports` 或 `providers` 中按已有项目方式引入。
- 不在 module 中编写业务逻辑。

### `<功能名>.controller.ts`

负责接口层。

- 定义路由、请求参数、Swagger 文档、权限装饰器。
- 调用 service 完成业务处理。
- 不直接写复杂业务逻辑、数据库查询或事务逻辑。
- 返回值使用统一响应包装，例如 `ResponseReturn.success(...)`。

### `<功能名>.service.ts`

负责业务逻辑。

- 使用 `@InjectRepository(Entity)` 注入 TypeORM Repository。
- 负责创建、更新、删除、查询、分页、权限组合等业务操作。
- 查询列表时优先使用 QueryBuilder，返回统一分页结构。
- 可使用 `plainToInstance(Entity, dto)` 将 DTO 转换为实体更新对象。
- 不处理 Swagger、路由装饰器和接口权限声明。

### `dto/*.dto.ts`

负责接口入参与出参结构。

- 入参 DTO 使用 `class-validator` 做参数校验。
- 查询参数中数字字段使用 `class-transformer` 的 `@Type(() => Number)` 转换类型。
- 字段使用 `@ApiProperty` 描述中文含义、示例、是否必填、长度、nullable 等。
- 响应 DTO 明确列出返回字段，不使用 `Object` 代替具体结构。

### `entities/*.entity.ts`

负责数据库表映射。

- 使用 TypeORM 装饰器定义表名、字段名、字段类型、长度、nullable、comment 和关联关系。
- 数据库字段名使用 snake_case，实体属性使用 camelCase。
- `bigint` 主键在 TypeScript 中声明为 `string`。
- 关联关系使用 `@OneToMany`、`@ManyToOne` 等 TypeORM 装饰器表达。

## 四、接口与 Controller 规范

### 路由组织

- `@Controller()` 使用统一维护的路径常量，不硬编码业务路径字符串。
- 路径常量从基础设施层的 `contants/paths` 引入。
- 功能动作通过方法级路由表达。

常用动作命名：

- `@Post('create')`：创建。
- `@Post('update')`：更新。
- `@Post('delete')` 或 `@Post('delete/:id')`：删除。
- `@Get('list')`：分页列表。
- `@Get('list-all')`：无分页列表。
- `@Post('detail')`、`@Get(':id')` 或 `@Get('detail')`：详情，按已有模块风格选择。
- `@Post('login')`：登录类操作。
- `@Post('logout')`：退出登录类操作。

接口方法命名：

- 创建：`create` / `createXxx`
- 更新：`update` / `updateXxx`
- 删除：`remove` / `deleteXxx`
- 列表：`findAll` / `getXxxList`
- 详情：`findOne` / `getXxxById`

### 请求参数

- 创建、更新、删除等写操作优先使用 `@Body()`。
- 列表查询使用 `@Query()` 或显式 `@Query('field')`。
- REST 风格详情或删除可以使用 `@Param('id')`，但同一模块内保持一致。
- 分页参数使用 `current` 和 `pageSize`，不要新增 `page`。

### Swagger

Controller 类上：

- 使用 `@ApiTags('中文模块名')`。
- 使用 `@ApiExtraModels(...)` 注册统一响应类型、分页类型、响应 DTO。

接口方法上：

- 每个接口必须有 `@ApiOperation({ summary: '中文说明' })`。
- 单对象返回使用 `@ApiOkDataResponse(XxxResponseDto)`。
- 分页返回使用 `@ApiOkPagesResponse(XxxResponseDto)`。
- 数组返回使用项目已有数组响应装饰器。
- 异常场景使用 `@ApiResponse({ status, description })` 补充说明。
- 禁止使用 `@ApiOkDataResponse(Object)` 或 `@ApiOkPagesResponse(Object)`，必须传具体 DTO、Entity 或基础类型。

复杂嵌套响应可以使用 `@ApiOkResponse` + `getSchemaPath(...)`，但要同时通过 `@ApiExtraModels(...)` 注册涉及的 DTO。

### 权限与公开接口

- 后台管理类接口使用 `createPermission(PATH, '中文分组名')` 生成权限装饰器。
- 权限动作优先使用 `PERMISSIONS.CREATE`、`PERMISSIONS.READ`、`PERMISSIONS.UPDATE`、`PERMISSIONS.DELETE`、`PERMISSIONS.OPTION`。
- 每个需要权限的接口添加 `@XxxPermission(PERMISSIONS.X, '中文说明')`。
- 登录、验证码、公开回调等不需要登录的接口使用 `@Public()`。
- 获取当前用户信息优先使用 `@User()`、`@User('id')` 或 `@UserId()`，不要在 controller 中直接访问 CLS。

## 五、Service 编码规范

- Service 类使用 `@Injectable()`。
- Repository 注入写在构造函数中：

```ts
constructor(
  @InjectRepository(XxxEntity)
  private readonly xxxRepository: Repository<XxxEntity>,
) {}
```

- 创建：`repository.create(dto)` 后 `repository.save(entity)`。
- 更新：`repository.update(id, plainToInstance(Entity, dto))`，返回更新对象 ID 或业务需要的结果。
- 删除：`repository.delete(id)`。
- 详情：`repository.findOne({ where: { id } })`。
- 列表：使用 `createQueryBuilder` 组合条件，分页时返回 `{ current, total, pageSize, records }`。
- 条件查询只在参数存在时追加 `andWhere`。
- 业务异常使用 NestJS 标准异常类，例如 `ForbiddenException`、`UnauthorizedException`，或项目统一错误工具。
- 涉及缓存、登录态、token 等通用能力时复用基础设施层 service，不在业务模块中重复实现。

## 六、DTO 编码规范

- 所有字段用 `@ApiProperty` 描述。
- 必填字段使用 `@IsNotEmpty()` 和对应类型校验。
- 可选字段使用 `@IsOptional()`。
- 字符串使用 `@IsString()`，并按需要添加 `@MaxLength()`。
- 数字字段使用 `@IsNumber()` 或 `@IsInt()`；查询参数数字字段配合 `@Type(() => Number)`。
- 分页 DTO 固定使用 `current?: number` 和 `pageSize?: number`。
- 响应 DTO 字段要与真实返回结构一致，明确 `nullable`、`maxLength`、数组结构等文档信息。

## 七、Entity 编码规范

- 实体表名使用 `@Entity('table_name', { schema: 'schema_name' })` 或项目已有约定。
- 主键使用：

```ts
@PrimaryGeneratedColumn({ type: 'bigint', name: 'id' })
id: string;
```

- 字段使用 `@Column(type, { name, nullable, comment, length })`。
- 数据库字段使用 snake_case，例如 `show_status`；实体属性使用 camelCase，例如 `showStatus`。
- 字段注释必须是中文业务含义。
- 可空数据库字段在 TypeScript 中声明为 `T | null`。
- 实体关联放在实体文件中声明，避免在 service 中用散落逻辑隐式表达关联。

## 八、导入与代码风格

- 使用单引号。
- import 按来源自然分组：NestJS、第三方库、项目基础设施、当前模块 DTO/Entity/Service。
- 类和 DTO 使用 PascalCase；变量、方法、属性使用 camelCase；数据库列名使用 snake_case。
- Controller 保持薄层，只做参数接收、装饰器声明和 service 调用。
- Service 承载业务流程，不写 Swagger 和路由装饰器。
- 方法返回类型显式标注 `Promise<...>`。
- 注释只写必要的业务说明，不写“给变量赋值”这类空注释。

## 九、开发前自检清单

1. 新功能是否放在正确的业务域和功能子模块下？
2. 是否创建或更新了对应 module/controller/service/dto/entities 文件？
3. 文件名、类名是否符合本规则？
4. 业务域 module 是否通过 `TypeOrmModule.forFeature([...])` 注册实体？
5. Controller 路径是否使用路径常量？
6. 每个接口是否有中文 `@ApiOperation` 和明确的响应 DTO？
7. 是否避免了 `Object` 作为 Swagger 响应模型？
8. 权限接口是否使用 `createPermission` 和 `PERMISSIONS`？
9. 公开接口是否明确使用 `@Public()`？
10. 分页参数是否使用 `current` 和 `pageSize`？
11. Entity 字段名、类型、nullable、comment 是否与数据库一致？
12. `CLAUDE.md` 或 `AGENTS.md` 引入本规则后，开发时是否按本规则执行？

## 十、业务模块代码模板

本节提供可直接套用的模块模板。模板中：

- `Xxx` 表示实体名或业务对象名，使用 PascalCase。
- `xxx` 表示功能子模块名，使用 camelCase。
- `XXX_PATH` 表示路径常量，统一从 `infrastructure/contants/paths` 引入。
- 相对 import 层级按实际文件深度调整。

### 入口模块模板

入口模块只聚合下级模块，不写业务逻辑。

```ts
import { Module } from '@nestjs/common';
import { AuthModule } from './auth/auth.module';
import { ProductModule } from './product/product.module';

@Module({
  imports: [AuthModule, ProductModule],
  controllers: [],
  providers: [],
  exports: [],
})
export default class AdminModule {}
```

如果项目存在统一模块入口，需要将入口模块注册进去：

```ts
import { Module } from '@nestjs/common';
import AdminModule from './admin/admin.module';

@Module({
  imports: [AdminModule],
  controllers: [],
  providers: [],
  exports: [],
})
export default class IndexModule {}
```

### 业务域模块模板

业务域模块负责注册实体、controller、service 和基础设施依赖。

```ts
import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Xxx } from './entities/Xxx.entity';
import { XxxController } from './xxx/xxx.controller';
import { XxxService } from './xxx/xxx.service';
import RedisModule from '../../../infrastructure/redis/redis.module';

@Module({
  imports: [TypeOrmModule.forFeature([Xxx]), RedisModule],
  controllers: [XxxController],
  providers: [XxxService],
  exports: [XxxService],
})
export class XxxModule {}
```

### Controller 模板

CRUD 接口优先使用 `@Get`、`@Post`，路径后缀使用 `create`、`list`、`detail`、`update`、`delete`。

```ts
import { Body, Controller, Get, Post, Query } from '@nestjs/common';
import { ApiExtraModels, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { XxxService } from './xxx.service';
import { CreateXxxDto } from './dto/CreateXxx.dto';
import { UpdateXxxDto } from './dto/UpdateXxx.dto';
import { ListXxxDto } from './dto/ListXxx.dto';
import { XxxResponseDto } from './dto/XxxResponse.dto';
import { Xxx } from '../entities/Xxx.entity';
import { PageResponse } from '../../../../infrastructure/types/PageResponse';
import { ResponseReturn } from '../../../../infrastructure/utils/ResponseReturn';
import {
  ApiOkDataResponse,
  ApiOkPagesResponse,
} from '../../../../infrastructure/decorator/data.decorator';
import {
  createPermission,
  PERMISSIONS,
} from '../../../../infrastructure/decorator/permission.decorator';
import { XXX_PATH } from '../../../../infrastructure/contants/paths';

const XxxPermission = createPermission(XXX_PATH, 'Xxx管理');

@ApiTags('Xxx管理')
@ApiExtraModels(ResponseReturn, PageResponse, XxxResponseDto)
@Controller(XXX_PATH)
export class XxxController {
  constructor(private readonly xxxService: XxxService) {}

  @ApiOperation({ summary: '创建Xxx' })
  @ApiOkDataResponse(XxxResponseDto)
  @ApiResponse({ status: 400, description: '请求参数错误' })
  @XxxPermission(PERMISSIONS.CREATE, '创建Xxx')
  @Post('create')
  async create(@Body() dto: CreateXxxDto): Promise<ResponseReturn<Xxx>> {
    return ResponseReturn.success(await this.xxxService.create(dto));
  }

  @ApiOperation({ summary: '获取Xxx列表' })
  @ApiOkPagesResponse(XxxResponseDto)
  @ApiResponse({ status: 400, description: '请求参数错误' })
  @XxxPermission(PERMISSIONS.READ, '查询Xxx')
  @Get('list')
  async findAll(
    @Query() query: ListXxxDto,
  ): Promise<ResponseReturn<PageResponse<Xxx>>> {
    return ResponseReturn.success(await this.xxxService.findAll(query));
  }

  @ApiOperation({ summary: '获取Xxx详情' })
  @ApiOkDataResponse(XxxResponseDto)
  @ApiResponse({ status: 404, description: 'Xxx不存在' })
  @XxxPermission(PERMISSIONS.READ, '查询Xxx详情')
  @Post('detail')
  async findOne(@Body('id') id: string): Promise<ResponseReturn<Xxx>> {
    return ResponseReturn.success(await this.xxxService.findOne(id));
  }

  @ApiOperation({ summary: '更新Xxx' })
  @ApiOkDataResponse(XxxResponseDto)
  @ApiResponse({ status: 404, description: 'Xxx不存在' })
  @ApiResponse({ status: 400, description: '请求参数错误' })
  @XxxPermission(PERMISSIONS.UPDATE, '更新Xxx')
  @Post('update')
  async update(@Body() dto: UpdateXxxDto): Promise<ResponseReturn<number>> {
    return ResponseReturn.success(await this.xxxService.update(dto));
  }

  @ApiOperation({ summary: '删除Xxx' })
  @ApiResponse({ status: 200, description: '删除成功' })
  @ApiResponse({ status: 404, description: 'Xxx不存在' })
  @XxxPermission(PERMISSIONS.DELETE, '删除Xxx')
  @Post('delete')
  async remove(@Body('id') id: number): Promise<ResponseReturn<void>> {
    await this.xxxService.remove(id);
    return ResponseReturn.success();
  }
}
```

### C 端或公开接口 Controller 变体

C 端接口默认走登录态，不使用后台权限装饰器；公开接口必须显式添加 `@Public()`。

```ts
import { Body, Controller, Get, Post, Req } from '@nestjs/common';
import { ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { FastifyRequest } from 'fastify';
import { AuthService } from './auth.service';
import { LoginDto } from './dto/Login.dto';
import { LoginResponseDto } from './dto/LoginResponse.dto';
import { UserInfoResponseDto } from './dto/UserInfoResponse.dto';
import { ResponseReturn } from '../../../../infrastructure/utils/ResponseReturn';
import { ApiOkDataResponse } from '../../../../infrastructure/decorator/data.decorator';
import { Public } from '../../../../infrastructure/decorator/public.decorator';
import { UserId } from '../../../../infrastructure/decorator/user.decorator';
import { USER_AUTH_PATH } from '../../../../infrastructure/contants/paths';

@ApiTags('用户认证')
@Controller(USER_AUTH_PATH)
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @ApiOperation({ summary: '登录' })
  @ApiResponse({ status: 401, description: '认证失败' })
  @ApiOkDataResponse(LoginResponseDto)
  @Public()
  @Post('login')
  async login(
    @Body() dto: LoginDto,
    @Req() request: FastifyRequest,
  ): Promise<ResponseReturn<LoginResponseDto>> {
    return ResponseReturn.success(await this.authService.login(dto, request));
  }

  @ApiOperation({ summary: '获取当前用户信息' })
  @ApiOkDataResponse(UserInfoResponseDto)
  @Get('userinfo')
  async userinfo(@UserId() id: string): Promise<ResponseReturn<UserInfoResponseDto>> {
    return ResponseReturn.success(await this.authService.getUserInfo(id));
  }
}
```

### Service 模板

```ts
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { plainToInstance } from 'class-transformer';
import { Repository } from 'typeorm';
import { Xxx } from '../entities/Xxx.entity';
import { CreateXxxDto } from './dto/CreateXxx.dto';
import { UpdateXxxDto } from './dto/UpdateXxx.dto';
import { ListXxxDto } from './dto/ListXxx.dto';
import { PageResponse } from '../../../../infrastructure/types/PageResponse';

@Injectable()
export class XxxService {
  constructor(
    @InjectRepository(Xxx)
    private readonly xxxRepository: Repository<Xxx>,
  ) {}

  async create(dto: CreateXxxDto): Promise<Xxx> {
    const entity = this.xxxRepository.create(dto);
    return this.xxxRepository.save(entity);
  }

  async update(dto: UpdateXxxDto): Promise<number> {
    await this.xxxRepository.update(dto.id, plainToInstance(Xxx, dto));
    return dto.id;
  }

  async remove(id: number): Promise<void> {
    await this.xxxRepository.delete(id);
  }

  async findOne(id: string): Promise<Xxx | null> {
    return this.xxxRepository.findOne({ where: { id } });
  }

  async findAll(query: ListXxxDto): Promise<PageResponse<Xxx>> {
    const { current = 1, pageSize = 10, keyword, status } = query;
    const queryBuilder = this.xxxRepository.createQueryBuilder('xxx');

    if (keyword) {
      queryBuilder.andWhere('xxx.name LIKE :keyword', {
        keyword: `%${keyword}%`,
      });
    }

    if (status !== undefined) {
      queryBuilder.andWhere('xxx.status = :status', { status });
    }

    const [records, total] = await queryBuilder
      .skip((current - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();

    return {
      current,
      total,
      pageSize,
      records,
    };
  }
}
```

并发敏感操作使用事务和锁，优先复用项目基础设施：

```ts
import { Transactional } from 'typeorm-transactional';

@Transactional()
async consume(userId: string, amount: number): Promise<void> {
  await this.cacheService.lockCall(`balance:${userId}`, async () => {
    // 读余额 -> 校验 -> 扣减 -> 写流水，保持在同一事务内。
  });
}
```

### DTO 模板

创建 DTO：

```ts
import { ApiProperty } from '@nestjs/swagger';
import {
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsString,
  MaxLength,
} from 'class-validator';

export class CreateXxxDto {
  @ApiProperty({ description: '名称', example: '示例名称' })
  @IsNotEmpty({ message: '名称不能为空' })
  @IsString()
  @MaxLength(64, { message: '名称长度不能超过64个字符' })
  name: string;

  @ApiProperty({ description: '排序', example: 100, required: false })
  @IsOptional()
  @IsNumber()
  sort?: number;
}
```

更新 DTO：

```ts
import { ApiProperty, PartialType } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import { IsInt, Min } from 'class-validator';
import { CreateXxxDto } from './CreateXxx.dto';

export class UpdateXxxDto extends PartialType(CreateXxxDto) {
  @ApiProperty({ description: 'ID' })
  @Type(() => Number)
  @IsInt()
  @Min(1)
  id: number;
}
```

列表 DTO：

```ts
import { ApiProperty } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import { IsInt, IsOptional, IsString, Min } from 'class-validator';

export class ListXxxDto {
  @ApiProperty({ description: '页码', example: 1, required: false })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  current?: number;

  @ApiProperty({ description: '每页数量', example: 10, required: false })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  pageSize?: number;

  @ApiProperty({ description: '关键词', required: false })
  @IsOptional()
  @IsString()
  keyword?: string;
}
```

响应 DTO：

```ts
import { ApiProperty } from '@nestjs/swagger';

export class XxxResponseDto {
  @ApiProperty({ description: 'ID' })
  id: number;

  @ApiProperty({ description: '名称', maxLength: 64, nullable: true })
  name: string | null;

  @ApiProperty({ description: '排序', nullable: true })
  sort: number | null;
}
```

删除 DTO：

```ts
import { ApiProperty } from '@nestjs/swagger';
import { IsArray, IsString } from 'class-validator';

export class DeleteXxxDto {
  @ApiProperty({ description: 'ID列表', type: [String] })
  @IsArray()
  @IsString({ each: true })
  ids: string[];
}
```

### Entity 模板

```ts
import { Column, Entity, OneToMany, PrimaryGeneratedColumn } from 'typeorm';
import { Child } from './Child.entity';

@Entity('table_name', { schema: 'schema_name' })
export class Xxx {
  @PrimaryGeneratedColumn({ type: 'bigint', name: 'id' })
  id: string;

  @Column('varchar', {
    name: 'name',
    nullable: true,
    comment: '名称',
    length: 64,
  })
  name: string | null;

  @Column('int', { name: 'sort', nullable: true, comment: '排序' })
  sort: number | null;

  @Column('int', { name: 'status', nullable: true, comment: '状态：0->禁用；1->启用' })
  status: number | null;

  @Column('datetime', { name: 'create_time', nullable: true, comment: '创建时间' })
  createTime: Date | null;

  @OneToMany(() => Child, (child) => child.parent)
  children?: Child[];
}
```

关联关系模板：

```ts
import { JoinColumn, ManyToOne, OneToMany } from 'typeorm';

@OneToMany(() => Child, (child) => child.parent)
children?: Child[];

@ManyToOne(() => Parent, (parent) => parent.children)
@JoinColumn({ name: 'parent_id' })
parent?: Parent;
```

### 登录认证 Service 要点

- token 使用 `uuidv4()` 或项目既有 token 生成方式。
- token、登录态和用户信息缓存写入 Redis，key 和过期时间使用项目已有枚举或常量。
- 登出时清理 Redis 中的 token。
- 密码校验使用 `bcrypt.compare`，创建或重置密码时使用 `bcrypt.hash`。
- 登录成功后按业务需要写登录日志。
- 后续请求由认证中间件或 guard 从 token 还原用户信息，不在业务 controller 中重复解析 token。
