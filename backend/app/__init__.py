from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# 先创建扩展实例（但暂不初始化）
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):
    try:
        app = Flask(__name__)
        app.config.from_object(config_class)

        # 初始化扩展
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        # 注册蓝图
        from app.routes.auth import auth_bp
        from app.routes.graph import graph_bp
        from app.routes.query import query_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(graph_bp, url_prefix='/api/graph')
        app.register_blueprint(query_bp, url_prefix='/api/query')

        # 必须在 app 上下文中导入模型
        with app.app_context():
            from app.models import User, Graph, QueryCache  # 显式导入模型
            
            # 创建数据库表（仅开发环境使用）
            db.create_all()

        return app
    except Exception as e:
        raise