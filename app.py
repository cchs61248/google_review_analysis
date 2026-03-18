"""
Flask Web API 後端
提供 Google Maps 評論分析的 RESTful API（SerpApi + LLM）
"""
import os
import sys
import logging
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import setup_logger
from src.core import GoogleMapsScraper
from src.services import ReviewAnalyzer

setup_logger()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Request: { "url": "...", "limit": 30, "force_refresh": false }
    """
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"success": False, "error": "請提供 Google Maps 網址"}), 400

        url = data["url"]
        limit = int(data.get("limit", 30))
        force_refresh = bool(data.get("force_refresh", False))
        logger.info(
            "收到分析請求: url=%s, limit=%s, force_refresh=%s",
            url[:80],
            limit,
            force_refresh,
        )

        try:
            scraper = GoogleMapsScraper()
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 500

        try:
            reviews = scraper.scrape_reviews(
                url,
                max_reviews=limit,
                force_refresh=force_refresh,
            )
        except Exception as e:
            logger.exception("取得評論失敗: %s", e)
            return jsonify({"success": False, "error": f"取得評論失敗: {e}"}), 500

        if not reviews:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "未找到評論，請確認網址或 SerpApi 設定",
                    }
                ),
                404,
            )

        try:
            analyzer = ReviewAnalyzer()
            analysis = analyzer.analyze(reviews)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 500
        except Exception as e:
            logger.exception("AI 分析失敗: %s", e)
            return jsonify({"success": False, "error": f"AI 分析失敗: {e}"}), 500

        return jsonify(
            {
                "success": True,
                "data": {
                    "reviews": reviews,
                    "analysis": analysis,
                    "total_reviews": len(reviews),
                },
            }
        )
    except Exception as e:
        logger.exception("未預期錯誤: %s", e)
        return jsonify({"success": False, "error": f"伺服器錯誤: {e}"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "message": "Google Maps 評論分析器 API 運行中",
        }
    )


@app.route("/api/debug_info", methods=["GET"])
@app.route("/api/debug", methods=["GET"])
def debug_info():
    import platform

    return jsonify(
        {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "is_railway": os.environ.get("RAILWAY_ENVIRONMENT") is not None,
            "has_openai_key": bool(os.environ.get("OPENAI_API_KEY")),
            "has_serpapi_key": bool(os.environ.get("SERPAPI_API_KEY")),
            "port": os.environ.get("PORT", "5000"),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
