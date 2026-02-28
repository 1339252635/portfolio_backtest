import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Product, PriceData, BacktestScenario, ScenarioAllocation, BacktestResult, Holding

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Product': Product,
        'PriceData': PriceData,
        'BacktestScenario': BacktestScenario,
        'ScenarioAllocation': ScenarioAllocation,
        'BacktestResult': BacktestResult,
        'Holding': Holding
    }


@app.route('/')
def index():
    return {
        'message': 'Portfolio Backtest API',
        'version': '1.0.0',
        'endpoints': {
            'products': '/api/products',
            'backtest': '/api/backtest',
            'analysis': '/api/analysis'
        }
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
