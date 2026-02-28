import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'data', 'portfolio.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据目录
    DATA_DIR = os.path.join(basedir, '..', 'data')
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        # 确保数据目录存在
        os.makedirs(Config.DATA_DIR, exist_ok=True)
