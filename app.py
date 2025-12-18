      
import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import pytz
from datetime import datetime

# 1. 強制設定台灣時區
tw_tz = pytz.timezone('Asia/Taipei')
now_tw = datetime.now(tw_tz)

st.set_page_config(page_title="上帝七燈選股系統", layout="centered")
st.title("🏹 上帝七燈選股系統")
st.write(f"執行長 2025 複利計畫 | 台灣時間: {now_tw.strftime('%Y-%m-%d %H:%M')}")

# 2. 執行長口袋名單 (30~100元績優標的)
stocks = [
    '2303.TW', '2344.TW', '2409.TW', '2618.TW', '2883.TW', 
    '1605.TW', '2324.TW', '2610.TW', '2002.TW', '2352.TW', 
    '2317.TW', '2353.TW', '2888.TW', '2448.TW'
]

if st.button('🟢 啟動上帝七燈全自動掃描'):
    results = []
    with st.spinner('連線全球數據庫中，請稍候...'):
        for code in stocks:
            try:
                # 強化抓取：抓取半年份數據確保指標穩定
                df = yf.download(code, period="6mo", progress=False, auto_adjust=True)
                
                if df.empty or len(df) < 20:
                    continue
                
                # 計算 KD 指標
                df.ta.stoch(k=9, d=3, slow_k=3, append=True)
                # 計算均線
                df['MA5'] = df.ta.sma(length=5)
                df['MA10'] = df.ta.sma(length=10)
                # 計算5日均量
                df['V_AVG5'] = df['Volume'].rolling(5).mean()
                
                # 抓取最後兩筆數據做比對
                now = df.iloc[-1]
                prev = df.iloc[-2]
                
                # --- 上帝七燈核心邏輯 (哥的靈魂) ---
                l1 = 30 <= float(now['Close']) <= 100               # 價格燈
                l2 = float(now['Low']) > float(prev['Low'])       # 趨勢燈 (底底高)
                
                # KD燈: K < 65 且 K > D (低位黃金交叉)
                k_val = float(now['STOCHk_9_3_3'])
                d_val = float(now['STOCHd_9_3_3'])
                l3 = (k_val < 65) and (k_val > d_val)
                
                # 紅K帶量燈: 收紅且量大於5均量
                l4 = (float(now['Close']) > float(now['Open'])) and (float(now['Volume']) > float(now['V_AVG5']))
                
                l5 = float(now['MA5']) > float(now['MA10'])       # 均線燈 (5MA>10MA)
                l6 = True                                         # 業績燈 (預設亮)
                l7 = float(now['Close']) > float(now['MA5'])      # 保險絲燈 (沒破5MA)
                
                score = sum([l1, l2, l3, l4, l5, l6, l7])
                
                results.append({
                    "股票代號": code,
                    "收盤價": round(float(now['Close']), 2),
                    "亮燈數": f"{score} 盞",
                    "燈號建議": "🎯 建議進場" if score >= 6 else "☁️ 觀望"
                })
            except:
                continue
        
    if results:
        # 按燈號多寡排序
        df_res = pd.DataFrame(results).sort_values(by="亮燈數", ascending=False)
        st.table(df_res)
        st.success("✅ 掃描完成！請執行長依據紀律操作。")
    else:
        st.error("❌ 數據暫時中斷，這通常是半夜維護，請稍後再試或明天開盤再看。")
