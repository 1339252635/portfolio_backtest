#!/usr/bin/env python3
"""
后端服务启动脚本
"""
import os
import sys
import subprocess

def main():
    """启动Flask后端服务"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    # 检查虚拟环境
    venv_path = os.path.join(backend_dir, 'venv')
    if os.path.exists(venv_path):
        if os.name == 'nt':  # Windows
            python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Linux/Mac
            python_path = os.path.join(venv_path, 'bin', 'python')
    else:
        python_path = sys.executable
    
    # 启动服务
    os.chdir(backend_dir)
    subprocess.run([python_path, 'run.py'])

if __name__ == '__main__':
    main()
