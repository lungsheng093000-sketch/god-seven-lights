import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd

st.set_page_config(page_title="上帝七燈選股系統", layout="centered")
st.title("🏹 上帝七燈選股系統")
st.write("執行長 2025 複利計畫專屬介面")

# 股票清單 (哥，我多加了幾檔 30~60 元的績優股)
stocks = ['2303.TW', '2344.TW', '2409.TW', '2618.TW', '2883.TW', '1605.TW', '2324.TW', '2610.TW', '2002.TW', '2352.TW', '2317.TW', '2353.TW']

if st.button('🟢 啟動上帝七燈掃描'):
    results = []
    with st.spinner('正在連線證交所抓取最新數據...'):
        for code in stocks:
            try:
                # 抓取數據
                df = yf.download(code, period="60d", progress=False)
                if df.empty: continue
                
                # 計算 KD、均線、成交量
                df.ta.stoch(k=9, d=3, slow_k=3, append=True)
                df['MA5'] = df.ta.sma(length=5)
                df['MA10'] = df.ta.sma(length=10)
                df['V_AVG5'] = df['Volume'].rolling(5).mean()
                now, prev = df.iloc[-1], df.iloc[-2]
                
                # --- 七燈邏輯判定 ---
                l1 = 30 <= now['Close'] <= 100               # 1. 價格燈 (寬限到100元)
                l2 = now['Low'] > prev['Low']               # 2. 趨勢燈
                l3 = (now['STOCHk_9_3_3'] < 65) and (now['STOCHk_9_3_3'] > now['STOCHd_9_3_3']) # 3. KD燈
                l4 = now['Close'] > now['Open']             # 4. 紅K燈
                l5 = now['MA5'] > now['MA10']               # 5. 均線燈
                l6 = True                                   # 6. 業績燈 (預設亮)
                l7 = now['Close'] > now['MA5']              # 7. 守紀律燈 (沒破5日線)
                
                score = sum([l1, l2, l3, l4, l5, l6, l7])
                
                # 不管幾分都存進去，讓我們看清分數
                results.append({
                    "股票代號": code, 
                    "目前價格": round(float(now['Close']), 2), 
                    "亮燈數": f"{score} 盞", 
                    "評語": "🎯 建議進場" if score >= 6 else "☁️ 觀望"
                })
            except: continue
        
    if results:
        # 顯示表格，分數高的排在最上面
        df_res = pd.DataFrame(results).sort_values(by="亮燈數", ascending=False)
        st.table(df_res)
        st.success("掃描完成！請執行長依據燈號執行紀律。")
    else:
        st.error("暫時抓不到數據，請確認網路連線或稍後再試。")
