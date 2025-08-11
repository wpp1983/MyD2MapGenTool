# 测试文档

本目录包含了MyMapGenTool项目的所有测试用例。

## 测试结构

```
tests/
├── __init__.py                    # 测试模块初始化
├── test_cliff_constraints.py     # 悬崖约束规则测试
├── test_template_loader.py       # 模板加载器测试
├── test_integration.py           # 集成测试
└── README.md                     # 本文档
```

## 测试分类

### 1. 单元测试 (Unit Tests)
- `test_template_loader.py` - 测试模板加载器的各个功能
- `test_cliff_constraints.py` - 测试悬崖生成约束逻辑

### 2. 集成测试 (Integration Tests)
- `test_integration.py` - 测试整体功能集成
- 包含性能测试和错误处理测试

### 3. 约束测试 (Constraint Tests)
- `test_cliff_constraints.py` - 专门测试悬崖生成规则
- 使用参数化测试覆盖多个随机种子

## 运行测试

### 使用Poetry运行所有测试
```bash
poetry run pytest
```

### 运行特定测试文件
```bash
poetry run pytest tests/test_cliff_constraints.py
```

### 运行详细模式
```bash
poetry run pytest -v
```

### 运行特定测试类
```bash
poetry run pytest tests/test_cliff_constraints.py::TestCliffConstraints
```

### 运行特定测试方法
```bash
poetry run pytest tests/test_cliff_constraints.py::TestCliffConstraints::test_cliff_basic_constraints
```

### 使用便捷脚本
```bash
# 运行所有测试
python run_tests.py all

# 运行特定测试文件
python run_tests.py test_cliff_constraints.py

# 详细模式
python run_tests.py verbose

# 覆盖率测试（需要安装pytest-cov）
python run_tests.py coverage
```

## 测试标记 (Markers)

### 可用标记
- `@pytest.mark.slow` - 标记慢速测试
- `@pytest.mark.integration` - 标记集成测试
- `@pytest.mark.unit` - 标记单元测试

### 运行特定标记的测试
```bash
# 只运行单元测试
poetry run pytest -m unit

# 跳过慢速测试
poetry run pytest -m "not slow"

# 只运行集成测试
poetry run pytest -m integration
```

## 参数化测试

悬崖约束测试使用了参数化测试来验证多个随机种子：

```python
@pytest.mark.parametrize("seed", [42, 123, 456, 789, 999, 1337, 2021, 555, 777, 888])
def test_cliff_constraints_multiple_seeds(self, seed):
    # 测试代码
```

## 测试覆盖率

如果安装了pytest-cov插件，可以生成测试覆盖率报告：

```bash
# 安装覆盖率插件
poetry add --group dev pytest-cov

# 生成HTML覆盖率报告
poetry run pytest --cov=src --cov-report=html

# 查看报告
open htmlcov/index.html
```

## 测试最佳实践

### 1. 命名约定
- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 2. 测试结构
```python
class TestSomething:
    def test_positive_case(self):
        # 测试正常情况
        pass
    
    def test_edge_case(self):
        # 测试边界情况
        pass
    
    def test_error_case(self):
        # 测试错误情况
        pass
```

### 3. 断言使用
```python
# 好的断言
assert result == expected, f"期望 {expected}，实际 {result}"

# 检查异常
with pytest.raises(ValueError):
    function_that_should_raise()
```

### 4. 测试数据
- 使用固定的随机种子确保测试可重现
- 对于地图生成，选择已知会产生特定结果的种子

## 持续集成

这些测试可以集成到CI/CD流水线中：

```yaml
# GitHub Actions 示例
- name: Run tests
  run: |
    poetry install
    poetry run pytest
```

## 故障排除

### 常见问题
1. **导入错误**: 确保在测试文件中正确设置了Python路径
2. **配置文件未找到**: 确保测试运行时工作目录正确
3. **随机性问题**: 使用固定种子确保测试可重现

### 调试测试
```bash
# 在失败时进入调试器
poetry run pytest --pdb

# 显示本地变量
poetry run pytest -l

# 不捕获输出（显示print语句）
poetry run pytest -s
```
