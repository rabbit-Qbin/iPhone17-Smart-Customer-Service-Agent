# 同时启动 main.py (API服务) 和 webUI.py (Gradio界面)
import subprocess
import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    # 启动 main.py (FastAPI 后端)
    main_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "main.py")],
        cwd=current_dir
    )
    
    # 启动 webUI.py (Gradio 前端)
    webui_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, "webUI.py")],
        cwd=current_dir
    )
    
    print("✅ 服务已启动:")
    print("   - API 服务: http://localhost:8012")
    print("   - Web 界面: http://127.0.0.1:7861")
    print("\n按 Ctrl+C 停止所有服务...")
    
    try:
        main_process.wait()
        webui_process.wait()
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        main_process.terminate()
        webui_process.terminate()
        print("✅ 服务已停止")
