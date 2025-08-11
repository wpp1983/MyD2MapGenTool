#!/usr/bin/env python3
"""
应用配置加载器 - 简化版
"""

import json
import os
from typing import Dict, Any

class AppConfig:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 获取项目根目录的config文件夹路径
            current_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(current_dir)
            config_path = os.path.join(project_root, "config", "config.json")
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {self.config_path} 未找到，使用默认配置")
            return {"ui": {"enable_gui": True}}
        except json.JSONDecodeError as e:
            print(f"警告: 配置文件格式错误: {e}，使用默认配置")
            return {"ui": {"enable_gui": True}}
    
    def is_gui_enabled(self) -> bool:
        """是否启用GUI"""
        return self.config.get('ui', {}).get('enable_gui', True)
    
    # 硬编码的默认配置
    def should_auto_detect_environment(self) -> bool:
        return True
    
    def should_fallback_to_headless(self) -> bool:
        return True
    
    def should_show_user_choice(self) -> bool:
        return False
    
    def get_default_map_size(self) -> tuple:
        return (12, 10)
    
    def get_headless_batch_seeds(self) -> list:
        return [42, 123, 456]
    
    def get_default_display(self) -> str:
        return ":0"
    
    def should_auto_set_display(self) -> bool:
        return True
    
    def is_verbose_output(self) -> bool:
        return True
    
    def should_auto_export_headless(self) -> bool:
        return True
