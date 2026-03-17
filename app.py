"""
Flask Web API 後端
提供 Google Maps 評論分析的 RESTful API
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# 確保可以 import src 模組
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import resolve_short_url, setup_logger
from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer

# 設定日誌
setup_logger()
logger = logging.getLogger(__name__)

# 建立 Flask 應用
app = Flask(__name__)
CORS(app)  # 允許跨域請求

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    分析 Google Maps 評論

    Request Body:
    {
        "url": "Google Maps URL",
        "limit": 30,  # optional
        "visible": false  # optional
    }

    Response:
    {
        "success": true,
        "data": {
            "reviews": [...],
            "analysis": "..."
        }
    }
    """
    try:
        data = request.get_json()

        # 驗證參數
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': '請提供 Google Maps 網址'
            }), 400

        url = data['url']
        limit = int(data.get('limit', 30))
        visible = data.get('visible', False)

        logger.info(f"收到分析請求: url={url}, limit={limit}")

        # 1. 解析網址
        try:
            full_url = resolve_short_url(url)
            logger.info(f"完整網址: {full_url}")
        except Exception as e:
            logger.error(f"網址解析失敗: {e}")
            return jsonify({
                'success': False,
                'error': f'網址解析失敗: {str(e)}'
            }), 400

        # 2. 爬取評論
        try:
            # Railway 環境中強制使用無頭模式
            is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
            headless_mode = True if is_railway else not visible

            if is_railway:
                logger.info("檢測到 Railway 環境，使用無頭模式")

            scraper = GoogleMapsScraper(
                headless=headless_mode,
                user_data_dir=None
            )
            reviews = scraper.scrape_reviews(full_url, max_reviews=limit)

            if not reviews:
                return jsonify({
                    'success': False,
                    'error': '未找到評論，請確認網址是否正確'
                }), 404

            logger.info(f"成功爬取 {len(reviews)} 則評論")

        except Exception as e:
            logger.exception(f"爬取評論失敗: {e}")
            return jsonify({
                'success': False,
                'error': f'爬取評論失敗: {str(e)}'
            }), 500

        # 3. AI 分析
        try:
            analyzer = ReviewAnalyzer()
            analysis = analyzer.analyze(reviews)
            logger.info("AI 分析完成")

        except ValueError as e:
            logger.error(f"AI 分析失敗: {e}")
            return jsonify({
                'success': False,
                'error': '請設定 OPENAI_API_KEY 環境變數'
            }), 500
        except Exception as e:
            logger.exception(f"AI 分析失敗: {e}")
            return jsonify({
                'success': False,
                'error': f'AI 分析失敗: {str(e)}'
            }), 500

        # 4. 回傳結果
        return jsonify({
            'success': True,
            'data': {
                'reviews': reviews,
                'analysis': analysis,
                'total_reviews': len(reviews)
            }
        })

    except Exception as e:
        logger.exception(f"未預期的錯誤: {e}")
        return jsonify({
            'success': False,
            'error': f'伺服器錯誤: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'message': 'Google Maps 評論分析器 API 運行中'
    })

@app.route('/api/debug_info', methods=['GET'])
@app.route('/api/debug', methods=['GET'])
def debug_info():
    """除錯資訊端點（debug_info）"""
    import platform
    import subprocess

    debug_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'is_railway': os.environ.get('RAILWAY_ENVIRONMENT') is not None,
        'has_openai_key': bool(os.environ.get('OPENAI_API_KEY')),
        'port': os.environ.get('PORT', '5000'),
    }

    # 檢查 Playwright 是否安裝
    try:
        result = subprocess.run(
            ['playwright', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        debug_info['playwright_installed'] = True
        debug_info['playwright_version'] = result.stdout.strip()
    except Exception:
        debug_info['playwright_installed'] = False
        debug_info['playwright_version'] = None

    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
