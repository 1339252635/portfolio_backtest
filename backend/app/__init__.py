from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.routes.products import bp as products_bp
    from app.routes.backtest import bp as backtest_bp
    from app.routes.analysis import bp as analysis_bp
    
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(backtest_bp, url_prefix='/api/backtest')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
