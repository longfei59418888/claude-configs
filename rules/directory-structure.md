# 目录结构与开发规范（Directory & Development Convention）

> 适用范围：本项目（React + TypeScript + Zustand）所有源码开发。
> 强制级别：**MUST（必须）** / **SHOULD（应当）** / **MAY（可选）**。
> 本规范只约束**目录结构、层次划分与命名**，编码逻辑细节以 ESLint / Prettier / tsconfig 为准。

---

## 0. 首要原则

1. **MUST** 遵循既有目录结构，新增文件对号入座，禁止随意放置。
2. **MUST NOT** 新增 `src` 下的一级目录；确有需要时先更新本规范登记其用途与约束，再落地。
3. **MUST** 沿用目录内既有命名与文件组织方式，不引入风格不一致的写法。
4. **SHOULD** 就近原则：只在单一位置使用的内容就近存放（页面私有组件/hooks/类型放页面内），被多处复用时再上提到通用目录。

---

## 1. 分层模型（MVVM）

| 层 | 目录 | 职责 |
| --- | --- | --- |
| Model | `src/store` | 全局状态（Zustand） |
| Service | `src/apis` | 后端接口调用与数据收发 |
| View + ViewModel | `src/components`、`src/pages` | UI 渲染与交互逻辑（`hooks.ts` 承载 ViewModel 逻辑，`index.tsx` 承载 View） |

**数据流向（MUST 单向）**：`pages / components` → `apis`（取数）/ `store`（读写状态）；`apis` 只做请求，不含 UI 逻辑；`store` 只管状态，不含渲染逻辑。

---

## 2. 目录职责与约束

### `src/apis` — 接口调用层（Service）
- **MUST** 按业务域拆分文件：`login.ts`、`admin.ts` 等，一个业务域一个文件。
- **MUST** 请求/响应类型放 `src/apis/types/<域>.ts`。
- **MUST** 仅做接口调用与数据转换，**MUST NOT** 写业务/UI 逻辑或状态操作。
- 接口地址常量 **MUST** 从 `src/constants/api.ts` 引入，不在此硬编码 URL。

### `src/store` — 状态管理（Model）
- **MUST** 每个 store 一个文件，命名 `useXxxStore.ts`（如 `useMemberInfoStore.ts`）。
- **MUST** store 状态类型放 `src/store/types/<name>.ts`。
- **MUST** 统一从 `src/store/index.ts` 导出。

### `src/components` — 通用组件（View + ViewModel）
- **MUST** 只放**跨页面复用**的组件；页面私有组件放对应页面的 `components/`。
- **MUST** 每个组件独立子目录（目录名小写，如 `layout/`），内部：
  - `index.tsx` 组件本体
  - `style.ts` / `styled.ts` 样式
  - `constants.ts` 组件内常量（可选）
  - `propsType.ts` 组件 props 类型（可选）
- **MUST NOT** 将只在某页面使用的组件放这里。

### `src/pages` — 页面（View + ViewModel）
- **MUST** 每个页面一个子目录（目录名小写驼峰，如 `login/`、`notFound/`）。
- **MUST** 页面标准文件结构见下方「§4 页面标准结构」。
- **MUST** 页面私有组件放该页面 `components/` 内，**MUST NOT** 上提到 `src/components`。

### `src/hooks` — 全局 hooks
- **MUST** 只放跨页面复用的 hooks。
- **MUST** 页面私有 hooks 放该页面目录的 `hooks.ts`，不放这里。

### `src/constants` — 常量
- **MUST** 按主题分文件：`api.ts`（接口地址）、`routes.ts` / `pages.ts`（路由/页面地址）、`menu.ts`、`storages.ts`（存储 Key）。
- **MUST** 只写常量定义，**MUST NOT** 写逻辑或副作用。

### `src/types` — 通用类型
- **MUST** 只放跨模块复用的 TS 类型（`commons.ts`、`route.ts`、`menu.ts`、`user.ts`）。
- **MUST** 接口专属类型放 `apis/types`，store 专属类型放 `store/types`，页面/组件专属类型放各自 `propsType.ts`。

### `src/utils` — 工具函数
- **MUST** 只放无副作用的纯工具函数（如 `localstorage.ts`）。
- **MUST** 不以 node_modules 引入的三方通用库放 `src/utils/libs/`，与业务解耦。

### `src/styles` — 全局样式
- **MUST** 只放全局样式与主题（`reset.ts`、`theme.ts`）。
- **MUST** 组件/页面局部样式放各自目录的 `styled.ts` / `styles.ts` / `style.ts`。

### `src/assets` — 静态资源
- **MUST** 图片、字体等静态资源，按类型/模块建子目录归类。

### `src/__tests__` — 测试
- **MUST** 测试文件统一放此目录（或与被测文件同名 `.test.ts(x)`，二选一并保持一致）。

### 根级源码文件
- `src/main.tsx` 应用入口；`src/app.tsx` 根组件；`src/router.tsx` 路由配置。**MUST** 保持这三者职责单一，不塞入业务逻辑。

---

## 3. 工程配置目录（不属于 src）

| 目录 | 用途 |
| --- | --- |
| `scripts/ops` | CI/CD（`ci.sh`、`Dockerfile`、`Jenkinsfile`、`app.conf`） |
| `jest` | 测试配置与 mocks |
| `.husky` | git hooks |

**MUST NOT** 把源码放入上述目录，也 **MUST NOT** 把构建/环境配置散落到 `src`。

---

## 4. 页面标准结构

```tree
src/pages/<page>/
├── index.tsx          # 页面入口（View）— 默认导出页面组件
├── hooks.ts           # 页面逻辑（ViewModel）— 状态、副作用、事件处理
├── styled.ts          # 页面样式（styled-components）
├── propsType.ts       # 页面/组件类型、枚举
└── components/        # 页面私有组件（仅本页面使用）
    └── <component>/
        ├── index.tsx
        ├── styles.ts
        └── propsType.ts
```

嵌套子模块（如 `pages/list/table/`）遵循同一结构：`index.tsx` + `hooks.ts` + `styles.ts` + `propsType.ts` + `utils.ts`（可选）+ `components/`。

---

## 5. 命名规范

### 5.1 目录与文件
| 类型 | 规则 | 示例 |
| --- | --- | --- |
| 组件目录 | 小写或小写驼峰 | `layout/`、`notFound/` |
| 页面目录 | 小写驼峰 | `login/`、`list/` |
| 组件/页面入口 | 固定 `index.tsx` | `index.tsx` |
| 逻辑 hooks 文件 | 固定 `hooks.ts` | `hooks.ts` |
| 样式文件 | `styled.ts` / `styles.ts` / `style.ts`（目录内保持统一） | `styled.ts` |
| 类型文件 | `propsType.ts`（组件/页面）；`types/<name>.ts`（模块） | `propsType.ts` |
| store 文件 | `useXxxStore.ts` | `useMemberInfoStore.ts` |
| 常量文件 | 主题名小写 | `api.ts`、`storages.ts` |
| 工具文件 | 功能名小写 | `localstorage.ts` |

### 5.2 代码标识符
| 类型 | 规则 | 示例 |
| --- | --- | --- |
| React 组件 | 大驼峰 PascalCase | `const Layout: FC = ...` |
| Hook | `use` 前缀 + 驼峰 | `useTable`、`useMemberInfoStore` |
| 变量 / 函数 | 小驼峰 camelCase | `getThirdParties`、`routerConfig` |
| 接口 interface | PascalCase（可选 `I` 前缀，与相邻文件保持一致） | `TableProps`、`IReturnData` |
| 类型别名 type | PascalCase | `RouteObject`、`QueryPagination` |
| 枚举 enum | 名 PascalCase，成员全大写 SNAKE | `FilterItemType.DATE_RANGE` |
| 常量 | 全大写 SNAKE_CASE | `PAGE_LOGIN`、`MEMBER_INFO_TOKEN` |
| 布尔量 | `is/has/can/should` 前缀 | `isLoading`、`hasError` |

---

## 6. 导入规范

- **MUST** 跨目录引用使用路径别名 `@src/*`（见 `tsconfig.json` paths），禁止 `../../..` 深层相对路径；同目录/相邻可用相对路径。
- **MUST** import 顺序由 `simple-import-sort` 管理，保持自动排序结果，不手动打乱。
- **SHOULD** 每个模块通过 `index.ts(x)` 对外暴露入口，隐藏内部文件结构。

---

## 7. 代码风格（由工具强制，此处仅登记基线）

- 不使用分号（`semi: false`）、单引号（含 JSX）、尾逗号 `all`。
- 缩进 2 空格、LF 换行、文件末尾保留空行（见 `.editorconfig`）。
- **MUST** 提交前通过 ESLint（含 `@typescript-eslint`、`react-hooks`、`jsx-a11y`）与 Prettier 校验。
- **MUST** 遵守 tsconfig 严格项（`noUnusedLocals`、`noUnusedParameters`、`strictNullChecks` 等），不留未使用变量与死代码。

---

## 8. 新增内容放置速查

| 我要新增… | 放到 |
| --- | --- |
| 一个后端接口 | `src/apis/<域>.ts`，类型 → `src/apis/types/<域>.ts` |
| 一个全局状态 | `src/store/useXxxStore.ts`，类型 → `src/store/types/`，并从 `index.ts` 导出 |
| 跨页面复用组件 | `src/components/<name>/`（`index.tsx` + `styled.ts`） |
| 某页面专用组件 | `src/pages/<page>/components/<name>/` |
| 跨页面 hook | `src/hooks/` |
| 页面专用 hook | 该页面的 `hooks.ts` |
| 一个常量 | `src/constants/<主题>.ts` |
| 跨模块类型 | `src/types/<name>.ts` |
| 页面/组件专属类型 | 同目录 `propsType.ts` |
| 纯工具函数 | `src/utils/`；三方库 → `src/utils/libs/` |
| 一个新页面 | `src/pages/<page>/`（按 §4 结构），并在 `src/constants/pages.ts` + `src/constants/routes.ts` 注册 |
| 图片/字体 | `src/assets/` |
| 全局样式/主题 | `src/styles/` |
