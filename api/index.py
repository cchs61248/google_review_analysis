"""
Vercel API 入口
由於 Vercel 無伺服器環境限制，此版本僅提供前端界面
實際爬蟲功能需要部署到支援 Playwright 的平台（如 Railway、Render、自架伺服器等）
"""
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'message': 'Google Maps 評論分析器前端運行中',
        'note': '完整功能需要本地運行或部署到支援 Playwright 的平台'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析端點（Vercel 版本）"""
    return jsonify({
        'success': False,
        'error': 'Vercel 環境不支援瀏覽器自動化。請參考 README 在本地運行或部署到 Railway/Render 等平台。'
    }), 501

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
