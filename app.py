import streamlit as st
import time

# --- 초기 설정 ---
# st.session_state를 사용하여 코인 잔액과 상태를 저장
if 'coins' not in st.session_state:
    st.session_state.coins = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

st.title("📚 뽀모도로 & 코인 리워드 앱")
st.header(f"💰 현재 코인: {st.session_state.coins}원")

# --- 타이머 설정 ---
study_time = st.slider("공부 시간 설정 (분)", min_value=1, max_value=60, value=25)
st.write(f"설정된 공부 시간: **{study_time}분**")

# --- 타이머 시작 버튼 ---
if st.button("공부 시작!"):
    st.session_state.is_running = True
    
# --- 타이머 실행 로직 ---
if st.session_state.is_running:
    total_seconds = study_time * 60
    
    # 1초씩 카운트다운
    timer_placeholder = st.empty()
    
    for i in range(total_seconds, 0, -1):
        minutes, seconds = divmod(i, 60)
        timer_placeholder.markdown(f"## ⏳ 남은 시간: {minutes:02d}:{seconds:02d}")
        time.sleep(1)
    
    # --- 시간 종료 및 보상 지급 ---
    st.balloons() # 완료 시 축하 효과!
    st.success(f"🥳 {study_time}분 공부 완료! 1000 코인 지급!")
    
    st.session_state.coins += 1000
    st.session_state.is_running = False
    st.rerun() # 코인 업데이트를 위해 화면 새로고침 (Streamlit의 방식)
