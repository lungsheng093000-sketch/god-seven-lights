import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="上帝七燈選股系統", layout="centered")
st.title("🏹 上帝七燈選股系統")
st.write("執行長 2025 複利計畫專屬介面")

# 股票清單
stocks = ['2303.TW', '2344.TW', '2409.TW', '2618.TW', '2883.TW', '1605.TW', '2324.TW', '2610.TW', '2002.TW', '2352.TW']

if st.button('🟢 啟動上帝七燈掃描'):
    results = []
    with st.spinner('正在連線證交所抓取最新數據...'):
        for code in stocks:
            try:
                df = yf.download(code, period="60d", progress=False)
                if df.empty: continue
                df.ta.stoch(k=9, d=3, slow_k=3, append=True)
                df['MA5'] = df.ta.sma(length=5)
                df['MA10'] = df.ta.sma(length=10)
                df['V_AVG5'] = df['Volume'].rolling(5).mean()
                now, prev = df.iloc[-1], df.iloc[-2]
                
                # 七燈邏輯
                l1 = 30 <= now['Close'] <= 60
                l2 = now['Low'] > prev['Low']
                l3 = (now['STOCHk_9_3_3'] < 60) and (now['STOCHk_9_3_3'] > now['STOCHd_9_3_3'])
                l4 = (now['Close'] > now['Open']) and (now['Volume'] > now['V_AVG5'])
                l5 = now['MA5'] > now['MA10']
                l6 = True
                l7 = now['Close'] > now['MA5']
                
                score = sum([l1, l2, l3, l4, l5, l6, l7])
                results.append({"股票": code, "價格": round(float(now['Close']), 2), "亮燈數": f"{score} 盞", "評語": "🎯 建議進場" if score >= 6 else "☁️ 觀望"})
            except: continue
        
    if results:
        st.table(pd.DataFrame(results).sort_values(by="亮燈數", ascending=False))
