"""
評論分析服務
"""
import logging
from typing import List, Dict, Optional
from openai import OpenAI
from ..config import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

logger = logging.getLogger(__name__)


class ReviewAnalyzer:
    """評論分析器（使用 LLM）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        use_stream: bool = True,
    ):
        """
        初始化分析器

        Args:
            api_key: OpenAI API Key（預設從環境變數讀取）
            base_url: API Base URL（預設從環境變數讀取）
            model: 使用的模型名稱（預設從環境變數讀取）
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError(
                "未設定 API Key。請在 .env 檔案中設定 OPENAI_API_KEY"
            )

        self.base_url = base_url or OPENAI_BASE_URL
        self.model = model or LLM_MODEL
        self.use_stream = use_stream

        # OpenAI Python v1+ 的串流是透過每次請求的 stream 參數來控制
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f"已初始化 ReviewAnalyzer，使用模型: {self.model}")

    def analyze(self, reviews: List[Dict]) -> str:
        """
        分析評論列表

        Args:
            reviews: 評論資料列表，每項需包含 'text' 欄位

        Returns:
            分析報告（Markdown 格式）
        """
        if not reviews:
            return "沒有評論可供分析。"

        # 組合評論文字
        reviews_text = self._format_reviews(reviews)
        if not reviews_text.strip():
            return "評論內容為空，無法分析。"

        # 建立提示詞
        prompt = self._build_prompt(reviews_text)

        # 呼叫 LLM API
        return self._call_llm_api(prompt)

    def analyze_formatted_text(self, formatted_text: str) -> str:
        """
        分析已經格式化的評論文字

        Args:
            formatted_text: 格式化的評論文字（包含評分、推薦餐點等完整資訊）

        Returns:
            分析報告（Markdown 格式）
        """
        if not formatted_text or not formatted_text.strip():
            return "評論內容為空，無法分析。"

        # 建立提示詞（直接使用格式化文字）
        prompt = self._build_prompt_from_formatted_text(formatted_text)

        # 呼叫 LLM API
        return self._call_llm_api(prompt)

    def _call_llm_api(self, prompt: str) -> str:
        """
        呼叫 LLM API 進行分析

        Args:
            prompt: 分析提示詞

        Returns:
            分析結果
        """
        try:
            if self.use_stream:
                logger.info("開始呼叫 LLM API（串流模式）進行分析")
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位專業的美食評論分析師，擅長整理與歸納 Google Maps 餐廳評論。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    stream=True,
                )

                chunks: List[str] = []
                for chunk in stream:
                    try:
                        choice = chunk.choices[0]
                        delta = getattr(choice, "delta", None)
                        content = getattr(delta, "content", None) if delta else None
                        if content:
                            chunks.append(content)
                    except Exception:
                        # 若某些 chunk 結構不符合預期，直接略過
                        continue

                result = "".join(chunks)
            else:
                logger.info("開始呼叫 LLM API（非串流模式）進行分析")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一位專業的美食評論分析師，擅長整理與歸納 Google Maps 餐廳評論。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                )
                result = response.choices[0].message.content
            logger.info("LLM 分析完成")
            return result

        except Exception as e:
            logger.exception(f"分析過程中發生錯誤: {e}")
            return f"分析過程中發生錯誤: {str(e)}"

    def _format_reviews(self, reviews: List[Dict]) -> str:
        """
        格式化評論列表

        Args:
            reviews: 評論資料列表

        Returns:
            格式化後的評論文字
        """
        parts = []
        for i, review in enumerate(reviews, 1):
            text = review.get("text", "")
            if not text:
                continue

            # 組合評論文字
            line = f"{review.get('number', i)}. {text}"

            # 如果有建議的餐點，一併附上
            if review.get("suggested_dishes"):
                line += f"\n   建議的餐點：{review['suggested_dishes']}"

            parts.append(line)

        return "\n".join(parts)

    def _build_prompt(self, reviews_text: str) -> str:
        """
        建立分析提示詞

        Args:
            reviews_text: 格式化後的評論文字

        Returns:
            完整的提示詞
        """
        return f"""
你是一位專業的美食評論分析師。以下是針對某家餐廳的 Google Maps 評論清單。
請綜合分析這些評論，並輸出以下資訊：

1. **推薦餐點**：列出顧客普遍好評的食物，並簡述原因。
2. **不推薦餐點**：列出顧客抱怨或認為普通的食物，並簡述原因。
3. **整體評價**：總結這家餐廳的優缺點、適合的客群或用餐情境。

評論列表：
{reviews_text}

請直接輸出分析結果，不需要開場白，並使用 Markdown 格式。
"""

    def _build_prompt_from_formatted_text(self, formatted_text: str) -> str:
        """
        從格式化文字建立分析提示詞

        Args:
            formatted_text: 完整的格式化評論文字（包含評分星星、推薦餐點等）

        Returns:
            完整的提示詞
        """
        return f"""
你是一位專業的美食評論分析師。以下是針對某家餐廳的 Google Maps 評論清單。
評論已經過格式化，包含評分（以星星表示）、評論內容、以及推薦的餐點。

請綜合分析這些評論，並輸出以下資訊：

1. **推薦餐點**：列出顧客普遍好評的食物，並簡述原因（參考評分和推薦餐點欄位）。
2. **不推薦餐點**：列出顧客抱怨或認為普通的食物，並簡述原因。
3. **整體評價**：總結這家餐廳的優缺點、適合的客群或用餐情境（參考評分分布和評論內容）。

格式化的評論列表：
{formatted_text}

請直接輸出分析結果，不需要開場白，並使用 Markdown 格式。
"""
