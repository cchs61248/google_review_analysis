"""
Vercel / Serverless 入口（輕量版）
完整分析請在 Railway 等環境部署 app.py，並設定 SERPAPI_API_KEY、OPENAI_API_KEY。
評論來源已改為 SerpApi，無需瀏覽器。
"""
from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "message": "前端運行中",
            "note": "完整 API 請部署 app.py；需 SERPAPI_API_KEY（SerpApi）與 OPENAI_API_KEY。",
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():
    return (
        jsonify(
            {
                "success": False,
                "error": "此為靜態／輕量部署。請使用 Railway 等執行 app.py 以取得完整分析。",
            }
        ),
        501,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
