import streamlit as st
import time

# --- 1. 테마 및 아이템 정의 (중앙 집중식 데이터) ---

# 테마 스타일 정의: 아이템 키, 가격, 설명, 적용될 CSS 내용을 포함합니다.
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

# 보조 아이템 (디자인 외 기능)
OTHER_ITEMS = {
    'retro_alarm': {'name': '레트로 알림', 'price': 3000, 'effect': '종료 알림 소리를 레트로 스타일로 바꿉니다.'}
}

# 상점에서 판매할 모든 아이템을 합칩니다.
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


# --- 3. 테마 적용 함수 (CSS 병합 로직) ---

def apply_theme():
    """
    구매된 모든 테마 아이템의 CSS를 병합하여 한 번에 적용합니다.
    """
    full_css = ""
    for item_key in st.session_state.owned_items:
        if item_key in THEME_STYLES:
            full_css += THEME_STYLES[item_key]['css']
            
    if full_css:
        st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)

# 앱 시작 시 테마를 즉시 적용합니다.
apply_theme()


# --- 4. 상점 구매 로직 함수 ---
# 메인 레이아웃에서 사용되기 전에 정의되어야 합니다.

def buy_shop_logic(item_key, item_info):
    if item_key in st.session_state.owned_items:
        # 테마 아이템이라면 '적용 중' 메시지 표시
        if item_key in THEME_STYLES:
             st.success("✅ 적용 중 (소유)")
        else:
             st.success("✅ 소유 중")
    else:
        # 구매 버튼은 고유한 key를 사용합니다.
        if st.button("구매", key=f"buy_{item_key}"):
            if st.session_state.coins >= item_info['price']:
                # 구매 성공
                st.session_state.coins -= item_info['price']
                st.session_state.owned_items.add(item_key)
                st.success(f"{item_info['name']} 구매 완료! 적용되었습니다.")
                
                # 구매 후 테마를 즉시 적용하고 화면을 새로고침합니다.
                apply_theme()
                st.rerun()
            else:
                # 잔액 부족
                st.error("잔액이 부족합니다.")


# --- 5. 타이머 로직 함수 ---

def run_timer(duration_minutes, is_study_session=True):
    total_seconds = duration_minutes * 60
    timer_placeholder = st.empty()
    
    for i in range(total_seconds, 0, -1):
        minutes, seconds = divmod(i, 60)
        
        # 적용된 테마와 상관없이 타이머 색상을 명확히 구분하기 위해 HTML을 사용합니다.
        color = "red" if is_study_session else "blue"
        status_text = "📚 공부 중" if is_study_session else "☕ 휴식 중"
        timer_placeholder.markdown(f"## <span style='color:{color};'>{status_text}</span> 남은 시간: {minutes:02d}:{seconds:02d}", unsafe_allow_html=True)
        
        time.sleep(1)
        
    st.session_state.is_running = False
    
    if is_study_session:
        # 공부 세션이 끝났을 경우 (25분 기준 1000 코인)
        reward = duration_minutes * 40 
        st.balloons() 
        st.success(f"🥳 {duration_minutes}분 공부 완료! **{reward} 코인** 지급!")
        st.session_state.coins += reward
        st.session_state.is_study = False 
        
        # 알림 소리 효과 적용
        if 'retro_alarm' in st.session_state.owned_items:
             st.info("🚨 레트로 알림 소리 띠리리링!")
        else:
             st.info("🔔 기본 알림이 울립니다.")
             
    else:
        # 휴식 세션이 끝났을 경우
        st.info(f"✅ {duration_minutes}분 휴식 끝! 다시 공부를 시작하세요.")
        st.session_state.is_study = True 
        
    st.rerun() # 상태 업데이트 및 화면 전환을 위해 새로고침


# --- 6. 메인 앱 레이아웃 ---

st.title("📚 뽀모도로 & 코인 리워드 앱")
st.header(f"💰 현재 코인: {st.session_state.coins}원")

tab_timer, tab_shop = st.tabs(["⏱️ 타이머", "🛒 상점"])

# --- 6.1 타이머 탭 ---
with tab_timer:
    study_duration = st.slider("공부 시간 (분)", min_value=5, max_value=60, value=25, step=5)
    break_duration = st.slider("휴식 시간 (분)", min_value=1, max_value=15, value=5, step=1)
    
    st.divider()

    if not st.session_state.is_running:
        if st.button("▶️ 공부/휴식 시작", type="primary", use_container_width=True):
            st.session_state.is_running = True
            st.rerun()
            
    if st.session_state.is_running:
        if st.button("⏹️ 중지하기", use_container_width=True):
            st.session_state.is_running = False
            st.warning("타이머가 중지되었습니다.")
            st.session_state.is_study = True 
            st.rerun()
            
        if st.session_state.is_study:
            run_timer(study_duration, is_study_session=True)
        else:
            run_timer(break_duration, is_study_session=False)

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
