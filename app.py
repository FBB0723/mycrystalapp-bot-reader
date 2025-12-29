import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import datetime

# ==========================================
# 設定頁面資訊
# ==========================================
st.set_page_config(page_title="水晶靈感抽籤", page_icon="💎")

# 自訂 CSS 讓介面更有質感
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #f0f2f6;
        color: #333;
        border-radius: 10px;
        height: 3em;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 連結 Google Sheets (快取機制避免重複讀取)
# ==========================================
@st.cache_resource
def init_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # 從 Streamlit Secrets 讀取憑證
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    return client

def get_data():
    client = init_connection()
    # 這裡填入您的試算表名稱，或者用 URL
    sheet = client.open("Crystal_DB").sheet1 
    return sheet

# ==========================================
# 核心邏輯 (與之前相同，但適配 Web)
# ==========================================
# (這裡省略了重複的資料庫定義，請將之前的 CRYSTAL_DB 和 HYAKUNIN_ISSHU 貼在下方)
# --- 為了版面整潔，請您把 CRYSTAL_DB 和 HYAKUNIN_ISSHU 完整複製過來放在這裡 ---

# 範例佔位符 (請替換成您的完整資料庫)
CRYSTAL_DB = { "白水晶": {"color": "white", "keywords": ["淨化"]}, "紫水晶": {"color": "purple", "keywords": ["智慧"]} }
HYAKUNIN_ISSHU = ["秋收稻岸宿，過夜搭茅屋。"] 

# 用戶星盤
USER_PROFILE = {
    "sun": "巨蟹座", "moon": "雙子座", "rising": "處女座",
    "venus": "巨蟹座", "mars": "天秤座", "mercury": "巨蟹座"
}

def get_daily_focus():
    weekday = datetime.datetime.today().weekday()
    focus_map = {
        0: ("月亮 (雙子)", USER_PROFILE["moon"], ["blue", "white", "all"]),
        1: ("火星 (天秤)", USER_PROFILE["mars"], ["red", "pink", "brown"]),
        2: ("水星 (巨蟹)", USER_PROFILE["mercury"], ["blue", "gray"]),
        3: ("木星 (幸運日)", USER_PROFILE["sun"], ["yellow", "purple", "orange"]),
        4: ("金星 (巨蟹)", USER_PROFILE["venus"], ["pink", "green", "white"]),
        5: ("土星 (處女)", USER_PROFILE["rising"], ["black", "brown", "earth"]),
        6: ("太陽 (巨蟹)", USER_PROFILE["sun"], ["gold", "white", "red"]),
    }
    return focus_map.get(weekday, ("宇宙", "全星座", ["all"]))

# ==========================================
# APP 介面
# ==========================================
st.title("💎 今日水晶靈感")
st.caption("連結 Google Sheets 資料庫 V6.0")

# 1. 讀取資料
try:
    sheet = get_data()
    # 取得所有紀錄 (List of Dicts)
    all_records = sheet.get_all_records()
    
    # 篩選 active 且今日未戴過的 (這裡邏輯可自訂，目前先全抓)
    active_pool = [d for d in all_records if d.get('status') == 'active']
    
    st.info(f"📚 目前庫存：{len(active_pool)} 條水晶 | 雲端連線成功")

    if st.button("🔮 開始今日抽籤", type="primary"):
        with st.spinner('正在感應星象與能量...'):
            
            # --- 抽籤邏輯 ---
            focus_planet, focus_sign, lucky_colors = get_daily_focus()
            
            # 簡單篩選範例 (您可以把之前的複雜邏輯搬過來)
            candidates = [c for c in active_pool] # 預設全選
            
            # 隨機選 2-3 條
            daily_count = random.choice([2, 3])
            selected = random.sample(candidates, min(len(candidates), daily_count))
            
            # --- 顯示結果 ---
            st.divider()
            st.subheader(f"🌟 今日焦點：{focus_planet}")
            st.write(f"幸運色：{', '.join(lucky_colors)}")
            
            cols = st.columns(len(selected))
            for idx, c in enumerate(selected):
                with cols[idx]:
                    role = "👑 主角" if idx == 0 else "⚔️ 護法"
                    st.success(f"{role}")
                    st.markdown(f"### {c['name']}")
                    st.text(f"#{c['id']} | {c['style']}")
                    st.caption(f"材質：{c['main_crystal']}")
            
            # --- 籤詩 ---
            st.divider()
            fortune = random.choice(HYAKUNIN_ISSHU)
            st.markdown(f"#### 📜 {fortune}")

            # --- 寫入紀錄 (進階功能) ---
            # 這裡可以加入更新 Google Sheets 'last_worn' 的程式碼
            # 為了避免誤觸，通常會多做一個「確認配戴」按鈕才寫入
            
except Exception as e:
    st.error("連線發生錯誤，請檢查 Secrets 設定。")
    st.error(e)
