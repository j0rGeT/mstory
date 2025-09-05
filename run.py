#!/usr/bin/env python3
"""
简化的启动脚本，用于启动小说故事创作系统
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    
    # 确保在正确的目录中
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 正在启动小说故事创作系统...")
    print("📖 系统将在浏览器中打开")
    print("🔧 请在侧边栏配置DeepSeek API Key")
    print("=" * 50)
    
    try:
        # 启动Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 系统已关闭")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")

if __name__ == "__main__":
    main()