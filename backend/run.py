import os
from dotenv import load_dotenv
from app import app


if __name__ == "__main__":
    # 仅保留一种调试模式设置
    app.run(host='0.0.0.0', port=5000)