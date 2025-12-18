import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from datetime import datetime

# 網頁配置
st.set_page_config(page_title="上帝七燈選股系統", layout="centered")
st.title("🏹 上帝七燈選股系統")
st.write(f"執行長 2025 複利計畫 | 當前時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# 擴大名單：包含 30~60 元左右的熱門績優股
stocks = [
    '2303.TW', '2344.TW', '2409.TW', '2618.TW', '2883.TW', 
    '1605.TW', '2324.TW', '2610.TW', '2002.TW', '2352.TW', 
    '2317.TW', '2353.TW', '2448.TW', '2313.TW', '2888.TW'
]

if st.button('🟢 啟動上帝七燈全自動掃描'):
    results = []
    with st.spinner('正在連線全球數據庫，請稍候...'):
        for code in stocks:
            try:
                # 強化抓取機制：增加 auto_adjust 並縮短時間範圍提高成功率
                df = yf.download(code, period="100d", interval="1d", progress=False, auto_adjust=True)
                
                if df.empty or len(df) < 30:
                    continue
                
                # 計算 KD (9, 3, 3)
                df.ta.stoch(high='High', low='Low', close='Close', k=9, d=3, slow_k=3, append=True)
                # 計算均線
                df['MA5'] = df.ta.sma(length=5)
                df['MA10'] = df.ta.sma(length=10)
                # 計算成交量均線
                df['V_AVG5'] = df['Volume'].rolling(5).mean()
                
                now = df.iloc[-1]
                prev = df.iloc[-2]
                
                # --- 上帝七燈邏輯 ---
                # 1. 價格燈 (30~100元)
                l1 = 30 <= float(now['Close']) <= 100
                # 2. 趨勢燈 (底底高)
                l2 = float(now['Low']) > float(prev['Low'])
                # 3. KD燈 (低位向上交叉，放寬至65以下)
                k_val = float(now['STOCHk_9_3_3'])
                d_val = float(now['STOCHd_9_3_3'])
                l3 = (k_val < 65) and (k_val > d_val)
                # 4. 紅K帶量燈 (收盤價>開盤價 且 量大於5日均量)
                l4 = (float(now['Close']) > float(now['Open'])) and (float(now['Volume']) > float(now['V_AVG5']))
                # 5. 均線燈 (5MA > 10MA)
                l5 = float(now['MA5']) > float(now['MA10'])
                # 6. 業績燈 (預設亮燈，未來可接入基本面數據)
                l6 = True 
                # 7. 保險絲燈 (收盤沒破5MA)
                l7 = float(now['Close']) > float(now['MA5'])
                
                score = sum([l1, l2, l3, l4, l5, l6, l7])
                
                results.append({
                    "股票代號": code,
                    "收盤價": round(float(now['Close']), 2),
                    "亮燈數": score,
                    "狀態": "🔥 準備進場" if score >= 6 else "☁️ 觀望"
                })
            except Exception as e:
                # 即使某一檔出錯，也不要卡死，繼續下一檔
                continue
        
    if results:
        # 視覺化呈現
        df_res = pd.DataFrame(results).sort_values(by="亮燈數", ascending=False)
        
        # 讓亮燈數顯示得更漂亮
        def color_score(val):
            color = 'red' if val >= 6 else 'black'
            return f'color: {color}; font-weight: bold'
        
        st.table(df_res)
        st.success("✅ 掃描完成！符合 6 燈以上者為目前最佳進場標的。")
    else:
        st.error("❌ 偵測到證交所數據庫連線異常，請稍後幾分鐘再按一次。")
