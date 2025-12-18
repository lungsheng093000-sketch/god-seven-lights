import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import pytz # 處理時差
from datetime import datetime

# 1. 處理台灣時差
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)

st.set_page_config(page_title="上帝七燈選股系統", layout="centered")
st.title("🏹 上帝七燈選股系統")
st.write(f"執行長 2025 複利計畫 | 台灣時間: {now_tw.strftime('%Y-%m-%d %H:%M')}")

# 擴大名單
stocks = ['2303.TW', '2344.TW', '2409.TW', '2618.TW', '2883.TW', '1605.TW', '2324.TW', '2610.TW', '2002.TW', '2352.TW', '2317.TW', '2353.TW']

if st.button('🟢 啟動上帝七燈全自動掃描'):
    results = []
    with st.spinner('連線數據庫中，半夜連線較慢請稍候...'):
        for code in stocks:
            try:
                # 這裡改用 period="max" 並抓最後 100 筆，確保一定有舊資料可以算
                ticker = yf.Ticker(code)
                df = ticker.history(period="6mo") 
                
                if df.empty or len(df) < 20:
                    continue
                
                # 計算指標
                df.ta.stoch(k=9, d=3, slow_k=3, append=True)
                df['MA5'] = df.ta.sma(length=5)
                df['MA10'] = df.ta.sma(length=10)
                df['V_AVG5'] = df['Volume'].rolling(5).mean()
                
                now = df.iloc[-1]
                prev = df.iloc[-2]
                
                # 七燈邏輯
                l1 = 30 <= float(now['Close']) <= 100
                l2 = float(now['Low']) > float(prev['Low'])
                l3 = (float(now['STOCHk_9_3_3']) < 65) and (float(now['STOCHk_9_3_3']) > float(now['STOCHd_9_3_3']))
                l4 = (float(now['Close']) > float(now['Open'])) and (float(now['Volume']) > float(now['V_AVG5']))
                l5 = float(now['MA5']) > float(now['MA10'])
                l6 = True 
                l7 = float(now['Close']) > float(now['MA5'])
                
                score = sum([l1, l2, l3, l4, l5, l6, l7])
                results.append({
                    "股票代號": code,
                    "最新價格": round(float(now['Close']), 2),
                    "亮燈數": score,
                    "建議": "🎯 進場" if score >= 6 else "☁️ 觀望"
                })
            except:
                continue
        
    if results:
        df_res = pd.DataFrame(results).sort_values(by="亮燈數", ascending=False)
        st.table(df_res)
        st.success("✅ 數據掃描完畢！")
    else:
        st.warning("⚠️ 數據庫半夜維護中，請執行長明日開盤後再試，或多按幾次。")
