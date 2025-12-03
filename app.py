import streamlit as st
import time

# --- 1. 초기 설정 및 상태 관리 ---

# 세션 상태 초기화: 앱을 새로 열 때 한 번만 실행됩니다.
if 'coins' not in st.session_state:
    st.session_state.coins = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'is_study' not in st.session_state:
    st.session_state.is_study = True # 현재 상태 (공부 중 / 휴식 중)
if 'theme' not in st.session_state:
    st.session_state.theme = 'default'
if 'owned_items' not in st.session_state:
    st.session_state.owned_items = set()

# 아이템 목록 (상점 데이터)
SHOP_ITEMS = {
    'dark_mode': {'name': '다크 모드', 'price': 5000, 'effect': '배경을 어둡게 바꿉니다.'},
    'retro_alarm': {'name': '레트로 알림', 'price': 3000, 'effect': '종료 알림 소리를 레트로 스타일로 바꿉니다.'}
}

# --- 2. 테마 적용 함수 ---

def apply_theme():
    """상점 아이템 구매에 따라 앱 테마를 적용합니다."""
    # 다크 모드 아이템을 소유하고 있다면 배경색을 변경하는 CSS를 적용합니다.
    if 'dark_mode' in st.session_state.owned_items:
        st.markdown(
            """
            <style>
            .main {
                background-color: #1E1E1E; /* 어두운 배경 */
                color: #FFFFFF; /* 밝은 글씨 */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    # 다른 테마 적용 로직은 여기에 추가할 수 있습니다.

apply_theme()


# --- 3. 타이머 로직 함수 ---

def run_timer(duration_minutes, is_study_session=True):
    """
    타이머를 실행하고 종료 시 코인을 지급합니다.
    """
    total_seconds = duration_minutes * 60
    
    # 타이머 표시를 위한 Placeholder
    timer_placeholder = st.empty()
    
    for i in range(total_seconds, 0, -1):
        minutes, seconds = divmod(i, 60)
        
        # 현재 상태를 나타내는 제목 표시
        status_text = "📚 공부 중" if is_study_session else "☕ 휴식 중"
        color = "red" if is_study_session else "blue"
        timer_placeholder.markdown(f"## <span style='color:{color};'>{status_text}</span> 남은 시간: {minutes:02d}:{seconds:02d}", unsafe_allow_html=True)
        
        time.sleep(1)
        
        # 중간에 중지 버튼이 눌렸는지 확인 (Streamlit에서는 어려운 부분, 간단화를 위해 생략)
        
    # --- 시간 종료 및 보상 지급/알림 ---
    
    st.session_state.is_running = False
    
    if is_study_session:
        # 공부 세션이 끝났을 경우
        reward = duration_minutes * 40 # 25분 기준 1000 코인 지급
        st.balloons() 
        st.success(f"🥳 {duration_minutes}분 공부 완료! **{reward} 코인** 지급!")
        st.session_state.coins += reward
        st.session_state.is_study = False # 다음은 휴식 세션
        
        # 알림 소리 효과 (웹에서는 복잡하므로 텍스트로 대체)
        if 'retro_alarm' in st.session_state.owned_items:
             st.info("🚨 레트로 알림 소리 띠리리링!")
        else:
             st.info("🔔 기본 알림이 울립니다.")
             
    else:
        # 휴식 세션이 끝났을 경우
        st.info(f"✅ {duration_minutes}분 휴식 끝! 다시 공부를 시작하세요.")
        st.session_state.is_study = True # 다음은 공부 세션
        
    st.rerun() # 상태 업데이트 및 화면 전환


# --- 4. 메인 앱 레이아웃 ---

st.title("📚 뽀모도로 & 코인 리워드 앱")
st.header(f"💰 현재 코인: {st.session_state.coins}원")

# 탭 구조 (타이머와 상점 분리)
tab_timer, tab_shop = st.tabs(["⏱️ 타이머", "🛒 상점"])

# --- 4.1 타이머 탭 ---
with tab_timer:
    
    # 타이머 설정 슬라이더
    study_duration = st.slider("공부 시간 (분)", min_value=5, max_value=60, value=25, step=5)
    break_duration = st.slider("휴식 시간 (분)", min_value=1, max_value=15, value=5, step=1)
    
    st.divider()

    # 타이머 시작 버튼
    if not st.session_state.is_running:
        if st.button("▶️ 공부/휴식 시작", type="primary", use_container_width=True):
            st.session_state.is_running = True
            st.rerun()
            
    # 타이머가 실행 중일 때 로직
    if st.session_state.is_running:
        # 타이머 중지 버튼 (앱의 구조상 실제 타이머 스레드를 멈추는 것은 복잡합니다.)
        if st.button("⏹️ 중지하기", use_container_width=True):
            st.session_state.is_running = False
            st.warning("타이머가 중지되었습니다.")
            st.session_state.is_study = True # 중지 후에는 다시 공부 시작으로 리셋
            st.rerun()
            
        # 현재 상태에 따라 타이머 실행
        if st.session_state.is_study:
            run_timer(study_duration, is_study_session=True)
        else:
            run_timer(break_duration, is_study_session=False)

# --- 4.2 상점 탭 ---
with tab_shop:
    st.subheader("아이템 상점")
    
    # 아이템 목록을 반복하며 표시
    for item_key, item_info in SHOP_ITEMS.items():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{item_info['name']}** ({item_info['price']}원)")
            st.caption(item_info['effect'])
            
        with col2:
            if item_key in st.session_state.owned_items:
                st.success("✅ 소유 중")
            else:
                # 구매 버튼 로직
                if st.button("구매", key=f"buy_{item_key}"):
                    if st.session_state.coins >= item_info['price']:
                        # 구매 성공
                        st.session_state.coins -= item_info['price']
                        st.session_state.owned_items.add(item_key)
                        st.success(f"{item_info['name']} 구매 완료! 재시작하면 적용됩니다.")
                        # st.rerun()
                    else:
                        # 코인 부족
                        st.error("잔액이 부족합니다.")
    
st.caption("참고: Streamlit의 특성상 중지 버튼을 누르면 타이머가 완전히 멈추지 않고, 다음 1초 대기 후에 중지 상태로 돌아갈 수 있습니다.")
