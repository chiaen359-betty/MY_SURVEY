import streamlit as st
import pandas as pd
import os
import datetime

# 嘗試引入時區套件，若環境未安裝則啟動自動修正機制
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False

# ==========================================
# 🛠️ 1. 萬用自訂設定區 (以後你只要改這裡就好)
# ==========================================
ADMIN_PASSWORD = "betty"  # 後台密碼[cite: 1]
DATA_FILE = "survey_results.csv"  # 存檔檔名[cite: 1]
CONFIG_FILE = "config.txt"  # ✨ 新增：存放時間設定的外部檔案
MAX_PEOPLE_LIMIT = 10     # ✨ 新增：報名人數上限設定[cite: 1]

# ⏱️ ✨ 外部時間設定讀寫函式
def load_config_times():
    """從 config.txt 讀取報名時間，若不存在或格式錯誤則給予預設值"""
    default_start = datetime.datetime(2026, 7, 19, 12, 40, 0)
    default_end = datetime.datetime(2026, 7, 19, 12, 50, 0)
    
    if not os.path.exists(CONFIG_FILE):
        return default_start, default_end
    
    try:
        config_data = {}
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    config_data[key] = val
        
        start_time = datetime.datetime.strptime(config_data.get("START_TIME"), "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(config_data.get("END_TIME"), "%Y-%m-%d %H:%M:%S")
        return start_time, end_time
    except Exception:
        return default_start, default_end

def save_config_times(start_time, end_time):
    """將新的報名時間寫入 config.txt"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(f"START_TIME={start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"END_TIME={end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

# 載入報名時間
START_TIME, END_TIME = load_config_times()

# 在這裡設定你的問卷問題：[cite: 1]
SURVEY_QUESTIONS = [
    {
        "id": "q1",
        "title": "1.請問您的中文全名？",
        "type": "text",
        "placeholder": "例如：王小明",
        "required": True
    },
    {
        "id": "q2",
        "title": "2.您的工號？",
        "type": "text",
        "placeholder": "例如：01234",
        "required": True
    },
    {
        "id": "q3",
        "title": "3.是否攜帶眷屬？",
        "type": "radio",
        "options": ["無攜帶(FREE)", "攜帶1人(報名費100元)", "攜帶2人(報名費200元)"],
        "required": True
    },
    {
        "id": "q4",
        "title": "4.您的建議？",
        "type": "textarea",
        "placeholder": "有任何想說的，請寫在這裡唷！",
        "required": False
    }
]

# ✨ 擴充預期欄位：加入「狀態」欄，用來在後台區分 正取/候補[cite: 1]
EXPECTED_COLUMNS = ["時間戳記", "狀態"] + [q["title"] for q in SURVEY_QUESTIONS][cite: 1]

# ==========================================
# 📦 2. 初始化與自動錯誤修復機制[cite: 1]
# ==========================================
def initialize_or_fix_csv():
    # 情況 1：如果檔案不存在，直接建立[cite: 1]
    if not os.path.exists(DATA_FILE):[cite: 1]
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)[cite: 1]
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")[cite: 1]
        return[cite: 1]
    
    # 情況 2：如果檔案存在，嘗試讀取並檢查欄位[cite: 1]
    try:[cite: 1]
        df_temp = pd.read_csv(DATA_FILE, encoding="utf-8-sig")[cite: 1]
        # 如果現存 CSV 的欄位數量或名稱與預期的不一樣，就進行修復[cite: 1]
        if list(df_temp.columns) != EXPECTED_COLUMNS:[cite: 1]
            # 為了避免壞掉，我們備份舊資料，並重新初始化乾淨的 CSV[cite: 1]
            df_temp.to_csv("survey_results_backup.csv", index=False, encoding="utf-8-sig")[cite: 1]
            df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)[cite: 1]
            df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")[cite: 1]
    except Exception:[cite: 1]
        # 如果連讀取都直接壞掉（例如 ParserError），代表檔案損毀，直接重置[cite: 1]
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)[cite: 1]
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")[cite: 1]

# 執行初始化或修復[cite: 1]
initialize_or_fix_csv()[cite: 1]


# ==========================================
# ✍️ 3. 前台問卷填寫介面[cite: 1]
# ==========================================
st.set_page_config(page_title="自訂問卷系統", layout="wide")[cite: 1]
st.title("📋 線上問卷調查")[cite: 1]

# ⏱️ ✨ 取得目前台灣時間 (台北時區) 並強制移除時區資訊以防比對出錯[cite: 1]
if HAS_PYTZ:[cite: 1]
    tw_tz = pytz.timezone("Asia/Taipei")[cite: 1]
    tw_now_raw = datetime.datetime.now(tw_tz)[cite: 1]
    tw_now = tw_now_raw.replace(tzinfo=None)[cite: 1]
else:[cite: 1]
    utc_now = datetime.datetime.now(datetime.timezone.utc)[cite: 1]
    tw_now_raw = utc_now + datetime.timedelta(hours=8)[cite: 1]
    tw_now = tw_now_raw.replace(tzinfo=None)[cite: 1]

# ⏱️ ✨ 檢查是否在報名時間內[cite: 1]
is_registration_open = START_TIME <= tw_now <= END_TIME[cite: 1]

if not is_registration_open:[cite: 1]
    # 🚫 ✨ 非報名期間顯示提示，且不渲染表單與人數統計[cite: 1]
    st.warning(f"目前非報名期間（開放時間：{START_TIME.strftime('%Y-%m-%d %H:%M')} 至 {END_TIME.strftime('%Y-%m-%d %H:%M')}）")
else:[cite: 1]
    # 🟢 ✨ 報名期間正常顯示問卷內容[cite: 1]
    # --- 計算目前填寫表單人數與總出席人數 ---[cite: 1]
    total_forms = 0[cite: 1]
    total_people = 0[cite: 1]

    if os.path.exists(DATA_FILE):[cite: 1]
        try:[cite: 1]
            df_count = pd.read_csv(DATA_FILE, encoding="utf-8-sig")[cite: 1]
            total_forms = len(df_count)[cite: 1]
            
            # ✨ 修改：僅統計資料庫內「狀態為正取」的總人數，避免候補人數干擾計數[cite: 1]
            q4_title = "👨‍👩‍👧‍👦 4. 是否攜帶家眷？" # 注意：此處需與 SURVEY_QUESTIONS 的標題對齊，若前台有調整請注意名稱
            # 這裡為了保險，先採用計算 row 數，或抓取問題3的欄位
            target_q = SURVEY_QUESTIONS[2]["title"]
            if target_q in df_count.columns and "狀態" in df_count.columns:
                df_confirmed = df_count[df_count["狀態"] == "正取"][cite: 1]
                for val in df_confirmed[target_q]:
                    if "攜帶1人" in str(val):
                        total_people += 2
                    elif "攜帶2人" in str(val):
                        total_people += 3
                    else:
                        total_people += 1  # 自己一人
            else:
                total_people = total_forms[cite: 1]
        except Exception:[cite: 1]
            total_forms = 0[cite: 1]
            total_people = 0[cite: 1]

    # ✨ 判斷目前是否已達上限[cite: 1]
    is_full = total_people >= MAX_PEOPLE_LIMIT[cite: 1]

    # 用漂亮的卡片元件顯示人數[cite: 1]
    col_metric1, col_metric2 = st.columns(2)[cite: 1]
    with col_metric1:[cite: 1]
        st.metric(label="🔥 目前累計填寫份數", value=f"{total_forms} 份")[cite: 1]
    with col_metric2:[cite: 1]
        st.metric(label="👨‍👩‍👧‍👦 目前正取總人數 (含眷屬)", value=f"{total_people} / {MAX_PEOPLE_LIMIT} 人")[cite: 1]

    # ✨ 新增：根據人數上限，即時在畫面上動態顯示對應提示[cite: 1]
    if is_full:[cite: 1]
        st.error(f"🚨 報名已額滿，您目前登記為候補")[cite: 1]
    else:[cite: 1]
        st.success(f"🍏 目前尚有空位（剩餘名額：{MAX_PEOPLE_LIMIT - total_people} 人），歡迎踴躍報名！")[cite: 1]

    st.write("請花費一分鐘填寫以下內容，謝謝您的參與！")[cite: 1]
    st.write("---")[cite: 1]

    # 用來暫存使用者回答的字典[cite: 1]
    user_responses = {}[cite: 1]

    with st.form(key="survey_form", clear_on_submit=True):[cite: 1]
        for q in SURVEY_QUESTIONS:[cite: 1]
            if q["type"] == "select":[cite: 1]
                user_responses[q["title"]] = st.selectbox([cite: 1]
                    q["title"],[cite: 1]
                    options=q["options"],[cite: 1]
                    index=None,[cite: 1]
                    placeholder="請選擇一個選項..."[cite: 1]
                )[cite: 1]
            elif q["type"] == "text":[cite: 1]
                user_responses[q["title"]] = st.text_input([cite: 1]
                    q["title"],[cite: 1]
                    placeholder=q.get("placeholder", "")[cite: 1]
                )[cite: 1]
            elif q["type"] == "radio":[cite: 1]
                user_responses[q["title"]] = st.radio([cite: 1]
                    q["title"],[cite: 1]
                    options=q["options"],[cite: 1]
                    index=None[cite: 1]
                )[cite: 1]
            elif q["type"] == "textarea":[cite: 1]
                user_responses[q["title"]] = st.text_area([cite: 1]
                    q["title"],[cite: 1]
                    placeholder=q.get("placeholder", "")[cite: 1]
                )[cite: 1]
                
        submit_button = st.form_submit_button(label="送出問卷", type="primary")[cite: 1]

    if submit_button:[cite: 1]
        # 檢查必填項目[cite: 1]
        has_error = False[cite: 1]
        for q in SURVEY_QUESTIONS:[cite: 1]
            val = user_responses[q["title"]][cite: 1]
            if q["required"]:[cite: 1]
                if val is None or (isinstance(val, str) and not val.strip()):[cite: 1]
                    st.warning(f"⚠️ 請填寫/選擇「{q['title']}」")[cite: 1]
                    has_error = True[cite: 1]
                    break[cite: 1]
                    
        if not has_error:[cite: 1]
            # ✨ 新增：依據送出當下是否額滿，給予正取或候補狀態[cite: 1]
            current_status = "候補" if is_full else "正取"[cite: 1]
            
            row_data = {
                "時間戳記": tw_now.strftime("%Y-%m-%d %H:%M:%S"),[cite: 1]
                "狀態": current_status[cite: 1]
            }
            
            for q in SURVEY_QUESTIONS:[cite: 1]
                val = user_responses[q["title"]][cite: 1]
                row_data[q["title"]] = val.strip() if isinstance(val, str) else val[cite: 1]
                
            # 寫入 CSV[cite: 1]
            new_data = pd.DataFrame([row_data])[cite: 1]
            new_data.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")[cite: 1]
            
            # ✨ 新增：送出成功後的彈出視窗提示[cite: 1]
            if current_status == "候補":[cite: 1]
                st.info("👋 問卷提交成功！因目前名額已滿，系統已將您登記為【候補】。")[cite: 1]
            else:[cite: 1]
                st.success("🎉 問卷提交 success！您已成功取得【正取】名額。")[cite: 1]
                
            st.rerun()  # 提交成功後立即重新整理[cite: 1]


# ==========================================
# 🔐 4. 安全密碼後台管理區[cite: 1]
# ==========================================
st.write("---")[cite: 1]

with st.expander("🛠️ 進入管理後台 (需管理員權限)", expanded=False):[cite: 1]
    password = st.text_input("請輸入管理員密碼：", type="password", placeholder="請輸入密碼...")[cite: 1]
    
    if password == ADMIN_PASSWORD:[cite: 1]
        st.success("🔓 密碼正確！已開啟管理權限。")[cite: 1]
        st.write("---")[cite: 1]
        
        # ⏱️ ✨ 新增功能：後台動態時間設定面板
        st.subheader("⚙️ 報名時間排程設定")
        st.write(f"目前設定的開放區間：`{START_TIME}` 至 `{END_TIME}`")
        
        col_start_date, col_start_time = st.columns(2)
        with col_start_date:
            new_start_date = st.date_input("開啟報名日期", value=START_TIME.date())
        with col_start_time:
            new_start_time = st.time_input("開啟報名時間", value=START_TIME.time())
            
        col_end_date, col_end_time = st.columns(2)
        with col_end_date:
            new_end_date = st.date_input("截止報名日期", value=END_TIME.date())
        with col_end_time:
            new_end_time = st.time_input("截止報名時間", value=END_TIME.time())
            
        if st.button("💾 儲存報名時間設定", type="primary"):
            updated_start = datetime.datetime.combine(new_start_date, new_start_time)
            updated_end = datetime.datetime.combine(new_end_date, new_end_time)
            
            if updated_start >= updated_end:
                st.error("❌ 錯誤：開啟時間不能大於或等於截止時間！")
            else:
                save_config_times(updated_start, updated_end)
                st.success("🎉 報名時間已成功更新並寫入設定檔！網頁即將重新整理...")
                st.rerun()
                
        st.write("---")
        
        # 讀取資料[cite: 1]
        if os.path.exists(DATA_FILE):[cite: 1]
            try:[cite: 1]
                df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")[cite: 1]
            except Exception as e:[cite: 1]
                df = pd.DataFrame()[cite: 1]
                st.error(f"讀取資料檔時發生錯誤，這通常是因為檔案格式損壞。錯誤訊息：{e}")[cite: 1]
        else:[cite: 1]
            df = pd.DataFrame()[cite: 1]
            
        if df.empty or len(df) == 0:[cite: 1]
            st.info("目前尚無問卷填寫紀錄。")[cite: 1]
        else:[cite: 1]
            st.subheader("📊 後台管理數據面板")[cite: 1]
            
            # --- 功能 1：顯示每個人的選擇 ---[cite: 1]
            st.write("### 📝 1. 原始問卷填寫明細")[cite: 1]
            st.write(f"目前累計填寫份數：**{len(df)}** 份")[cite: 1]
            st.dataframe(df, use_container_width=True)[cite: 1]
            
            csv_data = df.to_csv(index=False, encoding="utf-8-sig")[cite: 1]
            st.download_button([cite: 1]
                label="📥 下載完整問卷結果 (CSV)",[cite: 1]
                data=csv_data,[cite: 1]
                file_name="survey_export.csv",[cite: 1]
                mime="text/csv"[cite: 1]
            )[cite: 1]
            st.write("---")[cite: 1]
            
            # --- 功能 2：選項類自動統計 ---[cite: 1]
            st.write("### 📊 2. 選項類問題統計")[cite: 1]
            stats_questions = [q for q in SURVEY_QUESTIONS if q["type"] in ["select", "radio"]][cite: 1]
            
            if len(stats_questions) > 0:[cite: 1]
                cols = st.columns(2)[cite: 1]
                for idx, q in enumerate(stats_questions):[cite: 1]
                    col_target = cols[idx % 2][cite: 1]
                    title = q["title"][cite: 1]
                    
                    with col_target:[cite: 1]
                        st.markdown(f"**📍 {title}**")[cite: 1]
                        counts = df[title].value_counts()[cite: 1]
                        percents = df[title].value_counts(normalize=True) * 100[cite: 1]
                        
                        st.bar_chart(counts)[cite: 1]
                        
                        for opt, val in counts.items():[cite: 1]
                            pct = percents[opt][cite: 1]
                            st.caption(f"* **{opt}**：{val} 票 ({pct:.1f}%)")[cite: 1]
            else:[cite: 1]
                st.write("目前設定的問卷中，沒有選項類的題目可供統計。")[cite: 1]
                
            st.write("---")[cite: 1]
            
            # --- 功能 3：刪除全部結果 ---[cite: 1]
            st.write("### 🚨 3. 危險區域")[cite: 1]
            st.write("此動作將會清除所有已儲存的問卷回答，且**無法復原**。")[cite: 1]
            
            confirm_delete = st.checkbox("我確定要刪除所有問卷填寫結果。")[cite: 1]
            
            if confirm_delete:[cite: 1]
                if st.button("🔥 永久刪除全部問卷數據", type="primary"):[cite: 1]
                    df_empty = pd.DataFrame(columns=EXPECTED_COLUMNS)[cite: 1]
                    df_empty.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")[cite: 1]
                    st.success("💥 所有數據已被清空！請重新整理網頁。")[cite: 1]
                    st.rerun()  # 立即重新整理頁面[cite: 1]
                    
    elif password != "":[cite: 1]
        st.error("🔒 密碼錯誤，請重新輸入！")[cite: 1]