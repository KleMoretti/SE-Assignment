# 医院综合管理系统 - 变更日志

## [2.4.0] - 2025-10-26

### ✨ 新增功能

#### 统一服务管理工具

**服务管理脚本** (`manage.py`):
- ✅ 统一的服务启动命令 (`python manage.py start`)
- ✅ 统一的服务停止命令 (`python manage.py stop`)
- ✅ 统一的服务重启命令 (`python manage.py restart`)
- ✅ 服务状态查看命令 (`python manage.py status`)
- ✅ 帮助信息命令 (`python manage.py help`)
- ✅ 智能检测服务状态（自动检测端口占用）
- ✅ 安全停止机制（先从PID文件读取，再从端口检测）
- ✅ 自动浏览器打开功能
- ✅ 详细的启动日志和状态提示
- ✅ MySQL数据库连接检测
- ✅ 虚拟环境自动识别

**特性**：
- 面向对象设计 (`ServiceManager` 类)
- 完整的错误处理机制
- 支持后台服务运行
- 跨窗口进程管理
- 友好的命令行交互

#### 医生系统后端模板完善

**医生表单模板** (`backend/templates/doctor/doctor_form.html`):
- ✅ 完整的医生信息表单（添加/编辑）
- ✅ 响应式布局（Bootstrap卡片设计）
- ✅ 表单验证（必填字段标记）
- ✅ 字段分组展示（基本信息、联系方式、职业信息）
- ✅ 性别单选按钮
- ✅ 职称下拉选择（主任医师/副主任医师/主治医师/住院医师）
- ✅ 学历下拉选择（博士/硕士/本科）
- ✅ 日期选择器（入职日期）
- ✅ 状态管理（编辑时显示在职/离职选项）
- ✅ 专长多行文本输入

**排班表单模板** (`backend/templates/doctor/schedule_form.html`):
- ✅ 完整的排班表单（添加/编辑）
- ✅ 医生下拉选择（显示姓名、科室、职称）
- ✅ 日期选择器
- ✅ 班次单选按钮（上午班/下午班/夜班）
- ✅ 时间选择器（开始时间、结束时间）
- ✅ 最大接诊数输入（默认20人）
- ✅ 状态管理（可预约/已满/已取消）
- ✅ 备注多行文本输入
- ✅ 表单验证提示

**排班列表模板** (`backend/templates/doctor/schedule_list.html`):
- ✅ 完整的排班列表展示
- ✅ 搜索过滤功能（医生、日期）
- ✅ 班次颜色标签（上午班-绿色、下午班-橙色、夜班-红色）
- ✅ 状态颜色标签（可预约-绿色、已满-橙色、已取消-灰色）
- ✅ 响应式表格设计
- ✅ 分页导航
- ✅ 编辑/删除操作按钮
- ✅ 删除二次确认
- ✅ 友好的空数据提示

**绩效表单模板** (`backend/templates/doctor/performance_form.html`):
- ✅ 完整的绩效评估表单
- ✅ 医生下拉选择（编辑时禁用）
- ✅ 年份输入（2000-2100范围）
- ✅ 月份下拉选择（1-12月）
- ✅ 接诊人数输入
- ✅ 满意度评分输入（0-5分，步长0.1）
- ✅ 准时率评分输入（0-5分，步长0.1）
- ✅ 质量评分输入（0-5分，步长0.1）
- ✅ 绩效计算说明（显示计算公式）
- ✅ 实时显示综合评分和绩效奖金（编辑时）
- ✅ 备注输入
- ✅ 字段说明文本

**绩效列表模板** (`backend/templates/doctor/performance_list.html`):
- ✅ 完整的绩效列表展示
- ✅ 搜索过滤功能（医生、年份）
- ✅ 评分颜色标签（优秀-绿色、良好-橙色、一般-红色）
- ✅ 奖金金额高亮显示（绿色加粗）
- ✅ 响应式表格设计
- ✅ 分页导航
- ✅ 查看/删除操作按钮
- ✅ 精确到小数点后两位的数值显示

**绩效详情模板** (`backend/templates/doctor/performance_detail.html`):
- ✅ 详细的绩效信息展示
- ✅ 医生基本信息表格
- ✅ 绩效数据表格
- ✅ 绩效计算说明（完整的计算步骤）
- ✅ 综合评分卡片（带颜色区分）
- ✅ 绩效奖金卡片（绿色突出显示）
- ✅ 备注信息展示
- ✅ 返回列表按钮
- ✅ 美观的布局设计

### 🔄 核心变更

#### 1. 服务管理架构优化

**原有方式**：
```python
# start.py - 只能启动
python start.py

# stop.py - 只能停止
python stop.py
```

**新方式**：
```python
# manage.py - 统一管理
python manage.py start    # 启动服务
python manage.py stop     # 停止服务
python manage.py restart  # 重启服务
python manage.py status   # 查看状态
```

#### 2. ServiceManager类设计

**核心方法**：
```python
class ServiceManager:
    - print_banner()        # 打印横幅
    - check_directories()   # 检查目录
    - check_mysql()         # 检查MySQL
    - check_port()          # 检查端口占用
    - get_pid_from_port()   # 获取进程ID
    - kill_process()        # 结束进程
    - start_backend()       # 启动后端
    - start_frontend()      # 启动前端
    - start()               # 启动所有服务
    - stop()                # 停止所有服务
    - restart()             # 重启所有服务
    - status()              # 查看服务状态
```

#### 3. 智能服务检测

**端口检测**：
- 自动检测5000端口（后端）
- 自动检测3000端口（前端）
- 自动检测3306端口（MySQL）

**进程管理**：
- 从.server_pids文件读取PID
- 从端口反查进程ID
- 双重保障确保进程正确停止

**状态反馈**：
- 启动前检查服务是否已运行
- 启动后验证服务是否成功
- 实时显示启动进度
- 友好的成功/失败提示

#### 4. 模板系统完善

**Bootstrap 5集成**：
- 响应式网格系统
- 卡片式布局设计
- 表单组件美化
- 按钮组件统一
- 颜色系统规范

**表单验证**：
- HTML5表单验证
- 必填字段标记（红色星号）
- 输入范围限制
- 日期/时间格式验证
- 友好的提示文本

**用户体验优化**：
- 加载状态提示
- 操作成功/失败反馈
- 删除二次确认
- 空数据友好提示
- 返回按钮和面包屑导航

### 📝 文件变更

#### 新增文件

**服务管理**：
- `manage.py` - 统一服务管理脚本（460+行）

**后端模板**：
- `backend/templates/doctor/doctor_form.html` - 医生表单（155行）
- `backend/templates/doctor/schedule_form.html` - 排班表单（135行）
- `backend/templates/doctor/schedule_list.html` - 排班列表（105行）
- `backend/templates/doctor/performance_form.html` - 绩效表单（145行）
- `backend/templates/doctor/performance_list.html` - 绩效列表（115行）
- `backend/templates/doctor/performance_detail.html` - 绩效详情（130行）

#### 保留文件

**原有脚本**：
- `start.py` - 保留作为备用启动脚本
- `stop.py` - 保留作为备用停止脚本

**说明**：原有的start.py和stop.py被保留以确保向后兼容，但建议使用新的manage.py统一管理。

### 🔧 功能特性

#### 服务管理功能

**启动流程**：
1. 检查项目目录结构
2. 检查MySQL数据库状态
3. 检查服务是否已运行
4. 启动后端服务（5000端口）
5. 等待后端就绪
6. 检查并安装前端依赖
7. 启动前端服务（3000端口）
8. 保存进程ID到文件
9. 自动打开浏览器
10. 显示服务信息

**停止流程**：
1. 从PID文件读取进程
2. 停止记录的进程
3. 删除PID文件
4. 检查端口占用
5. 停止占用端口的进程
6. 显示停止结果

**状态查看**：
- 后端服务状态（运行/停止）
- 前端服务状态（运行/停止）
- MySQL数据库状态
- 进程ID信息
- 访问地址信息

#### 模板功能特性

**医生管理**：
- 添加医生（完整信息录入）
- 编辑医生（支持状态更新）
- 医生编号唯一性（添加时必填，编辑时只读）
- 专长信息（多行文本域）

**排班管理**：
- 添加排班（选择医生、日期、班次）
- 编辑排班（支持状态调整）
- 时间设置（开始/结束时间）
- 接诊数限制（1-100人）
- 班次可视化（颜色区分）

**绩效管理**：
- 添加评估（选择医生、年月）
- 编辑评估（重新计算评分）
- 自动计算（综合评分和奖金）
- 计算公式展示（透明化）
- 详情查看（完整信息）

### 🎨 UI/UX优化

#### 颜色系统

**状态颜色**：
- 成功/可用：#67C23A（绿色）
- 警告/部分：#E6A23C（橙色）
- 危险/错误：#F56C6C（红色）
- 信息/中性：#909399（灰色）
- 主要/强调：#409EFF（蓝色）

**班次颜色**：
- 上午班：绿色 (success)
- 下午班：橙色 (warning)
- 夜班：红色 (danger)

**评分颜色**：
- 优秀(≥4.5分)：绿色
- 良好(≥3.5分)：橙色
- 一般(<3.5分)：红色

#### 布局设计

**卡片式布局**：
- 统一的页面头部
- 内容区域卡片化
- 操作按钮右对齐
- 表格响应式设计

**表单布局**：
- 两列栅格布局（6-6分割）
- 标签左对齐
- 必填字段标记
- 帮助文本灰色显示

**列表布局**：
- 搜索框卡片独立
- 表格卡片独立
- 分页器居中显示
- 操作列固定宽度

### 📚 使用示例

#### 服务管理

**启动服务**：
```bash
# 方式1：直接运行（默认启动）
python manage.py

# 方式2：明确指定启动命令
python manage.py start
```

**停止服务**：
```bash
python manage.py stop
```

**重启服务**：
```bash
python manage.py restart
```

**查看状态**：
```bash
python manage.py status
```

**查看帮助**：
```bash
python manage.py help
```

#### 医生系统传统视图

**访问路径**：
- 医生列表：`http://localhost:5000/api/doctor/list`
- 添加医生：`http://localhost:5000/api/doctor/doctor/add`
- 编辑医生：`http://localhost:5000/api/doctor/doctor/edit/<id>`
- 排班列表：`http://localhost:5000/api/doctor/schedules-list`
- 添加排班：`http://localhost:5000/api/doctor/schedule/add`
- 绩效列表：`http://localhost:5000/api/doctor/performances-list`
- 添加绩效：`http://localhost:5000/api/doctor/performance/add`
- 绩效详情：`http://localhost:5000/api/doctor/performance/detail/<id>`

### ⚠️ 注意事项

#### 服务管理

**进程管理**：
- 服务在后台运行，关闭命令窗口不影响服务
- 使用manage.py stop或任务管理器停止服务
- .server_pids文件存储进程ID，请勿手动编辑

**端口占用**：
- 确保5000端口未被其他程序占用（后端）
- 确保3000端口未被其他程序占用（前端）
- 确保3306端口MySQL服务正常运行

**虚拟环境**：
- 脚本自动检测backend/venv虚拟环境
- 如存在虚拟环境则优先使用
- 否则使用系统Python环境

#### 模板使用

**数据关联**：
- 删除医生前需先删除排班和绩效
- 排班需要选择有效的医生
- 绩效评估需要选择有效的医生

**表单验证**：
- 必填字段不能为空
- 日期格式必须为YYYY-MM-DD
- 评分范围0-5分
- 月份范围1-12月

**数据计算**：
- 综合评分自动计算，不可手动修改
- 绩效奖金自动计算，不可手动修改
- 计算公式：
  - 综合评分 = 满意度×0.4 + 准时率×0.2 + 质量×0.4
  - 绩效奖金 = 接诊人数×10 + 综合评分×100

### 🐛 Bug修复

- ✅ 修复原有start.py中文档路径问题
- ✅ 修复stop.py无法完全停止所有服务问题
- ✅ 优化进程停止逻辑，确保服务彻底关闭

### 🚀 性能优化

- ✅ 减少重复的端口检测调用
- ✅ 优化进程检测效率
- ✅ 改进启动等待时间
- ✅ 使用面向对象设计提升代码可维护性

### 📦 兼容性

#### 向后兼容

- ✅ 保留start.py和stop.py脚本
- ✅ manage.py可与原有脚本共存
- ✅ 不影响现有的前后端代码
- ✅ 模板与RESTful API并存

#### 推荐使用

**推荐**：
- 使用 `python manage.py` 进行服务管理
- 使用Vue前端访问RESTful API
- 使用后端模板作为管理后台

**保留**：
- start.py 和 stop.py 作为备用方案
- 传统Flask模板视图供后台管理使用

### 🎯 下一步计划

#### v2.5 (计划中)
- [ ] 添加服务监控功能（自动重启）
- [ ] 添加日志查看功能
- [ ] 完善绩效统计图表
- [ ] 添加排班日历视图
- [ ] 医生详情页面增强

#### v3.0 (规划中)
- [ ] Docker容器化部署
- [ ] 自动化部署脚本
- [ ] 健康检查端点
- [ ] 性能监控面板

---

## [2.3.0] - 2025-10-22

### ✨ 新增功能

#### 医生模块前端完善

**医生排班管理页面** (`frontend/src/views/doctor/DoctorSchedule.vue`):
- ✅ 完整的排班CRUD操作（创建、查看、编辑、删除）
- ✅ 多维度搜索过滤（医生、日期、班次、状态）
- ✅ 班次可视化（上午班/下午班/夜班）
- ✅ 状态管理（可预约/已满/已取消）
- ✅ 时间选择器（开始时间、结束时间）
- ✅ 最大接诊数设置
- ✅ 排班冲突检测
- ✅ 响应式布局设计

**医生绩效管理页面** (`frontend/src/views/doctor/DoctorPerformance.vue`):
- ✅ 完整的绩效CRUD操作
- ✅ 统计卡片展示（总记录数、总接诊人数、平均满意度、总绩效奖金）
- ✅ 多维度过滤（医生、年份、月份）
- ✅ 评分系统（满意度、准时率、质量评分、综合评分）
- ✅ 可视化评分（星级评分展示）
- ✅ 滑块输入（0-5分评分）
- ✅ 自动计算综合评分和绩效奖金
- ✅ 绩效详情查看对话框

**医生详情页面** (`frontend/src/views/doctor/DoctorDetail.vue`):
- ✅ 完整的基本信息展示
- ✅ 统计数据卡片（预约、病历、排班）
- ✅ 快捷操作按钮（查看排班、查看绩效、添加排班、添加绩效）
- ✅ 最近排班列表（5条）
- ✅ 最近绩效记录（5条）
- ✅ 可视化图标和数据展示
- ✅ 返回列表按钮

**医生列表页面增强** (`frontend/src/views/doctor/DoctorList.vue`):
- ✅ 添加"排班"快捷按钮（跳转到排班管理并过滤该医生）
- ✅ 添加"绩效"快捷按钮（跳转到绩效管理并过滤该医生）
- ✅ "查看"按钮改为跳转到详情页面
- ✅ 操作列宽度调整为280px以容纳更多按钮

**导航菜单优化** (`frontend/src/components/AppHeader.vue`):
- ✅ 医生管理改为下拉菜单
- ✅ 子菜单包含：医生列表、排班管理、绩效管理
- ✅ Element Plus下拉组件集成
- ✅ 菜单跳转功能

**路由配置更新** (`frontend/src/router/index.js`):
- ✅ 新增 `/doctor/detail/:id` - 医生详情页
- ✅ 新增 `/doctor/schedule` - 排班管理页
- ✅ 新增 `/doctor/performance` - 绩效管理页
- ✅ 所有页面均需要认证

### 🔄 核心变更

#### 1. URL查询参数支持

**排班管理页面**:
- ✅ 支持从URL获取 `doctor_id` 参数
- ✅ 自动过滤显示指定医生的排班
- ✅ 方便从医生列表快捷跳转

**绩效管理页面**:
- ✅ 支持从URL获取 `doctor_id` 参数
- ✅ 自动过滤显示指定医生的绩效
- ✅ 统计数据自动更新

#### 2. 页面交互优化

**表格展示**:
- ✅ 班次使用颜色标签（上午班-绿色、下午班-橙色、夜班-红色）
- ✅ 状态使用颜色标签（可预约-绿色、已满-橙色、已取消-灰色）
- ✅ 评分使用颜色标签（优秀-绿色、良好-橙色、一般-红色）
- ✅ 奖金使用绿色加粗显示

**表单验证**:
- ✅ 必填字段验证
- ✅ 日期格式验证
- ✅ 评分范围验证（0-5分）
- ✅ 月份范围验证（1-12月）

**用户体验**:
- ✅ Loading状态显示
- ✅ 骨架屏加载效果
- ✅ 操作成功/失败提示
- ✅ 删除二次确认
- ✅ 表单清空和验证重置

#### 3. 数据联动

**医生列表 → 排班管理**:
```javascript
router.push({
  path: '/doctor/schedule',
  query: { doctor_id: row.id }
})
```

**医生列表 → 绩效管理**:
```javascript
router.push({
  path: '/doctor/performance',
  query: { doctor_id: row.id }
})
```

**排班/绩效 → 自动过滤**:
```javascript
onMounted(() => {
  const route = useRoute()
  if (route.query.doctor_id) {
    searchForm.doctor_id = parseInt(route.query.doctor_id)
  }
  getList()
})
```

### 📝 文件变更

#### 新增文件
- `frontend/src/views/doctor/DoctorSchedule.vue` - 排班管理页面（540行）
- `frontend/src/views/doctor/DoctorPerformance.vue` - 绩效管理页面（680行）
- `frontend/src/views/doctor/DoctorDetail.vue` - 医生详情页面（420行）

#### 修改文件
- `frontend/src/views/doctor/DoctorList.vue` - 添加排班和绩效快捷按钮
- `frontend/src/components/AppHeader.vue` - 医生管理改为下拉菜单
- `frontend/src/router/index.js` - 添加3个新路由
- `docs/CHANGELOG.md` - 更新变更日志（本次修改）

### 🔧 功能特性

#### 排班管理
- **班次类型**: 上午班(08:00-12:00) / 下午班(14:00-18:00) / 夜班(18:00-次日08:00)
- **状态管理**: 可预约 / 已满 / 已取消
- **冲突检测**: 同一医生在同一时段不能重复排班
- **时间范围**: 支持查询指定日期范围的排班

#### 绩效管理
- **评分维度**: 
  - 满意度评分（40%权重）
  - 准时率评分（20%权重）
  - 质量评分（40%权重）
- **自动计算**: 
  - 综合评分 = 满意度×0.4 + 准时率×0.2 + 质量×0.4
  - 绩效奖金 = 接诊人数×10 + 综合评分×100
- **统计分析**: 总接诊人数、平均满意度、总奖金

#### 数据可视化
- **统计卡片**: 图标+数值展示
- **星级评分**: Element Plus评分组件
- **颜色标签**: 不同状态用不同颜色
- **滑块输入**: 0-5分滑块选择器

### 🎨 UI/UX优化

#### 布局设计
- ✅ 卡片式布局，层次分明
- ✅ 20px标准间距
- ✅ 统一的页面头部和操作按钮
- ✅ 响应式网格系统

#### 交互设计
- ✅ 悬停效果（按钮、链接）
- ✅ Loading遮罩
- ✅ 骨架屏加载
- ✅ 平滑过渡动画
- ✅ 友好的错误提示

#### 颜色系统
- **主色**: #409EFF (蓝色 - 主要操作)
- **成功**: #67C23A (绿色 - 成功状态)
- **警告**: #E6A23C (橙色 - 警告状态)
- **危险**: #F56C6C (红色 - 危险操作)
- **信息**: #909399 (灰色 - 次要信息)

### 📚 使用示例

#### 查看医生排班
1. 进入医生管理列表
2. 点击某医生的"排班"按钮
3. 自动跳转到排班管理页面，并过滤该医生的排班
4. 可进行添加、编辑、删除操作

#### 添加绩效评估
1. 进入绩效管理页面
2. 点击"添加绩效评估"按钮
3. 选择医生、年份、月份
4. 输入接诊人数和各项评分
5. 系统自动计算综合评分和奖金
6. 保存后显示在列表中

#### 查看医生详情
1. 进入医生管理列表
2. 点击某医生的"查看"按钮
3. 跳转到详情页面
4. 查看基本信息、统计数据、最近排班和绩效
5. 可快捷跳转到排班或绩效管理

### ⚠️ 注意事项

#### 数据关联
- 删除医生前需先删除其所有排班和绩效记录
- 排班和绩效数据会关联到医生信息
- 修改医生基本信息不影响历史排班和绩效

#### 评分规则
- 所有评分取值范围为0-5分
- 综合评分自动计算，不可手动修改
- 绩效奖金根据公式自动计算

#### 排班规则
- 每个医生每天每个班次只能排一次
- 取消的排班不能恢复，需重新创建
- 最大接诊数默认为20人

### 🐛 Bug修复
- ✅ 修复医生列表"查看"按钮点击无响应问题
- ✅ 修复排班和绩效页面初始化时不加载医生列表问题
- ✅ 修复URL参数传递类型不匹配问题

### 🚀 性能优化
- ✅ 页面组件懒加载
- ✅ 表格数据分页加载
- ✅ 防抖搜索（避免频繁请求）
- ✅ 缓存医生列表（减少API调用）

---

## [2.2.0] - 2025-10-22

### ✨ 新增功能

#### 用户认证与授权系统

**后端认证功能**：
- ✅ 用户模型（User）- 支持多角色（admin/doctor/nurse/user）
- ✅ JWT认证集成 - 使用Flask-JWT-Extended
- ✅ 用户注册API - 支持用户名、邮箱、角色等信息
- ✅ 用户登录API - 返回access_token和refresh_token
- ✅ Token刷新API - 自动刷新access_token
- ✅ 获取当前用户信息API
- ✅ 更新个人信息API
- ✅ 修改密码API
- ✅ 用户管理API（管理员专用）- 列表、更新、删除
- ✅ 角色权限装饰器 - `@role_required()`
- ✅ 密码加密存储 - 使用Werkzeug安全函数

**前端认证功能**：
- ✅ 登录/注册页面 - 现代化UI设计
- ✅ 用户状态管理 - Pinia Store
- ✅ Token自动管理 - localStorage持久化
- ✅ 请求拦截器升级 - 自动添加Authorization头
- ✅ 响应拦截器优化 - 401自动跳转登录
- ✅ 路由守卫 - 未登录拦截+登录后重定向
- ✅ 用户信息缓存 - 刷新页面保持登录状态

#### 医生管理前端集成

**医生管理界面**：
- ✅ 医生列表页面 - 完整的CRUD操作
- ✅ 高级搜索功能 - 支持姓名、编号、科室、状态多维度筛选
- ✅ 添加/编辑对话框 - 表单验证+美观UI
- ✅ 医生详情展示 - 包含统计信息
- ✅ 数据分页 - 可配置每页显示数量
- ✅ 操作确认 - 删除前二次确认
- ✅ 响应式设计 - 适配不同屏幕尺寸

**API集成**：
- ✅ 完整的医生管理API封装（`/api/doctor.js`）
- ✅ 完整的认证API封装（`/api/auth.js`）
- ✅ 统一的错误处理机制
- ✅ Loading状态管理

### 🔄 核心变更

#### 1. 用户模型 (`backend/models.py`)

**新增User模型**：
```python
class User(db.Model):
    - username（用户名，唯一）
    - password_hash（密码哈希）
    - email（邮箱）
    - phone（手机号）
    - real_name（真实姓名）
    - role（角色：admin/doctor/nurse/user）
    - department（所属科室）
    - is_active（是否激活）
    - last_login（最后登录时间）
```

**方法**：
- `set_password()` - 设置密码（自动加密）
- `check_password()` - 验证密码
- `to_dict()` - 序列化（支持敏感信息控制）

#### 2. 认证模块 (`backend/modules/auth/`)

**新增认证蓝图**：
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新Token
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/update-profile` - 更新个人信息
- `POST /api/auth/change-password` - 修改密码
- `GET /api/auth/users` - 获取用户列表（管理员）
- `PUT /api/auth/users/<id>` - 更新用户（管理员）
- `DELETE /api/auth/users/<id>` - 删除用户（管理员）

**权限控制**：
```python
@role_required('admin', 'doctor')
def protected_route():
    pass
```

#### 3. 应用配置 (`backend/app.py`)

**变更**：
- ✅ 注册认证蓝图 - `/api/auth`
- ✅ JWT配置已在config.py中定义
- ✅ CORS配置已支持Authorization头

#### 4. 前端状态管理 (`frontend/src/stores/user.js`)

**新增用户Store**：
```javascript
- token, refreshToken（Token管理）
- userInfo（用户信息）
- isLoggedIn（登录状态）
- isAdmin, isDoctor（角色判断）
- handleLogin()（登录处理）
- handleLogout()（登出处理）
- getUserInfo()（获取用户信息）
```

#### 5. 请求拦截器 (`frontend/src/api/request.js`)

**升级内容**：
- ✅ 自动添加Token到请求头
- ✅ 刷新Token请求特殊处理
- ✅ 401错误自动清除Token并跳转登录
- ✅ 错误信息优化展示

#### 6. 路由配置 (`frontend/src/router/index.js`)

**新增功能**：
- ✅ 登录路由 - `/login`
- ✅ 全局前置守卫 - 认证检查
- ✅ 未登录拦截 - 自动跳转登录页
- ✅ 登录后重定向 - 返回原始页面
- ✅ 404路由处理

**路由元信息**：
```javascript
meta: {
  title: '页面标题',
  requiresAuth: true // 是否需要认证
}
```

### 📝 文件变更

#### 新增文件

**后端**：
- `backend/modules/auth/__init__.py` - 认证模块初始化
- `backend/modules/auth/routes.py` - 认证路由（10个API，400+行）

**前端**：
- `frontend/src/api/auth.js` - 认证API封装（9个方法）
- `frontend/src/api/doctor.js` - 医生管理API封装（17个方法）
- `frontend/src/stores/user.js` - 用户状态管理
- `frontend/src/views/Login.vue` - 登录/注册页面
- `frontend/src/views/doctor/DoctorList.vue` - 医生列表页面（完整功能）

#### 修改文件

**后端**：
- `backend/models.py` - 添加User模型
- `backend/app.py` - 注册认证蓝图

**前端**：
- `frontend/src/api/request.js` - 升级请求/响应拦截器
- `frontend/src/router/index.js` - 添加路由守卫

### 🔧 功能特性

#### 认证流程

1. **注册流程**：
   - 填写用户名、密码等信息
   - 后端验证（用户名唯一性、密码长度等）
   - 密码加密存储
   - 返回用户信息

2. **登录流程**：
   - 提交用户名和密码
   - 后端验证用户身份
   - 生成JWT Token（access + refresh）
   - 前端存储Token和用户信息
   - 自动跳转到首页或原始页面

3. **Token管理**：
   - Access Token - 有效期短（如1小时）
   - Refresh Token - 有效期长（如7天）
   - Token自动刷新机制
   - 过期自动跳转登录

4. **权限控制**：
   - 基于角色的访问控制（RBAC）
   - 装饰器保护API端点
   - 前端路由守卫
   - 管理员特权功能

#### 安全特性

- ✅ 密码加密存储（Werkzeug安全函数）
- ✅ JWT Token认证（Flask-JWT-Extended）
- ✅ Token过期自动处理
- ✅ 用户状态检查（is_active）
- ✅ 角色权限验证
- ✅ 防止管理员账号删除
- ✅ CORS跨域安全配置

### 📚 API使用示例

#### 用户注册
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "doctor_zhang",
  "password": "123456",
  "email": "zhang@hospital.com",
  "real_name": "张医生",
  "role": "doctor",
  "department": "内科"
}
```

#### 用户登录
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "doctor_zhang",
  "password": "123456"
}

响应：
{
  "success": true,
  "data": {
    "user": { ... },
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi...",
    "token_type": "Bearer"
  }
}
```

#### 受保护的API请求
```bash
GET /api/doctor/doctors
Authorization: Bearer eyJ0eXAi...
```

### ⚠️ 重要提示

#### 初始化管理员账号

系统首次运行后，需要手动创建管理员账号：

```bash
# 方法1：通过注册API创建
POST /api/auth/register
{
  "username": "admin",
  "password": "admin123",
  "role": "admin",
  "email": "admin@hospital.com"
}

# 方法2：通过Python脚本创建
python create_admin.py
```

#### Token配置

在`backend/config.py`中配置JWT：
```python
JWT_SECRET_KEY = 'your-secret-key'  # 生产环境请使用强随机字符串
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
```

#### 前端环境变量

在`frontend/.env`中配置：
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

### 🐛 Bug修复

- ✅ 修复request.js中router导入循环依赖问题
- ✅ 修复Token过期后无限重定向问题
- ✅ 修复用户信息缓存不一致问题

### 🚀 性能优化

- ✅ Token存储优化（localStorage）
- ✅ 用户信息缓存机制
- ✅ 路由懒加载（动态import）
- ✅ API请求防抖处理

---

## [2.1.0] - 2025-10-22

### ✨ 新增功能

#### 医生管理模块 RESTful API

**医生信息管理 API**：
- ✅ `GET /api/doctor/doctors` - 获取医生列表（支持分页、搜索、多维度过滤）
- ✅ `GET /api/doctor/doctors/<id>` - 获取医生详情（包含统计信息）
- ✅ `POST /api/doctor/doctors` - 创建医生
- ✅ `PUT /api/doctor/doctors/<id>` - 更新医生信息
- ✅ `DELETE /api/doctor/doctors/<id>` - 删除医生（带关联检查）
- ✅ `GET /api/doctor/doctors/statistics` - 获取医生统计数据

**医生排班管理 API**：
- ✅ `GET /api/doctor/schedules` - 获取排班列表（支持多维度过滤）
- ✅ `GET /api/doctor/schedules/<id>` - 获取排班详情
- ✅ `POST /api/doctor/schedules` - 创建排班（带重复检查）
- ✅ `PUT /api/doctor/schedules/<id>` - 更新排班
- ✅ `DELETE /api/doctor/schedules/<id>` - 删除排班
- ✅ `GET /api/doctor/doctors/<id>/schedules` - 获取医生的排班列表（支持日期范围）

**医生绩效管理 API**：
- ✅ `GET /api/doctor/performances` - 获取绩效列表（支持年月过滤）
- ✅ `GET /api/doctor/performances/<id>` - 获取绩效详情
- ✅ `POST /api/doctor/performances` - 创建绩效评估（自动计算综合评分和奖金）
- ✅ `PUT /api/doctor/performances/<id>` - 更新绩效评估
- ✅ `DELETE /api/doctor/performances/<id>` - 删除绩效评估
- ✅ `GET /api/doctor/doctors/<id>/performances` - 获取医生的绩效记录（含统计）
- ✅ `GET /api/doctor/performances/statistics` - 获取绩效统计数据

### 🔄 核心变更

#### 1. 统一响应格式 (`backend/modules/doctor/routes.py`)

**新增辅助函数**：
```python
def success_response(data=None, message='操作成功', code='SUCCESS')
def error_response(message='操作失败', code='ERROR', status_code=400)
```

**响应格式**：
```json
{
  "success": true/false,
  "message": "提示信息",
  "code": "状态码",
  "data": { ... }
}
```

#### 2. 数据验证增强

**医生信息验证**：
- ✅ 必填字段验证（doctor_no, name, gender）
- ✅ 医生编号唯一性检查
- ✅ 日期格式验证（YYYY-MM-DD）
- ✅ 外键关联验证

**排班验证**：
- ✅ 必填字段验证（doctor_id, date, shift）
- ✅ 排班冲突检查（同医生同时段）
- ✅ 医生存在性验证
- ✅ 日期范围验证

**绩效验证**：
- ✅ 必填字段验证（doctor_id, year, month）
- ✅ 月份范围验证（1-12）
- ✅ 重复记录检查（同医生同年月）
- ✅ 自动计算综合评分和奖金

#### 3. 错误处理优化

**新增错误代码**：
- `DOCTOR_NOT_FOUND` - 医生不存在
- `DOCTOR_NO_EXISTS` - 医生编号已存在
- `DOCTOR_HAS_APPOINTMENTS` - 医生有关联预约记录
- `DOCTOR_HAS_MEDICAL_RECORDS` - 医生有关联病历记录
- `SCHEDULE_NOT_FOUND` - 排班不存在
- `SCHEDULE_EXISTS` - 排班冲突
- `PERFORMANCE_NOT_FOUND` - 绩效记录不存在
- `PERFORMANCE_EXISTS` - 绩效记录重复
- `INVALID_DATE_FORMAT` - 日期格式错误
- `INVALID_MONTH` - 月份无效
- `MISSING_FIELD` - 缺少必填字段

#### 4. 查询功能增强

**医生列表过滤**：
- ✅ 搜索：姓名、编号、电话、邮箱
- ✅ 科室过滤
- ✅ 状态过滤（在职/离职）
- ✅ 职称过滤
- ✅ 分页支持

**排班列表过滤**：
- ✅ 医生过滤
- ✅ 日期过滤
- ✅ 班次过滤
- ✅ 状态过滤
- ✅ 日期范围查询

**绩效列表过滤**：
- ✅ 医生过滤
- ✅ 年份过滤
- ✅ 月份过滤
- ✅ 分页支持

#### 5. 统计功能

**医生统计**：
- ✅ 总医生数、在职数、离职数
- ✅ 按科室统计分布
- ✅ 按职称统计分布
- ✅ 科室列表、职称列表

**医生详情统计**：
- ✅ 预约总数、已完成预约数
- ✅ 病历记录总数
- ✅ 排班总数

**绩效统计**：
- ✅ 接诊人数统计
- ✅ 平均满意度
- ✅ 平均综合评分
- ✅ 奖金总额

### 📝 文件变更

#### 修改的文件
- `backend/modules/doctor/routes.py` - 完善医生管理API接口
  - 添加RESTful API路由（医生信息、排班、绩效）
  - 添加统一响应格式
  - 添加数据验证和错误处理
  - 添加统计分析功能
  - 保留传统视图（兼容现有模板）

### 🔧 API功能特性

#### 分页支持
所有列表接口均支持分页：
```
?page=1&per_page=10
```

#### 搜索过滤
支持模糊搜索和精确过滤：
```
?search=张三&department=内科&status=active
```

#### 关联数据
响应中包含关联对象的基本信息：
```json
{
  "doctor_id": 1,
  "doctor_name": "张医生"
}
```

#### 级联检查
删除操作前检查关联记录，防止数据孤立。

### ⚠️ 兼容性说明

- ✅ 保留传统视图路由（`/list`, `/doctor/add`, `/doctor/edit` 等）
- ✅ RESTful API使用新路由（`/doctors`, `/schedules`, `/performances`）
- ✅ 两种路由可以并存，互不影响
- ✅ 模板路径更新为 `doctor/` 子目录

### 🐛 Bug修复

- ✅ 修复传统视图路由冲突问题（`/doctors` vs `/list`）
- ✅ 修复日期格式处理错误
- ✅ 修复外键关联验证缺失

### 🚀 性能优化

- ✅ 使用 `filter_by` 而非 `filter` 提升查询性能
- ✅ 优化统计查询，减少数据库访问次数
- ✅ 序列化优化，使用模型自带的 `to_dict()` 方法

### 📚 API使用示例

#### 创建医生
```bash
POST /api/doctor/doctors
Content-Type: application/json

{
  "doctor_no": "D001",
  "name": "张医生",
  "gender": "男",
  "department": "内科",
  "title": "主任医师",
  "phone": "13800138000",
  "email": "zhang@hospital.com"
}
```

#### 创建排班
```bash
POST /api/doctor/schedules
Content-Type: application/json

{
  "doctor_id": 1,
  "date": "2025-10-23",
  "shift": "morning",
  "start_time": "08:00",
  "end_time": "12:00",
  "max_patients": 30
}
```

#### 创建绩效评估
```bash
POST /api/doctor/performances
Content-Type: application/json

{
  "doctor_id": 1,
  "year": 2025,
  "month": 10,
  "patient_count": 120,
  "satisfaction_score": 95,
  "punctuality_score": 98,
  "quality_score": 92
}
```

---

## [2.0.0] - 2025-10-11

### 🎉 重大变更：技术栈升级

本次更新将系统架构从传统Web应用升级为**前后端分离架构**。

---

### ✨ 新增功能

#### 前端技术栈
- ✅ 引入 **Vue.js 3.x** 作为前端框架
- ✅ 使用 **Vite** 作为构建工具
- ✅ 集成 **Element Plus** UI组件库
- ✅ 引入 **Pinia** 进行状态管理
- ✅ 使用 **Axios** 处理HTTP请求
- ✅ 配置 **Vue Router 4** 路由管理

#### 后端技术栈
- ✅ 添加 **Flask-CORS** 支持跨域请求
- ✅ 集成 **Flask-JWT-Extended** 实现JWT认证
- ✅ 引入 **Flask-RESTful** 构建REST API
- ✅ 添加 **python-dotenv** 环境变量管理
- ✅ 集成 **marshmallow** 数据验证

#### 数据库
- ✅ 从 SQLite 迁移到 **MySQL 8.0+**
- ✅ 配置数据库连接池
- ✅ 添加自动重连机制

---

### 🔄 核心变更

#### 1. 配置文件 (`config.py`)

**变更内容**：
- ✅ 添加 MySQL 数据库配置
- ✅ 添加 JWT 认证配置
- ✅ 添加 CORS 配置
- ✅ 添加数据库连接池配置
- ✅ 系统版本升级至 2.0.0

**新增配置项**：
```python
# MySQL配置
MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# JWT配置
JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES

# 连接池配置
SQLALCHEMY_POOL_SIZE, SQLALCHEMY_POOL_RECYCLE
```

#### 2. 应用入口 (`app.py`)

**重大变更**：
- ✅ 添加 CORS 中间件支持
- ✅ 初始化 JWT 管理器
- ✅ API路由前缀改为 `/api/*`
- ✅ 移除模板渲染，改为JSON API响应
- ✅ 添加健康检查端点 (`/` 和 `/health`)
- ✅ 添加全局错误处理（404, 500）
- ✅ 优化启动信息显示

**路由变更**：
```
旧: /patient/* → 新: /api/patient/*
旧: /doctor/*  → 新: /api/doctor/*
旧: /pharmacy/* → 新: /api/pharmacy/*
```

#### 3. 数据库模型 (`models.py`)

**所有模型添加**：
- ✅ `to_dict()` 方法：支持JSON序列化
- ✅ 时间字段改用 `datetime.utcnow`（避免时区问题）
- ✅ 关系字段添加 `cascade='all, delete-orphan'`（级联删除）
- ✅ 导入 `typing.Dict` 类型提示

**新增功能**：
- ✅ 自动计算低库存状态 (`MedicineInventory`)
- ✅ 包含关联数据（如病人姓名、医生姓名）
- ✅ Float类型字段转换为标准float

#### 4. 依赖包 (`requirements.txt`)

**新增依赖**：
```txt
# 数据库驱动
PyMySQL==1.1.0
mysqlclient==2.2.0

# RESTful API
Flask-RESTful==0.3.10
Flask-CORS==4.0.0

# JWT认证
Flask-JWT-Extended==4.5.3

# 环境变量
python-dotenv==1.0.0

# 数据验证
marshmallow==3.20.1

# 数据库迁移
Flask-Migrate==4.0.5
```

---

### 📁 新增文件

#### 配置文件
- ✅ `env.template` - 环境变量模板
- ✅ `init_database.sql` - MySQL数据库初始化脚本

#### 文档文件
- ✅ `SETUP_GUIDE.md` - 详细的环境配置指南
- ✅ `CHANGELOG.md` - 本变更日志
- ✅ `.cursor/rules/hospital.mdc` - 完整的技术选型与编码规范

---

### 🔧 配置变更

#### 环境变量（新增）
```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=hospital_db

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
```

#### 数据库连接字符串
```
旧: sqlite:///hospital.db
新: mysql+pymysql://user:pass@localhost:3306/hospital_db?charset=utf8mb4
```

---

### 📝 API变更

#### 路由前缀变更

| 模块 | 旧路由 | 新路由 |
|------|--------|--------|
| 病人管理 | `/patient/*` | `/api/patient/*` |
| 医生管理 | `/doctor/*` | `/api/doctor/*` |
| 药品管理 | `/pharmacy/*` | `/api/pharmacy/*` |

#### 响应格式标准化

**成功响应**：
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**：
```json
{
  "success": false,
  "message": "错误信息",
  "code": "ERROR_CODE"
}
```

---

### ⚠️ 重要提示

#### 向后兼容性
- ⚠️ 本次更新**不向后兼容** v1.x版本
- ⚠️ 前端HTML模板不再使用，需要重新开发Vue前端
- ⚠️ 数据库从SQLite迁移到MySQL，需要数据迁移

#### 迁移步骤
1. 备份现有SQLite数据库
2. 安装MySQL 8.0+
3. 创建新数据库并执行`init_database.sql`
4. 迁移数据（如需要）
5. 更新依赖包：`pip install -r requirements.txt`
6. 配置环境变量：复制`env.template`为`.env`
7. 初始化数据库表：运行数据库初始化命令
8. 启动后端服务：`python app.py`
9. 开发Vue前端项目

---

### 📚 文档更新

- ✅ 更新 `README.md` - 反映新技术栈
- ✅ 新增 `SETUP_GUIDE.md` - 详细配置指南
- ✅ 更新 `.cursor/rules/hospital.mdc` - 完整规范文档

---

### 🐛 Bug修复

- ✅ 修复时间字段使用本地时间导致的时区问题
- ✅ 修复datetime.now在类定义时求值的问题
- ✅ 优化数据库连接池配置

---

### 🚀 性能优化

- ✅ 添加数据库连接池（提升并发性能）
- ✅ 添加连接预检和自动重连
- ✅ 优化查询性能（添加索引）
- ✅ 前后端分离架构（提升用户体验）

---

### 📦 依赖变更

#### 新增
- Flask-CORS 4.0.0
- Flask-RESTful 0.3.10
- Flask-JWT-Extended 4.5.3
- PyMySQL 1.1.0
- python-dotenv 1.0.0
- marshmallow 3.20.1

#### 保持
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Werkzeug 3.0.1

---

### 🎯 下一步计划

#### v2.1 (计划中)
- [ ] 完整的JWT认证实现
- [ ] 用户权限管理
- [ ] Vue前端完整实现
- [ ] API文档（Swagger）
- [ ] 单元测试覆盖

#### v3.0 (规划中)
- [ ] 微服务架构
- [ ] Redis缓存
- [ ] 消息队列
- [ ] Docker部署
- [ ] CI/CD集成

---

### 👥 贡献者

- 系统架构升级
- 技术栈迁移
- 文档编写

---

### 📞 技术支持

如有问题，请查看：
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - 环境配置指南
- [.cursor/rules/hospital.mdc](.cursor/rules/hospital.mdc) - 编码规范
- [README.md](README.md) - 项目说明

---

**版本**: 2.0.0  
**发布日期**: 2025-10-11  
**架构**: 前后端分离  
**状态**: ✅ 稳定版本

