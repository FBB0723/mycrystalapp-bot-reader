import streamlit as st
import pandas as pd
import random
import datetime

# ==========================================
# ⚠️ 設定區：請確認網址正確
# ==========================================
sheet_url = "https://docs.google.com/spreadsheets/d/1-C-j0p2jfB63ty6hnYi9A6vXsQdC-CanRi3lLrVSuNA/export?format=csv"

# ==========================================
# 頁面設定 (增加 CSS 隱藏表格索引)
# ==========================================
st.set_page_config(page_title="今日抽抽籤", page_icon="💎")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #f0f2f6;
        color: #333;
        border-radius: 10px;
        height: 3em;
        border: 1px solid #dcdcdc;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
    }
    h3 {
        color: #2c3e50;
        font-size: 1.3rem;
        margin-bottom: 0px;
    }
    .role-tag {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .palette-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-top: 5px;
        color: white;
    }
    .id-tag {
        font-size: 0.8rem;
        color: #888;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. 視覺色盤定義
# ==========================================
PALETTE_MAP = {
    "A": {"name": "莫蘭迪色系", "color": "#a89f91", "desc": "溫柔・灰調・歲月靜好"},
    "B": {"name": "冰川海洋系", "color": "#89c2d9", "desc": "透亮・淨化・百搭首選"},
    "C": {"name": "大地森林系", "color": "#5e503f", "desc": "深邃・自然・穩重能量"},
    "D": {"name": "暗夜星空系", "color": "#22333b", "desc": "神秘・強烈・個性防護"},
    "E": {"name": "璀璨富貴系", "color": "#e09f3e", "desc": "閃耀・吸睛・強大氣場"},
    "None": {"name": "未分類", "color": "#adb5bd", "desc": "自由搭配"}
}

# ==========================================
# 2. 完整水晶資料庫 (The Master Brain)
# ==========================================
CRYSTAL_DB = {
    # --- 1. 水晶家族 (Quartz Family) ---
    "白水晶": {"color": "white", "zodiac": ["全星座"], "keywords": ["淨化", "專注", "水晶之王", "阿賽斯特萊"]},
    "阿賽斯特萊": {"color": "white", "zodiac": ["全星座"], "keywords": ["高頻", "覺醒", "淨化"]},
    "粉晶": {"color": "pink", "zodiac": ["金牛座", "天秤座", "巨蟹座"], "keywords": ["桃花", "人緣", "舒緩", "馬粉"]},
    "紫水晶": {"color": "purple", "zodiac": ["水瓶座", "雙魚座", "射手座"], "keywords": ["智慧", "貴人", "安神", "紫玉晶"]},
    "紫黃晶": {"color": "purple", "zodiac": ["雙子座", "雙魚座"], "keywords": ["調和", "招財", "智慧"]},
    "黃水晶": {"color": "yellow", "zodiac": ["雙子座", "獅子座"], "keywords": ["偏財", "自信", "腸胃", "檸檬黃"]},
    "茶晶": {"color": "brown", "zodiac": ["摩羯座", "天蠍座"], "keywords": ["穩重", "排濁氣", "安眠"]},
    "髮晶": {"color": "gold", "zodiac": ["獅子座", "摩羯座"], "keywords": ["氣場", "權威", "財運"]},
    "鈦晶": {"color": "gold", "zodiac": ["獅子座", "處女座"], "keywords": ["正財", "霸氣", "決斷力"]},
    "銅髮晶": {"color": "red", "zodiac": ["天蠍座", "牡羊座"], "keywords": ["行動力", "女性健康", "勇氣"]},
    "黑髮晶": {"color": "black", "zodiac": ["摩羯座", "天蠍座"], "keywords": ["領袖", "防小人", "排除負能"]},
    "幽靈水晶": {"color": "green", "zodiac": ["金牛座", "摩羯座"], "keywords": ["事業", "招財", "健康", "綠幽靈"]},
    "彩幽靈": {"color": "all", "zodiac": ["全星座"], "keywords": ["全方位", "快樂", "願望"]},
    "兔毛水晶": {"color": "white", "zodiac": ["全星座"], "keywords": ["柔和", "能量", "護身"]},
    "膠花水晶": {"color": "red", "zodiac": ["全星座"], "keywords": ["桃花", "貴人", "開運", "錦鯉膠花"]},
    "超七": {"color": "all", "zodiac": ["全星座"], "keywords": ["全能", "放大能量", "七脈輪", "極光23"]},
    "極光23": {"color": "purple", "zodiac": ["全星座"], "keywords": ["靈性", "古老能量", "修復"]},

    # --- 2. 瑪瑙與玉髓 (Agate & Chalcedony) ---
    "瑪瑙": {"color": "red", "zodiac": ["雙子座", "處女座"], "keywords": ["平衡", "保護", "安穩"]},
    "鹽源瑪瑙": {"color": "all", "zodiac": ["全星座"], "keywords": ["多彩", "療癒", "保平安"]},
    "櫻花瑪瑙": {"color": "pink", "zodiac": ["全星座"], "keywords": ["溫柔", "綻放", "純淨"]},
    "阿拉善": {"color": "earth", "zodiac": ["摩羯座"], "keywords": ["大地", "避邪", "質樸"]},
    "玉髓": {"color": "blue", "zodiac": ["巨蟹座", "雙子座"], "keywords": ["避邪", "化煞", "平安"]},
    "藍玉髓": {"color": "blue", "zodiac": ["雙子座"], "keywords": ["溝通", "喉輪", "平靜"]},

    # --- 3. 長石家族 (Feldspar Family) ---
    "月光石": {"color": "blue", "zodiac": ["巨蟹座", "天蠍座", "雙魚座"], "keywords": ["戀人", "直覺", "柔和", "灰月光"]},
    "太陽石": {"color": "orange", "zodiac": ["獅子座", "天秤座"], "keywords": ["正向", "驅散憂鬱", "貴人"]},
    "阿魯沙": {"color": "green", "zodiac": ["獅子座"], "keywords": ["療癒", "陽光", "財運"]},
    "拉長石": {"color": "gray", "zodiac": ["射手座", "摩羯座", "水瓶座"], "keywords": ["靈魂伴侶", "耐力", "消除疲勞"]},
    "天河石": {"color": "blue", "zodiac": ["處女座", "水瓶座"], "keywords": ["幸運", "希望", "貴人"]},

    # --- 4. 藍色系礦石 (Blue Stones) ---
    "海藍寶": {"color": "blue", "zodiac": ["雙魚座", "雙子座"], "keywords": ["溝通", "勇氣", "旅行平安"]},
    "藍晶石": {"color": "blue", "zodiac": ["金牛座", "天秤座"], "keywords": ["協調", "冥想", "突破"]},
    "青金石": {"color": "blue", "zodiac": ["射手座", "水瓶座"], "keywords": ["洞察力", "眉心輪", "平靜"]},
    "藍磷灰": {"color": "blue", "zodiac": ["雙子座"], "keywords": ["和平", "自我表達", "控制食慾"]},
    "方納石": {"color": "blue", "zodiac": ["射手座"], "keywords": ["專注", "理智", "學業"]},
    "坦桑石": {"color": "blue", "zodiac": ["射手座", "摩羯座"], "keywords": ["靈性", "轉化", "社交"]},
    "堇青石": {"color": "blue", "zodiac": ["射手座", "天秤座"], "keywords": ["指引", "減肥", "理性"]},

    # --- 5. 玉石與翡翠 (Jade & Jadeite) ---
    "翡翠": {"color": "green", "zodiac": ["全星座"], "keywords": ["避邪", "擋災", "健康", "墨翠"]},
    "和田玉": {"color": "white", "zodiac": ["全星座"], "keywords": ["養人", "溫潤", "君子"]},
    "岫玉": {"color": "green", "zodiac": ["全星座"], "keywords": ["調和", "女性之石", "美容"]},
    "佘太翠": {"color": "green", "zodiac": ["全星座"], "keywords": ["平靜", "安神", "古樸"]},
    "東陵玉": {"color": "green", "zodiac": ["牡羊座", "金牛座"], "keywords": ["機會", "快樂", "幸運"]},

    # --- 6. 曜石與虎眼 (Obsidian & Chatoyant) ---
    "黑曜石": {"color": "black", "zodiac": ["摩羯座", "射手座"], "keywords": ["避邪", "防小人", "排除負能"]},
    "金曜石": {"color": "black", "zodiac": ["摩羯座"], "keywords": ["招財", "避邪", "行動力"]},
    "虎眼石": {"color": "yellow", "zodiac": ["摩羯座", "獅子座"], "keywords": ["勇氣", "自信", "事業"]},
    "彼得石": {"color": "blue", "zodiac": ["獅子座"], "keywords": ["暴風雨", "王者", "突破"]},
    "金運石": {"color": "black", "zodiac": ["摩羯座"], "keywords": ["極致招財", "賭運", "避邪"]},

    # --- 7. 其他常見寶石 (Other Gemstones) ---
    "碧璽": {"color": "all", "zodiac": ["全星座"], "keywords": ["旺夫", "全能", "暢通氣血"]},
    "石榴石": {"color": "red", "zodiac": ["摩羯座", "水瓶座", "蠍子座"], "keywords": ["氣血", "女性之石", "魅力"]},
    "螢石": {"color": "green", "zodiac": ["雙魚座", "水瓶座"], "keywords": ["天才之石", "專注", "情緒穩定"]},
    "紫鋰輝": {"color": "pink", "zodiac": ["全星座"], "keywords": ["無私的愛", "消除壓力", "暢通"]},
    "紫雲母": {"color": "purple", "zodiac": ["天秤座"], "keywords": ["人際", "鬆弛感", "美貌"]},
    "薔薇石": {"color": "pink", "zodiac": ["金牛座"], "keywords": ["修補關係", "自信", "愛"]},
    "摩根石": {"color": "pink", "zodiac": ["雙魚座"], "keywords": ["人緣", "愛情", "溫和"]},
    "透石膏": {"color": "white", "zodiac": ["全星座"], "keywords": ["淨化", "平靜", "天使之石"]},
    "火焰石": {"color": "red", "zodiac": ["牡羊座"], "keywords": ["勇氣", "熱情", "探索"]},

    # --- 8. 有機寶石與木質 (Organic & Wood) ---
    "檀木": {"color": "brown", "zodiac": ["全星座"], "keywords": ["安神", "避邪", "禪意", "綠檀", "黑檀"]},
    "沉香": {"color": "brown", "zodiac": ["全星座"], "keywords": ["靜心", "通關", "養氣"]},
    "崖柏": {"color": "brown", "zodiac": ["全星座"], "keywords": ["去百毒", "定魂", "香氣"]},
    "菩提": {"color": "white", "zodiac": ["全星座"], "keywords": ["智慧", "覺悟", "修身", "白菩提"]},
    "珊瑚玉": {"color": "yellow", "zodiac": ["全星座"], "keywords": ["富貴", "生命力", "化石"]},
    "珍珠": {"color": "white", "zodiac": ["巨蟹座", "雙魚座"], "keywords": ["純潔", "健康", "圓滿", "白貝母"]},
    "琥珀": {"color": "yellow", "zodiac": ["獅子座", "巨蟹座"], "keywords": ["安神", "定驚", "長壽"]},

    # --- 9. 特殊與宗教材質 ---
    "龍宮舍利": {"color": "white", "zodiac": ["全星座"], "keywords": ["最強護身", "正氣", "因果", "財寶龍宮"]},
    "硃砂": {"color": "red", "zodiac": ["全星座"], "keywords": ["極陽", "避邪", "鎮靜"]},
    "太赫茲": {"color": "gray", "zodiac": ["全星座"], "keywords": ["健康", "磁場", "波頻"]},

    # --- 10. 設計款多寶 ---
    "多寶": {"color": "all", "zodiac": ["全星座"], "keywords": ["平衡", "多元", "繽紛"]},
}

# ==========================================
# 3. 核心邏輯
# ==========================================
def get_crystal_info(crystal_name):
    if not isinstance(crystal_name, str): return {}
    if crystal_name in CRYSTAL_DB: return CRYSTAL_DB[crystal_name]
    for key in CRYSTAL_DB:
        if key in crystal_name: return CRYSTAL_DB[key]
        for k in CRYSTAL_DB[key].get("keywords", []):
            if k in crystal_name: return CRYSTAL_DB[key]
    return {"keywords": ["獨特能量"]}

def get_daily_focus():
    weekday = datetime.datetime.today().weekday()
    focus_map = {
        0: "月亮日 (週一)", 1: "火星日 (週二)", 2: "水星日 (週三)",
        3: "木星日 (週四)", 4: "金星日 (週五)", 5: "土星日 (週六)", 6: "太陽日 (週日)"
    }
    return focus_map.get(weekday, "宇宙能量日")

def get_visual_partners(leader, pool, count):
    leader_p = str(leader.get('Palette', 'None')).strip().upper()
    selected = []
    
    # 視覺相容邏輯
    compatible_map = {
        "A": ["A", "B"],      
        "B": ["A", "B", "C", "D", "E"], 
        "C": ["C", "B", "E"], 
        "D": ["D", "B", "E"], 
        "E": ["B", "D"],      
        "None": ["A", "B", "C", "D", "E"]
    }
    
    target_palettes = compatible_map.get(leader_p, ["B"])
    candidates = [c for c in pool if str(c.get('Palette', 'None')).strip().upper() in target_palettes]
    
    if len(candidates) < count:
        candidates = pool
        
    if len(candidates) > 0:
        partners = random.sample(candidates, min(len(candidates), count))
        selected.extend(partners)
        
    return selected

# ==========================================
# 主程式
# ==========================================
st.title("💎 今天的夥伴 (Visual Ver.)")

try:
    df = pd.read_csv(sheet_url)
    df = df.astype(str)
    all_records = df.to_dict('records')
    active_pool = [d for d in all_records if d.get('status') == '服役中']
    
    st.success(f"✅ 連線成功！共 {len(active_pool)} 條水晶準備就緒")

    if st.button("🎨 開啟視覺系抽籤", type="primary"):
        daily_focus = get_daily_focus()
        
        if len(active_pool) > 0:
            # 1. 主角
            leader = random.choice(active_pool)
            leader_palette = str(leader.get('Palette', 'None')).strip().upper()
            
            # 2. 配角
            remaining_pool = [c for c in active_pool if c['id'] != leader['id']]
            partners = get_visual_partners(leader, remaining_pool, random.choice([1, 2]))
            
            final_team = [leader] + partners
            
            # 3. 顯示結果
            st.divider()
            st.subheader(f"🌟 {daily_focus} | 風格：{PALETTE_MAP.get(leader_palette, {}).get('name', '混搭')}")
            
            cols = st.columns(len(final_team))
            for idx, c in enumerate(final_team):
                with cols[idx]:
                    role = "👑 主角" if idx == 0 else "✨ 配角"
                    p_code = str(c.get('Palette', 'None')).strip().upper()
                    p_info = PALETTE_MAP.get(p_code, PALETTE_MAP["None"])
                    info = get_crystal_info(c['main_crystal'])
                    
                    # 顯示角色標籤
                    st.markdown(f"<div class='role-tag'>{role}</div>", unsafe_allow_html=True)
                    
                    # 顯示名稱
                    st.markdown(f"### {c['name']}")
                    
                    # ⚠️ 這裡將 ID 加回來了，顯示在樣式旁邊
                    st.markdown(f"<span class='id-tag'>#{c['id']}</span> | {c['style']}", unsafe_allow_html=True)
                    
                    # 色系標籤
                    st.markdown(f"""
                        <div class='palette-tag' style='background-color: {p_info['color']};'>
                            {p_info['name']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 功效
                    st.caption(f"能量：{'、'.join(info.get('keywords', []))}")
                    
            # 移除了籤詩區塊
            
        else:
            st.warning("⚠️ 庫存是空的，請檢查 status。")

except Exception as e:
    st.error("發生錯誤，請檢查網址或欄位設定。")
    st.code(f"{e}")
