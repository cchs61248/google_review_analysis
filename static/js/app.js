// ==================== 主要應用邏輯 ====================

// 取得 DOM 元素
const mapsUrlInput = document.getElementById('maps-url');
const reviewLimitInput = document.getElementById('review-limit');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingSection = document.getElementById('loading');
const errorSection = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const resultsSection = document.getElementById('results');
const totalReviewsElement = document.getElementById('total-reviews');
const analysisContent = document.getElementById('analysis-content');
const reviewsContent = document.getElementById('reviews-content');

// 分頁按鈕
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

// ==================== 事件監聽 ====================

// 分析按鈕點擊事件
analyzeBtn.addEventListener('click', handleAnalyze);

// Enter 鍵觸發分析
mapsUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleAnalyze();
    }
});

// 分頁切換
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;
        switchTab(targetTab);
    });
});

// ==================== 主要功能 ====================

/**
 * 處理分析請求
 */
async function handleAnalyze() {
    const url = mapsUrlInput.value.trim();
    const limit = parseInt(reviewLimitInput.value);

    // 驗證輸入
    if (!url) {
        showError('請輸入 Google Maps 網址');
        return;
    }

    if (!limit || limit < 1 || limit > 200) {
        showError('評論數量必須介於 1 到 200 之間');
        return;
    }

    // 重置狀態
    hideError();
    hideResults();
    showLoading();
    analyzeBtn.disabled = true;

    try {
        // 發送 API 請求
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                limit: limit
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || '請求失敗');
        }

        // 顯示結果
        displayResults(data.data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || '發生未知錯誤，請稍後再試');
    } finally {
        hideLoading();
        analyzeBtn.disabled = false;
    }
}

/**
 * 顯示分析結果
 */
function displayResults(data) {
    const { reviews, analysis, total_reviews } = data;

    // 更新統計資訊
    totalReviewsElement.textContent = total_reviews;

    // 渲染 AI 分析報告（將 Markdown 轉換為 HTML）
    analysisContent.innerHTML = markdownToHtml(analysis);

    // 渲染原始評論列表
    renderReviews(reviews);

    // 顯示結果區並切換到分析報告分頁
    showResults();
    switchTab('analysis');
}

/**
 * 渲染評論列表
 */
function renderReviews(reviews) {
    reviewsContent.innerHTML = '';

    reviews.forEach(review => {
        const reviewElement = createReviewElement(review);
        reviewsContent.appendChild(reviewElement);
    });
}

/**
 * 建立單個評論元素
 */
function createReviewElement(review) {
    const div = document.createElement('div');
    div.className = 'review-item';

    // 評論標題（評分）
    const header = document.createElement('div');
    header.className = 'review-header';
    
    const rating = document.createElement('div');
    rating.className = 'review-rating';
    rating.innerHTML = `<i class="fas fa-star"></i> ${review.rating || 'N/A'}`;
    
    header.appendChild(rating);
    div.appendChild(header);

    // 評論內容
    if (review.text) {
        const text = document.createElement('div');
        text.className = 'review-text';
        text.textContent = review.text;
        div.appendChild(text);
    }

    // 推薦餐點
    if (review.suggested_dishes && review.suggested_dishes.length > 0) {
        const dishesContainer = document.createElement('div');
        dishesContainer.className = 'review-dishes';
        
        // 處理陣列或字串格式
        const dishes = Array.isArray(review.suggested_dishes) 
            ? review.suggested_dishes 
            : review.suggested_dishes.split(/[,、]/).map(d => d.trim()).filter(d => d);
        
        dishes.forEach(dish => {
            const dishTag = document.createElement('span');
            dishTag.className = 'dish-tag';
            dishTag.textContent = dish;
            dishesContainer.appendChild(dishTag);
        });
        
        div.appendChild(dishesContainer);
    }

    return div;
}

/**
 * 簡易 Markdown 轉 HTML
 */
function markdownToHtml(markdown) {
    if (!markdown) return '';

    let html = markdown;

    // 標題
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // 粗體
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

    // 列表
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // 段落
    html = html.split('\n\n').map(para => {
        if (para.startsWith('<h') || para.startsWith('<ul') || para.startsWith('<li')) {
            return para;
        }
        return `<p>${para}</p>`;
    }).join('\n');

    // 換行
    html = html.replace(/\n/g, '<br>');

    return html;
}

/**
 * 切換分頁
 */
function switchTab(tabName) {
    tabBtns.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    tabPanes.forEach(pane => {
        if (pane.id === `${tabName}-tab`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });
}

// ==================== UI 狀態管理 ====================

function showLoading() {
    loadingSection.classList.remove('hidden');
}

function hideLoading() {
    loadingSection.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
}

function hideError() {
    errorSection.classList.add('hidden');
}

function showResults() {
    resultsSection.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
}

// ==================== 初始化 ====================

// 頁面載入時檢查 API 健康狀態
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('API Status:', data.message);
    } catch (error) {
        console.error('API 連接失敗:', error);
    }
});
