#!/usr/bin/env python3
"""
应用配置加载器 - 简化版
"""

import argparse
import json
import os
from typing import Dict, Any, List, Optional, Tuple


class AppConfig:
    def __init__(self, config_path: str = None, args: argparse.Namespace = None):
        if config_path is None:
            # 获取项目根目录的config文件夹路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "config.json")
        self.config_path = config_path
        self.config = self._load_config()
        self.args = args or argparse.Namespace()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 未找到，使用默认配置")
            return {"ui": {"enable_gui": True}}
        except json.JSONDecodeError as e:
            print(f"警告: 配置文件格式错误: {e}，使用默认配置")
            return {"ui": {"enable_gui": True}}

    def is_gui_enabled(self) -> bool:
        """是否启用GUI"""
        # 命令行参数优先于配置文件
        if hasattr(self.args, "headless") and self.args.headless:
            return False
        if hasattr(self.args, "no_gui") and self.args.no_gui:
            return False
        return self.config.get("ui", {}).get("enable_gui", True)

    # 硬编码的默认配置
    def should_auto_detect_environment(self) -> bool:
        return True

    def should_fallback_to_headless(self) -> bool:
        return True

    def should_show_user_choice(self) -> bool:
        return False

    def get_default_map_size(self) -> tuple:
        # 检查命令行参数中的size设置
        if hasattr(self.args, "size") and self.args.size:
            try:
                width, height = map(int, self.args.size.split("x"))
                return (width, height)
            except (ValueError, AttributeError):
                print(f"警告: 无效的尺寸格式 '{self.args.size}', 使用默认尺寸")
        return (12, 10)

    def get_headless_batch_seeds(self) -> list:
        # 检查命令行参数
        if hasattr(self.args, "seed") and self.args.seed is not None:
            return [self.args.seed]
        if hasattr(self.args, "batch") and self.args.batch is not None:
            # 生成指定数量的随机种子
            import random

            return [random.randint(1, 999999) for _ in range(self.args.batch)]
        return [42, 123, 456]

    def get_default_display(self) -> str:
        return ":0"

    def should_auto_set_display(self) -> bool:
        return True

    def is_verbose_output(self) -> bool:
        # 检查quiet参数
        if hasattr(self.args, "quiet") and self.args.quiet:
            return False
        # 检查verbose参数
        if hasattr(self.args, "verbose") and self.args.verbose:
            return True
        return True

    def should_auto_export_headless(self) -> bool:
        return True

    def get_output_directory(self) -> str:
        """获取输出目录"""
        if hasattr(self.args, "output") and self.args.output:
            return self.args.output
        return "."
    
    def get_phase(self) -> Optional[int]:
        """获取地形生成阶段"""
        if hasattr(self.args, "phase") and self.args.phase is not None:
            return self.args.phase
        return None

    @staticmethod
    def create_argument_parser() -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description="暗黑2风格地图生成工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例用法:
  %(prog)s                              # GUI模式 (默认)
  %(prog)s --headless                   # 无GUI模式，生成默认地图
  %(prog)s --headless --seed 42         # 指定种子生成单个地图
  %(prog)s --headless --batch 5         # 批量生成5个随机地图
  %(prog)s --headless --size 16x12      # 指定地图尺寸
  %(prog)s --headless --quiet           # 安静模式运行
  %(prog)s --headless --output ./maps   # 指定输出目录
            """,
        )

        # GUI控制
        gui_group = parser.add_mutually_exclusive_group()
        gui_group.add_argument(
            "--headless", "--no-gui", action="store_true", help="无GUI模式运行 (批量生成)"
        )

        # 地图生成参数
        parser.add_argument("--seed", type=int, help="指定地图生成种子 (整数)")

        parser.add_argument("--batch", type=int, metavar="N", help="批量生成N个地图 (仅无GUI模式)")

        parser.add_argument("--size", metavar="WxH", help="地图尺寸，格式为 宽x高 (例如: 16x12)")

        parser.add_argument("--phase", type=int, metavar="N", help="指定地形生成阶段 (1-3)")

        # 输出控制
        parser.add_argument("--output", "-o", metavar="DIR", help="输出目录路径")

        # 显示控制
        verbose_group = parser.add_mutually_exclusive_group()
        verbose_group.add_argument(
            "--verbose", "-v", action="store_true", help="详细输出模式"
        )

        verbose_group.add_argument(
            "--quiet", "-q", action="store_true", help="安静模式 (最少输出)"
        )

        return parser
