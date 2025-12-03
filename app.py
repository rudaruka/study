import streamlit as st
import time

# --- 1. 테마 및 아이템 정의 (중앙 집중식 데이터) ---

THEME_STYLES = {
    'dark_mode': {
        'name': '다크 모드', 
        'price': 5000, 
        'effect': '앱 배경을 어둡게 바꿉니다.',
        'css': """
            .main { background-color: #1E1E1E; color: #FFFFFF; } 
            h2, h3, h4 { color: #CCCCCC !important; }
            .stButton>button { border: 1px solid #555555; }
        """
    },
    'forest_theme': {
        'name': '🌳 포레스트 테마', 
        'price': 8000, 
        'effect': '편안한 녹색 계열 테마를 적용합니다.',
        'css': """
            .main { background-color: #E8F5E9; color: #1B5E20; }
            h2, h3, h4 { color: #388E3C !important; }
            .stSlider > div > div:nth-child(1) { background-color: #81C784 !important; }
            .stTextInput>div>div>input { border-color: #4CAF50; }
        """
    },
    'sky_theme': {
        'name': '☁️ 스카이 테마', 
        'price': 10000, 
        'effect': '시원한 파란색 계열 테마를 적용합니다.',
        'css': """
            .main { background-color: #E3F2FD; color: #1565C0; }
            h2, h3, h4 { color: #1E88E5 !important; }
            .stButton>button { background-color: #90CAF9; color: #000000; }
        """
    }
}

OTHER_ITEMS = {
    'retro_alarm': {'name': '레트로 알림', 'price': 3000, 'effect': '종료 알림 소리를 레트로 스타일로 바꿉니다.'}
}

SHOP_ITEMS = {**THEME_STYLES, **OTHER_ITEMS}


# --- 2. 초기 설정 및 상태 관리 ---

if 'coins' not in st.session_state:
    st.session_state.coins = 0
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'is_study' not in st.session_state:
    st.session_state.is_study = True 
if 'owned_items' not in st.session_state:
    st.session_state.owned_items = set()
    
# NEW: 사용자가 설정한 전체 시간 (분)
if 'study_duration' not in st.session_state:
    st.session_state.study_duration = 25
if 'break_duration' not in st.session_state:
    st.session_state.break_duration = 5
    
# NEW: 현재 남은 시간 (초) - 중지 시 이 값을 저장합니다.
if 'remaining_study_seconds' not in st.session_state:
    st.session_state.remaining_study_seconds = st.session_state.study_duration * 60
if 'remaining_break_seconds' not in st.session_state:
    st.session_state.remaining_break_seconds = st.session_state.break_duration * 60


# --- 3. 테마 적용 함수 ---

def apply_theme():
    full_css = ""
    for item_key in st.session_state.owned_items:
        if item_key in THEME_STYLES:
            full_css += THEME_STYLES[item_key]['css']
            
    if full_css:
        st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)

apply_theme()


# --- 4. 상점 구매 로직 함수 ---

def buy_shop_logic(item_key, item_info):
    if item_key in st.session_state.owned_items:
        if item_key in THEME_STYLES:
             st.success("✅ 적용 중 (소유)")
        else:
             st.success("✅ 소유 중")
    else:
        if st.button("구매", key=f"buy_{item_key}"):
            if st.session_state.coins >= item_info['price']:
                st.session_state.coins -= item_info['price']
                st.session_state.owned_items.add(item_key)
                st.success(f"{item_info['name']} 구매 완료! 적용되었습니다.")
                
                apply_theme()
                st.rerun()
            else:
                st.error("잔액이 부족합니다.")


# --- 5. 타이머 로직 함수 ---

def run_timer(is_study_session=True):
    # 사용할 남은 시간 상태 변수 키를 결정
    if is_study_session:
        session_key = 'remaining_study_seconds'
        duration_key = 'study_duration'
    else:
        session_key = 'remaining_break_seconds'
        duration_key = 'break_duration'
        
    current_seconds = st.session_state[session_key] # 저장된 남은 시간부터 시작
    timer_placeholder = st.empty()
    
    # 남은 시간부터 0까지 카운트다운
    for i in range(current_seconds, 0, -1):
        # NEW: 다음 초에 남을 시간을 세션 상태에 저장 (중지 시 이 값이 보존됨)
        st.session_state[session_key] = i - 1 

        minutes, seconds = divmod(i, 60)
        
        color = "red" if is_study_session else "blue"
        status_text = "📚 공부 중" if is_study_session else "☕ 휴식 중"
        timer_placeholder.markdown(f"## <span style='color:{color};'>{status_text}</span> 남은 시간: {minutes:02d}:{seconds:02d}", unsafe_allow_html=True)
        
        time.sleep(1)
        
    # --- 타이머 완료 로직 ---
    st.session_state.is_running = False
    
    if is_study_session:
        reward = st.session_state[duration_key] * 40 
        st.balloons() 
        st.success(f"🥳 {st.session_state[duration_key]}분 공부 완료! **{reward} 코인** 지급!")
        st.session_state.coins += reward
        st.session_state.is_study = False 
        
        # 완료되었으므로 남은 시간을 전체 시간으로 초기화
        st.session_state.remaining_study_seconds = st.session_state.study_duration * 60
        
        if 'retro_alarm' in st.session_state.owned_items:
             st.info("🚨 레트로 알림 소리 띠리리링!")
        else:
             st.info("🔔 기본 알림이 울립니다.")
             
    else:
        st.info(f"✅ {st.session_state[duration_key]}분 휴식 끝!")
        st.session_state.is_study = True 
        
        # 완료되었으므로 남은 시간을 전체 시간으로 초기화
        st.session_state.remaining_break_seconds = st.session_state.break_duration * 60
        
    st.rerun()


# NEW: 슬라이더 변경 시 남은 시간도 초기화하는 함수
def update_durations():
    # 설정 시간 변경 시, 남은 시간을 새로운 설정 시간(초)으로 초기화
    st.session_state.remaining_study_seconds = st.session_state.study_duration * 60
    st.session_state.remaining_break_seconds = st.session_state.break_duration * 60
    st.session_state.is_study = True # 설정 변경 시 순서를 공부로 리셋


# --- 6. 메인 앱 레이아웃 ---

st.title("📚 공부법은 위대하다!")
st.header(f"💰 현재 코인: {st.session_state.coins}원")

tab_timer, tab_shop = st.tabs(["⏱️ 타이머", "🛒 상점"])

# --- 6.1 타이머 탭 (st.empty()를 사용하여 안정화 및 신규 버튼 추가) ---
with tab_timer:
    
    # 슬라이더 컨테이너를 먼저 확보합니다.
    slider_placeholder = st.empty()

    # 버튼 컨테이너를 먼저 확보합니다.
    button_placeholder = st.empty()
    
    st.divider()
    
    # 1. 타이머가 실행 중이 아닐 때: 설정 슬라이더와 시작/이어하기 버튼 표시
    if not st.session_state.is_running:
        
        # 슬라이더 표시 (타이머가 멈춰있을 때만)
        with slider_placeholder.container():
            st.session_state.study_duration = st.slider(
                "공부 시간 설정 (분) * 한번 설정시 타이머가 끝날때까지 변경하지 마세요 *", 
                min_value=5, max_value=60, 
                value=st.session_state.study_duration, step=5, 
                key='slider_study',
                on_change=update_durations
            )
            st.session_state.break_duration = st.slider(
                "휴식 시간 설정 (분) * 한번 설정시 타이머가 끝날때까지 변경하지 마세요 *", 
                min_value=1, max_value=15, 
                value=st.session_state.break_duration, step=1,
                key='slider_break',
                on_change=update_durations
            )
        
        # 현재 남은 시간 확인
        if st.session_state.is_study:
            current_remaining = st.session_state.remaining_study_seconds
            full_duration_seconds = st.session_state.study_duration * 60
        else:
            current_remaining = st.session_state.remaining_break_seconds
            full_duration_seconds = st.session_state.break_duration * 60

        # --- Case 1: 마저 하기(Resume) + 시간 초기화(Reset) 버튼 표시 ---
        if current_remaining > 0 and current_remaining < full_duration_seconds:
            minutes = current_remaining // 60
            seconds = current_remaining % 60
            resume_button_text = f"▶️ {minutes}분 {seconds}초 마저 하기"
            
            # 버튼 영역을 2개 컬럼으로 분할
            with button_placeholder.container():
                col_reset, col_resume = st.columns(2)
            
                # 1. 시간 초기화 버튼
                if col_reset.button("🔄 시간 초기화", use_container_width=True, key='reset_timer_button'):
                    st.session_state.remaining_study_seconds = st.session_state.study_duration * 60
                    st.session_state.remaining_break_seconds = st.session_state.break_duration * 60
                    st.session_state.is_study = True # 다음 세션을 공부로 초기화
                    st.warning("타이머가 처음 설정 값으로 초기화되었습니다.")
                    st.rerun()
    
                # 2. 마저 하기 버튼 (Resume)
                if col_resume.button(resume_button_text, type="warning", use_container_width=True, key='start_resume_button'):
                    st.session_state.is_running = True
                    st.rerun()

        # --- Case 2: 시작 버튼만 표시 (시간이 가득 찼거나 0일 때) ---
        else:
            if st.session_state.is_study:
                button_text = f"▶️ {st.session_state.study_duration}분 공부 시작"
                button_type = "primary"
            else:
                button_text = f"☕ {st.session_state.break_duration}분 휴식 시작"
                button_type = "secondary"

            # 버튼을 고정된 button_placeholder 안에 그립니다.
            if button_placeholder.button(button_text, type=button_type, use_container_width=True, key='start_resume_button'):
                st.session_state.is_running = True
                st.rerun()
            
    # 2. 타이머가 실행 중일 때: 중지 버튼만 표시하고 타이머 실행
    else: # st.session_state.is_running == True
        
        # 실행 중이므로 슬라이더는 지웁니다.
        slider_placeholder.empty()

        # 중지 버튼을 고정된 button_placeholder 안에 그립니다.
        if button_placeholder.button("⏹️ 중지하기", use_container_width=True, key='stop_timer_button'):
            st.session_state.is_running = False
            st.warning("타이머가 중지되었습니다. '마저 하기' 버튼을 눌러 남은 시간을 다시 시작하세요.")
            st.rerun()
            
        # run_timer 함수 호출 (타이머 카운트다운 시작)
        if st.session_state.is_study:
            run_timer(is_study_session=True)
        else:
            run_timer(is_study_session=False)

# --- 6.2 상점 탭 ---
with tab_shop:
    st.subheader("아이템 상점")
    
    # 테마 아이템 표시
    st.markdown("### 🖼️ 테마 및 디자인")
    for item_key, item_info in THEME_STYLES.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item_info['name']}** ({item_info['price']}원)")
            st.caption(item_info['effect'])
        with col2:
            buy_shop_logic(item_key, item_info)
            
    st.markdown("---")
    
    # 보조 아이템 표시
    st.markdown("### 📢 알림 및 효과")
    for item_key, item_info in OTHER_ITEMS.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item_info['name']}** ({item_info['price']}원)")
            st.caption(item_info['effect'])
        with col2:
            buy_shop_logic(item_key, item_info)
