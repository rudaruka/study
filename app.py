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
    
if 'study_duration' not in st.session_state:
    st.session_state.study_duration = 25
if 'break_duration' not in st.session_state:
    st.session_state.break_duration = 5


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

def run_timer(duration_minutes, is_study_session=True):
    total_seconds = duration_minutes * 60
    timer_placeholder = st.empty()
    
    for i in range(total_seconds, 0, -1):
        minutes, seconds = divmod(i, 60)
        
        color = "red" if is_study_session else "blue"
        status_text = "📚 공부 중" if is_study_session else "☕ 휴식 중"
        timer_placeholder.markdown(f"## <span style='color:{color};'>{status_text}</span> 남은 시간: {minutes:02d}:{seconds:02d}", unsafe_allow_html=True)
        
        time.sleep(1)
        
    # **수정**: 타이머가 완료되면 is_running만 False로 바꾸고, 다음 세션 버튼이 tab_timer에 나타나도록 합니다.
    st.session_state.is_running = False 
    
    if is_study_session:
        reward = duration_minutes * 40 
        st.balloons() 
        st.success(f"🥳 {duration_minutes}분 공부 완료! **{reward} 코인** 지급!")
        st.session_state.coins += reward
        st.session_state.is_study = False # 다음은 휴식 세션
        
        if 'retro_alarm' in st.session_state.owned_items:
             st.info("🚨 레트로 알림 소리 띠리리링!")
        else:
             st.info("🔔 기본 알림이 울립니다.")
             
    else:
        st.info(f"✅ {duration_minutes}분 휴식 끝!")
        st.session_state.is_study = True # 다음은 공부 세션
        
    st.rerun() # 화면 전환을 위해 새로고침


# --- 6. 메인 앱 레이아웃 ---

st.title("📚 뽀모도로 & 코인 리워드 앱")
st.header(f"💰 현재 코인: {st.session_state.coins}원")

tab_timer, tab_shop = st.tabs(["⏱️ 타이머", "🛒 상점"])

# --- 6.1 타이머 탭 (재시작 로직 강화) ---
with tab_timer:
    
    # 타이머가 실행 중이 아닐 때 설정 슬라이더와 다음 세션 시작 버튼을 표시합니다.
    if not st.session_state.is_running:
        
        # 설정 슬라이더는 is_running이 False일 때만 표시됩니다.
        st.session_state.study_duration = st.slider(
            "공부 시간 설정 (분)", 
            min_value=5, max_value=60, 
            value=st.session_state.study_duration, step=5, 
            key='slider_study'
        )
        st.session_state.break_duration = st.slider(
            "휴식 시간 설정 (분)", 
            min_value=1, max_value=15, 
            value=st.session_state.break_duration, step=1,
            key='slider_break'
        )
        st.divider()

        # **수정**: is_study 상태에 따라 버튼 텍스트를 변경합니다.
        if st.session_state.is_study:
            button_text = f"▶️ {st.session_state.study_duration}분 공부 시작"
            button_type = "primary"
        else:
            button_text = f"☕ {st.session_state.break_duration}분 휴식 시작"
            button_type = "secondary"

        if st.button(button_text, type=button_type, use_container_width=True):
            st.session_state.is_running = True
            st.rerun()
            
    # 타이머가 실행 중일 때 로직
    if st.session_state.is_running:
        
        # 타이머 실행 중에는 중지 버튼만 표시
        if st.button("⏹️ 중지하기", use_container_width=True):
            st.session_state.is_running = False
            st.warning("타이머가 중지되었습니다. 다음 '공부 시작' 버튼을 눌러 초기화하고 다시 시작하세요.")
            st.session_state.is_study = True # 중지 시에는 다음 세션을 '공부'로 초기화
            st.rerun()
            
        # run_timer 함수에 세션 상태에 저장된 값을 전달합니다.
        if st.session_state.is_study:
            run_timer(st.session_state.study_duration, is_study_session=True)
        else:
            run_timer(st.session_state.break_duration, is_study_session=False)

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
