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
# 🛠️ 1. 萬用自訂設定區
# ==========================================
ADMIN_PASSWORD = "betty"
DATA_FILE = "survey_results.csv"
MAX_PEOPLE_LIMIT = 10

# ✨ 新增：報名時間區間設定
TW_TZ = pytz.timezone("Asia/Taipei") if HAS_PYTZ else None
REG_OPEN_TIME = datetime.datetime(2026, 7, 19, 12, 40, tzinfo=TW_TZ)
REG_CLOSE_TIME = datetime.datetime(2026, 7, 19, 12, 50, tzinfo=TW_TZ)

SURVEY_QUESTIONS = [
    {"id": "q1", "title": "1.請問您的中文全名？", "type": "text", "placeholder": "例如：王小明", "required": True},
    {"id": "q2", "title": "2.您的工號？", "type": "text", "placeholder": "例如：01234", "required": True},
    {"id": "q3", "title": "3.是否攜帶眷屬？", "type": "radio", "options": ["無攜帶(FREE)", "攜帶1人(報名費100元)", "攜帶2人(報名費200元)"], "required": True},
    {"id": "q4", "title": "4.您的建議？", "type": "textarea", "placeholder": "有任何想說的，請寫在這裡唷！", "required": False}
]

EXPECTED_COLUMNS = ["時間戳記", "狀態"] + [q["title"] for q in SURVEY_QUESTIONS]

# ==========================================
# 📦 2. 初始化與自動錯誤修復機制 
# ==========================================
def initialize_or_fix_csv():
    if not os.path.exists(DATA_FILE):
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
        return
    try:
        df_temp = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
        if list(df_temp.columns) != EXPECTED_COLUMNS:
            df_temp.to_csv("survey_results_backup.csv", index=False, encoding="utf-8-sig")
            df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
            df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    except Exception:
        df_init = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df_init.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

initialize_or_fix_csv()

# ==========================================
# ✍️ 3. 前台問卷填寫介面
# ==========================================
st.set_page_config(page_title="自訂問卷系統", layout="wide")
st.title("📋 線上問卷調查")

# 取得當前時間
now = datetime.datetime.now(TW_TZ) if HAS_PYTZ else datetime.datetime.now()

# ✨ 新增：時間邏輯判斷
if now < REG_OPEN_TIME or now > REG_CLOSE_TIME:
    st.warning("⚠️ 目前非報名期間")
else:
    # 只有在報名期間才顯示問卷表單
    total_forms = 0
    total_people = 0
    if os.path.exists(DATA_FILE):
        try:
            df_count = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
            total_forms = len(df_count)
            q4_title = "3.是否攜帶眷屬？" # 修正對應題目欄位名稱
            if q4_title in df_count.columns and "狀態" in df_count.columns:
                df_confirmed = df_count[df_count["狀態"] == "正取"]
                for val in df_confirmed[q4_title]:
                    if "攜帶2人" in str(val): total_people += 3
                    elif "攜帶1人" in str(val): total_people += 2
                    else: total_people += 1
        except:
            total_forms = 0
            total_people = 0

    is_full = total_people >= MAX_PEOPLE_LIMIT
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1: st.metric(label="🔥 目前累計填寫份數", value=f"{total_forms} 份")
    with col_metric2: st.metric(label="👨‍👩‍👧‍👦 目前正取總人數 (含眷屬)", value=f"{total_people} / {MAX_PEOPLE_LIMIT} 人")

    if is_full:
        st.error(f"🚨 報名已額滿，您目前登記為候補")
    else:
        st.success(f"🍏 目前尚有空位（剩餘名額：{MAX_PEOPLE_LIMIT - total_people} 人），歡迎踴躍報名！")

    st.write("請花費一分鐘填寫以下內容，謝謝您的參與！")
    st.write("---")

    user_responses = {}
    with st.form(key="survey_form", clear_on_submit=True):
        for q in SURVEY_QUESTIONS:
            if q["type"] == "text": user_responses[q["title"]] = st.text_input(q["title"], placeholder=q.get("placeholder", ""))
            elif q["type"] == "radio": user_responses[q["title"]] = st.radio(q["title"], options=q["options"], index=None)
            elif q["type"] == "textarea": user_responses[q["title"]] = st.text_area(q["title"], placeholder=q.get("placeholder", ""))
        submit_button = st.form_submit_button(label="送出問卷", type="primary")

    if submit_button:
        has_error = False
        for q in SURVEY_QUESTIONS:
            val = user_responses[q["title"]]
            if q["required"] and (val is None or (isinstance(val, str) and not val.strip())):
                st.warning(f"⚠️ 請填寫/選擇「{q['title']}」")
                has_error = True
                break
        if not has_error:
            current_status = "候補" if is_full else "正取"
            row_data = {"時間戳記": now.strftime("%Y-%m-%d %H:%M:%S"), "狀態": current_status}
            for q in SURVEY_QUESTIONS:
                val = user_responses[q["title"]]
                row_data[q["title"]] = val.strip() if isinstance(val, str) else val
            new_data = pd.DataFrame([row_data])
            new_data.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")
            if current_status == "候補": st.info("👋 問卷提交成功！系統已將您登記為【候補】。")
            else: st.success("🎉 問卷提交成功！您已成功取得【正取】名額。")
            st.rerun()

# ==========================================
# 🔐 4. 安全密碼後台管理區
# ==========================================
st.write("---")
with st.expander("🛠️ 進入管理後台 (需管理員權限)", expanded=False):
    password = st.text_input("請輸入管理員密碼：", type="password", placeholder="請輸入密碼...")
    if password == ADMIN_PASSWORD:
        st.success("🔓 密碼正確！")
        # (後台管理程式碼維持不變...)