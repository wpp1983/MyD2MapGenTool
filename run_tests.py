#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试执行命令
"""

import subprocess
import sys
import os


def run_all_tests():
    """运行所有测试"""
    print("🧪 运行所有测试...")
    result = subprocess.run(["poetry", "run", "pytest"], cwd=os.getcwd())
    return result.returncode


def run_specific_test(test_file):
    """运行特定测试文件"""
    print(f"🧪 运行测试文件: {test_file}")
    result = subprocess.run(
        ["poetry", "run", "pytest", f"tests/{test_file}"], cwd=os.getcwd()
    )
    return result.returncode


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("🧪 运行测试并生成覆盖率报告...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "pytest",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term",
        ],
        cwd=os.getcwd(),
    )
    return result.returncode


def run_verbose():
    """运行详细模式测试"""
    print("🧪 运行详细模式测试...")
    result = subprocess.run(["poetry", "run", "pytest", "-v", "-s"], cwd=os.getcwd())
    return result.returncode


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python run_tests.py all           # 运行所有测试")
        print("  python run_tests.py <test_file>   # 运行特定测试文件")
        print("  python run_tests.py coverage      # 运行测试并生成覆盖率")
        print("  python run_tests.py verbose       # 详细模式")
        sys.exit(1)

    command = sys.argv[1]

    if command == "all":
        exit_code = run_all_tests()
    elif command == "coverage":
        exit_code = run_with_coverage()
    elif command == "verbose":
        exit_code = run_verbose()
    elif command.endswith(".py"):
        exit_code = run_specific_test(command)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
