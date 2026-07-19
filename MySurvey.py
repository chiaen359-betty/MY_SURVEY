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
ADMIN_PASSWORD = "betty"  # 後台密碼
DATA_FILE = "survey_results.csv"  # 存檔檔名
MAX_PEOPLE_LIMIT = 10  # 🎯 報名人數上限設定 (達到此人數即截止)

# 在這裡設定你的問卷問題：
SURVEY_QUESTIONS = [
    {
        "id": "name",
        "title": "👤 請填入你是誰？",
        "type": "text",
        "placeholder": "請輸入您的名字或暱稱...",
        "required": True
    },
    {
        "id": "q1",
        "title": "1. 你喜歡什麼顏色？🌈",
        "type": "radio",
        "options": ["紅", "橙", "黃", "綠", "藍", "靛", "紫"],
        "required": True
    },
    {
        "id": "q2",
        "title": "2. 你喜歡什麼寵物？🐶🐱",
        "type": "text",
        "placeholder": "例如：貓咪、水豚、金吉拉...",
        "required": True
    },
    {
        "id": "q3",
        "title": "3. 明天要一起吃藏壽司嗎？🍣",
        "type": "radio",
        "options": ["Yes", "No"],
        "required": True
    },
    {
        "id": "q4",
        "title": "👨‍👩‍👧‍👦 4. 是否攜帶家眷？",
        "type": "radio",
        "options": ["自己一人", "帶 1 人", "帶 2 人"],
        "required": True
    },
    {
        "id": "q5",
        "title": "5. 其他意見？💬",
        "type": "textarea",
        "placeholder": "有任何想說的，或者是想扭到什麼扭蛋，都可以寫在這裡唷！",
        "required": False
    }
]

# 根據你的設定，自動產生預期的 CSV 欄位名稱
EXPECTED_COLUMNS = ["時間戳記"] + [q["title"] for q in SURVEY_QUESTIONS]

# ==========================================
# 📦 2. 初始化與自動錯誤修復機制 
# ==========================================
def initialize_or_fix_csv():
    # 情況 1：如果檔案不存在，直接建立
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return
    
    # 情況 2：如果檔案存在，嘗試讀取並檢查欄位
    try:
        df_temp = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        # 如果現存 CSV 的欄位數量或名稱與預期的不一樣，就進行修復
        if list(df_temp.columns) != EXPECTED_COLUMNS:
            # 為了避免壞掉，我們備份舊資料，並重新初始化乾淨的 CSV
            df_temp.to_csv("survey_results_backup.csv", index=False, encoding="utf-8-sig")
            df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    except Exception:
        # 如果連讀取都直接壞掉（例如 ParserError），代表檔案損毀，直接重置
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

# 執行初始化或修復
initialize_or_fix_csv()


# ==========================================
# ✍️ 3. 前台問卷填寫介面
# ==========================================
st.set_page_config(page_title="自訂問卷系統", layout="wide")
st.title("📋 線上問卷調查")

# --- 計算目前填寫表單人數與總出席人數 ---
total_forms = 0
total_people = 0

if os.path.exists(DATA_FILE):
    try:
        df_count = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        total_forms = len(df_count)
        
        # 定義家眷選項對應的人數：自己一人->1人，帶1人->2人，帶2人->3人
        q4_title = "👨‍👩‍👧‍👦 4. 是否攜帶家眷？"
        if q4_title in df_count.columns:
            for val in df_count[q4_title]:
                if val == "帶 1 人":
                    total_people += 2
                elif val == "帶 2 人":
                    total_people += 3
                else:
                    total_people += 1  # 自己一人或未預期狀況預設 1 人
        else:
            total_people = total_forms
    except Exception:
        total_forms = 0
        total_people = 0

# 用漂亮的卡片元件顯示人數，並加上進度與上限標示
col_metric1, col_metric2 = st.columns(2)
with col_metric1:
    st.metric(label="🔥 目前累計填寫份數", value=f"{total_forms} 份")
with col_metric2:
    st.metric(label="👨‍👩‍👧‍👦 目前累計總人數 (含眷屬)", value=f"{total_people} / {MAX_PEOPLE_LIMIT} 人")

st.write("請花費一分鐘填寫以下內容，謝謝您的參與！")
st.write("---")

# 📢 新增：人數判定截止機制
if total_people >= MAX_PEOPLE_LIMIT:
    st.error("❌ 報名已額滿")
    st.info(f"目前累計總人數已達 {total_people} 人（上限 {MAX_PEOPLE_LIMIT} 人），非常感謝大家的踴躍參與！後續若有釋出名額將再行通知。")
else:
    # 狀態：未額滿 -> 正常顯示問卷表單
    user_responses = {}

    with st.form(key="survey_form", clear_on_submit=True):
        for q in SURVEY_QUESTIONS:
            if q["type"] == "select":
                user_responses[q["title"]] = st.selectbox(
                    q["title"], 
                    options=q["options"], 
                    index=None, 
                    placeholder="請選擇一個選項..."
                )
            elif q["type"] == "text":
                user_responses[q["title"]] = st.text_input(
                    q["title"], 
                    placeholder=q.get("placeholder", "")
                )
            elif q["type"] == "radio":
                user_responses[q["title"]] = st.radio(
                    q["title"], 
                    options=q["options"], 
                    index=None
                )
            elif q["type"] == "textarea":
                user_responses[q["title"]] = st.text_area(
                    q["title"], 
                    placeholder=q.get("placeholder", "")
                )
                
        submit_button = st.form_submit_button(label="送出問卷", type="primary")

    if submit_button:
        # 檢查必填項目
        has_error = False
        for q in SURVEY_QUESTIONS:
            val = user_responses[q["title"]]
            if q["required"]:
                if val is None or (isinstance(val, str) and not val.strip()):
                    st.warning(f"⚠️ 請填寫/選擇「{q['title']}」")
                    has_error = True
                    break
                    
        if not has_error:
            # 取得台灣時間 (台北時區)
            if HAS_PYTZ:
                tw_tz = pytz.timezone("Asia/Taipei")
                tw_now = datetime.datetime.now(tw_tz)
            else:
                # 防錯替代方案：手動計算 UTC+8 時間
                utc_now = datetime.datetime.now(datetime.timezone.utc)
                tw_now = utc_now + datetime.timedelta(hours=8)
                
            row_data = {"時間戳記": tw_now.strftime("%Y-%m-%d %H:%M:%S")}
            
            for q in SURVEY_QUESTIONS:
                val = user_responses[q["title"]]
                row_data[q["title"]] = val.strip() if isinstance(val, str) else val
                
            # 寫入 CSV
            new_data = pd.DataFrame([row_data])
            new_data.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
            st.success("🎉 問卷提交成功！感謝您的回答。")
            st.rerun()  # 提交成功後立即重新整理，讓上方的人數即時更新！


# ==========================================
# 🔐 4. 安全密碼後台管理區
# ==========================================
st.write("---")

with st.expander("🛠️ 進入管理後台 (需管理員權限)", expanded=False):
    password = st.text_input("請輸入管理員密碼：", type="password", placeholder="請輸入密碼...")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 密碼正確！已開啟管理權限。")
        st.write("---")
        
        # 讀取資料
        if os.path.exists(DATA_FILE):
            try:
                df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            except Exception as e:
                df = pd.DataFrame()
                st.error(f"讀取資料檔時發生錯誤，這通常是因為檔案格式損壞。錯誤訊息：{e}")
        else:
            df = pd.DataFrame()
            
        if df.empty or len(df) == 0:
            st.info("目前尚無問卷填寫紀錄。")
        else:
            st.subheader("📊 後台管理數據面板")
            
            # --- 功能 1：顯示每個人的選擇 ---
            st.write("### 📝 1. 原始問卷填寫明細")
            st.write(f"目前累計填寫份數：**{len(df)}** 份")
            st.dataframe(df, use_container_width=True)
            
            csv_data = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下載完整問卷結果 (CSV)",
                data=csv_data,
                file_name="survey_export.csv",
                mime="text/csv"
            )
            st.write("---")
            
            # --- 功能 2：選項類自動統計 ---
            st.write("### 📊 2. 選項類問題統計")
            stats_questions = [q for q in SURVEY_QUESTIONS if q["type"] in ["select", "radio"]]
            
            if len(stats_questions) > 0:
                cols = st.columns(2)
                for idx, q in enumerate(stats_questions):
                    col_target = cols[idx % 2]
                    title = q["title"]
                    
                    with col_target:
                        st.markdown(f"**📍 {title}**")
                        counts = df[title].value_counts()
                        percents = df[title].value_counts(normalize=True) * 100
                        
                        st.bar_chart(counts)
                        
                        for opt, val in counts.items():
                            pct = percents[opt]
                            st.caption(f"* **{opt}**：{val} 票 ({pct:.1f}%)")
            else:
                st.write("目前設定的問卷中，沒有選項類的題目可供統計。")
                
            st.write("---")
            
            # --- 功能 3：刪除全部結果 ---
            st.write("### 🚨 3. 危險區域")
            st.write("此動作將會清除所有已儲存的問卷回答，且**無法復原**。")
            
            confirm_delete = st.checkbox("我確定要刪除所有問卷填寫結果。")
            
            if confirm_delete:
                if st.button("🔥 永久刪除全部問卷數據", type="primary"):
                    df_empty = pd.DataFrame(columns=EXPECTED_COLUMNS)
                    df_empty.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
                    st.success("💥 所有數據已被清空！請重新整理網頁。")
                    st.rerun()  # 立即重新整理頁面
                    
    elif password != "":
        st.error("🔒 密碼錯誤，請重新輸入！")