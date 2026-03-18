import streamlit as st
import time
from datetime import date, datetime

# =====================================================
# 1. 데이터 정의
# =====================================================

THEME_STYLES = {
    'dark_mode': {
        'name': '🌙 다크 모드',
        'price': 5000,
        'effect': '앱 배경을 어둡게 바꿉니다.',
        'css': """
            .main { background-color: #1E1E1E !important; color: #FFFFFF; }
            h2, h3, h4 { color: #CCCCCC !important; }
            .stButton>button { border: 1px solid #555555; }
        """
    },
    'forest_theme': {
        'name': '🌳 포레스트 테마',
        'price': 8000,
        'effect': '편안한 녹색 계열 테마를 적용합니다.',
        'css': """
            .main { background-color: #E8F5E9 !important; color: #1B5E20; }
            h2, h3, h4 { color: #388E3C !important; }
            .stTextInput>div>div>input { border-color: #4CAF50; }
        """
    },
    'sky_theme': {
        'name': '☁️ 스카이 테마',
        'price': 10000,
        'effect': '시원한 파란색 계열 테마를 적용합니다.',
        'css': """
            .main { background-color: #E3F2FD !important; color: #1565C0; }
            h2, h3, h4 { color: #1E88E5 !important; }
            .stButton>button { background-color: #90CAF9; color: #000000; }
        """
    },
    'starry_background': {
        'name': '🌌 별이 빛나는 밤',
        'price': 12000,
        'effect': '밤하늘을 연상시키는 그라데이션 배경을 적용합니다.',
        'css': """
            .main {
                background: linear-gradient(to top right, #0F2027, #203A43, #2C5364) !important;
                color: #E0E0E0;
            }
            h2, h3, h4 { color: #ADD8E6 !important; }
            .stButton>button { border: 1px solid #778899; }
        """
    },
    'cherry_blossom': {
        'name': '🌸 벚꽃 테마',
        'price': 9000,
        'effect': '포근한 벚꽃빛 핑크 테마를 적용합니다.',
        'css': """
            .main { background-color: #FFF0F5 !important; color: #880E4F; }
            h2, h3, h4 { color: #C2185B !important; }
            .stButton>button { background-color: #F8BBD9; color: #880E4F; }
        """
    }
}

OTHER_ITEMS = {
    'retro_alarm': {'name': '🔔 레트로 알림', 'price': 3000, 'effect': '종료 알림 소리를 레트로 스타일로 바꿉니다.'},
    'golden_font': {'name': '🏆 황금 폰트', 'price': 4000, 'effect': '타이머 글자 색을 황금색으로 바꿉니다.'},
    'double_coin': {'name': '💎 코인 2배', 'price': 15000, 'effect': '공부 완료 시 코인을 2배로 받습니다.'},
    'focus_bgm': {'name': '🎵 집중 BGM', 'price': 6000, 'effect': '타이머 실행 중 집중 BGM 이모지를 표시합니다.'},
}

# 업적 정의
ACHIEVEMENTS = {
    'first_study':   {'name': '🎓 첫 걸음',      'desc': '첫 번째 공부 세션 완료', 'condition': lambda s: s['total_sessions'] >= 1,   'reward': 1000},
    'five_sessions': {'name': '🔥 5연속 집중',    'desc': '총 5번 공부 완료',       'condition': lambda s: s['total_sessions'] >= 5,   'reward': 3000},
    'ten_sessions':  {'name': '💪 10번 도전',     'desc': '총 10번 공부 완료',      'condition': lambda s: s['total_sessions'] >= 10,  'reward': 5000},
    'one_hour':      {'name': '⏰ 1시간 돌파',    'desc': '총 공부 시간 60분 달성', 'condition': lambda s: s['total_minutes'] >= 60,   'reward': 2000},
    'five_hours':    {'name': '🌟 5시간 달성',    'desc': '총 공부 시간 300분 달성','condition': lambda s: s['total_minutes'] >= 300,  'reward': 8000},
    'ten_hours':     {'name': '👑 10시간 마스터',  'desc': '총 공부 시간 600분 달성','condition': lambda s: s['total_minutes'] >= 600,  'reward': 20000},
    'coin_100':      {'name': '💰 코인 부자',     'desc': '코인 총 100개 적립',     'condition': lambda s: s['total_coins_earned'] >= 100, 'reward': 500},
    'coin_1000':     {'name': '🏦 코인 만 부자',  'desc': '코인 총 1000개 적립',    'condition': lambda s: s['total_coins_earned'] >= 1000,'reward': 2000},
    'pomodoro_4':    {'name': '🍅 뽀모도로 4세트','desc': '4세트 사이클 완료',      'condition': lambda s: s['completed_cycles'] >= 1,  'reward': 4000},
    'daily_3':       {'name': '📅 오늘 3번 완료', 'desc': '하루에 3번 공부 완료',   'condition': lambda s: s['today_sessions'] >= 3,    'reward': 1500},
}

# =====================================================
# 2. 초기 상태 설정
# =====================================================

defaults = {
    'coins': 0,
    'is_running': False,
    'is_study': True,
    'owned_items': set(),
    'active_theme': None,
    'study_duration': 25,
    'break_duration': 5,
    'long_break_duration': 15,
    'sessions_before_long_break': 4,
    'current_cycle_count': 0,   # 현재 사이클 내 완료한 공부 횟수
    'completed_cycles': 0,      # 완성된 전체 사이클 수
    # 통계
    'total_sessions': 0,
    'total_minutes': 0,
    'total_coins_earned': 0,
    'today_sessions': 0,
    'today_minutes': 0,
    'last_date': str(date.today()),
    'daily_history': {},        # {"2024-01-01": {"sessions": N, "minutes": M}}
    'session_log': [],          # [{"time": "HH:MM", "duration": N, "type": "study"}]
    # 업적
    'unlocked_achievements': set(),
    # 사이클 모드 여부
    'cycle_mode': True,
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 날짜 바뀌면 오늘 통계 리셋
today_str = str(date.today())
if st.session_state.last_date != today_str:
    st.session_state.today_sessions = 0
    st.session_state.today_minutes = 0
    st.session_state.last_date = today_str

# =====================================================
# 3. 유틸리티 함수
# =====================================================

def apply_theme():
    active_key = st.session_state.active_theme
    if active_key and active_key in THEME_STYLES:
        st.markdown(f"<style>{THEME_STYLES[active_key]['css']}</style>", unsafe_allow_html=True)

def update_durations():
    st.session_state.study_duration = max(1, st.session_state.input_study)
    st.session_state.break_duration = max(1, st.session_state.input_break)
    st.session_state.remaining_study_seconds = int(st.session_state.study_duration * 60)
    st.session_state.remaining_break_seconds = int(st.session_state.break_duration * 60)
    st.session_state.is_study = True

def check_achievements():
    """업적 달성 여부 확인 후 보상 지급"""
    newly_unlocked = []
    stats = {
        'total_sessions': st.session_state.total_sessions,
        'total_minutes': st.session_state.total_minutes,
        'total_coins_earned': st.session_state.total_coins_earned,
        'today_sessions': st.session_state.today_sessions,
        'completed_cycles': st.session_state.completed_cycles,
    }
    for key, ach in ACHIEVEMENTS.items():
        if key not in st.session_state.unlocked_achievements:
            if ach['condition'](stats):
                st.session_state.unlocked_achievements.add(key)
                st.session_state.coins += ach['reward']
                st.session_state.total_coins_earned += ach['reward']
                newly_unlocked.append(ach)
    return newly_unlocked

def toggle_theme(item_key):
    if st.session_state.active_theme == item_key:
        st.session_state.active_theme = None
    else:
        st.session_state.active_theme = item_key
    apply_theme()
    st.rerun()

def buy_shop_logic(item_key, item_info):
    is_owned = item_key in st.session_state.owned_items
    is_theme = item_key in THEME_STYLES

    if is_owned:
        if is_theme:
            is_active = st.session_state.active_theme == item_key
            if is_active:
                if st.button("해제 ❌", key=f"deactivate_{item_key}", use_container_width=True):
                    toggle_theme(item_key)
                st.success("✅ 적용 중")
            else:
                if st.button("적용 👍", key=f"activate_{item_key}", use_container_width=True, type="primary"):
                    toggle_theme(item_key)
                st.caption("소유 중")
        else:
            st.success("✅ 소유 중")
    else:
        if st.button(f"구매 {item_info['price']}원", key=f"buy_{item_key}", use_container_width=True):
            if st.session_state.coins >= item_info['price']:
                st.session_state.coins -= item_info['price']
                st.session_state.owned_items.add(item_key)
                if is_theme:
                    st.session_state.active_theme = item_key
                st.success(f"{item_info['name']} 구매 완료!")
                st.rerun()
            else:
                st.error("잔액이 부족합니다.")

def get_next_session_type():
    """다음 세션이 짧은 휴식인지 긴 휴식인지 반환"""
    if not st.session_state.cycle_mode:
        return 'short_break'
    count = st.session_state.current_cycle_count + 1  # 완료 후 카운트
    if count >= st.session_state.sessions_before_long_break:
        return 'long_break'
    return 'short_break'

# =====================================================
# 4. 남은 시간 초기화 (세션 상태에 없을 때만)
# =====================================================

if 'remaining_study_seconds' not in st.session_state:
    st.session_state.remaining_study_seconds = st.session_state.study_duration * 60
if 'remaining_break_seconds' not in st.session_state:
    st.session_state.remaining_break_seconds = st.session_state.break_duration * 60
if 'remaining_long_break_seconds' not in st.session_state:
    st.session_state.remaining_long_break_seconds = st.session_state.long_break_duration * 60
# is_long_break 상태 추가
if 'is_long_break' not in st.session_state:
    st.session_state.is_long_break = False

# =====================================================
# 5. 타이머 로직
# =====================================================

def run_timer(is_study_session=True, is_long_break=False):
    if is_study_session:
        session_key = 'remaining_study_seconds'
        duration_key = 'study_duration'
    elif is_long_break:
        session_key = 'remaining_long_break_seconds'
        duration_key = 'long_break_duration'
    else:
        session_key = 'remaining_break_seconds'
        duration_key = 'break_duration'

    current_seconds = st.session_state[session_key]
    timer_placeholder = st.empty()
    progress_placeholder = st.empty()

    is_golden = 'golden_font' in st.session_state.owned_items
    has_bgm = 'focus_bgm' in st.session_state.owned_items
    total_seconds = st.session_state[duration_key] * 60

    for i in range(current_seconds, 0, -1):
        st.session_state[session_key] = i - 1
        minutes, seconds = divmod(i, 60)

        if is_golden:
            color = "#FFD700"
        elif is_study_session:
            color = "#FF4B4B"
        elif is_long_break:
            color = "#7B2FBE"
        else:
            color = "#1E88E5"

        if is_study_session:
            status_text = "📚 공부 중"
            if has_bgm:
                status_text += " 🎵"
        elif is_long_break:
            status_text = "🛌 긴 휴식 중"
        else:
            status_text = "☕ 휴식 중"

        progress = (total_seconds - i) / total_seconds
        progress_placeholder.progress(progress)
        timer_placeholder.markdown(
            f"<h2 style='text-align:center; color:{color};'>{status_text}</h2>"
            f"<h1 style='text-align:center; color:{color}; font-size:72px;'>{minutes:02d}:{seconds:02d}</h1>",
            unsafe_allow_html=True
        )
        time.sleep(1)

    st.session_state.is_running = False

    # --- 공부 완료 ---
    if is_study_session:
        duration_val = st.session_state[duration_key]
        base_reward = int(duration_val * 40)
        is_double = 'double_coin' in st.session_state.owned_items
        reward = base_reward * 2 if is_double else base_reward

        st.session_state.coins += reward
        st.session_state.total_coins_earned += reward
        st.session_state.total_sessions += 1
        st.session_state.total_minutes += duration_val
        st.session_state.today_sessions += 1
        st.session_state.today_minutes += duration_val

        # 사이클 관리
        st.session_state.current_cycle_count += 1
        if st.session_state.current_cycle_count >= st.session_state.sessions_before_long_break:
            st.session_state.is_long_break = True
            st.session_state.current_cycle_count = 0
            st.session_state.completed_cycles += 1
        else:
            st.session_state.is_long_break = False

        # 일별 기록 저장
        today = str(date.today())
        if today not in st.session_state.daily_history:
            st.session_state.daily_history[today] = {'sessions': 0, 'minutes': 0}
        st.session_state.daily_history[today]['sessions'] += 1
        st.session_state.daily_history[today]['minutes'] += duration_val

        # 세션 로그
        st.session_state.session_log.append({
            'time': datetime.now().strftime("%H:%M"),
            'duration': duration_val,
            'type': 'study'
        })

        st.balloons()
        reward_text = f"**{reward} 코인** 지급!" + (" (2배!💎)" if is_double else "")
        st.success(f"🥳 {duration_val}분 공부 완료! {reward_text}")

        # 업적 확인
        newly = check_achievements()
        for ach in newly:
            st.toast(f"🏆 업적 달성: {ach['name']} (+{ach['reward']}코인)", icon="🎉")

        if 'retro_alarm' in st.session_state.owned_items:
            st.info("🚨 레트로 알림 띠리리링!")
        else:
            st.info("🔔 기본 알림이 울립니다.")

        st.session_state.is_study = False
        st.session_state.remaining_study_seconds = int(st.session_state.study_duration * 60)

    # --- 휴식 완료 ---
    else:
        break_type = "긴 휴식" if is_long_break else "휴식"
        st.info(f"✅ {st.session_state[duration_key]}분 {break_type} 끝! 다시 집중해볼까요? 💪")
        st.session_state.is_study = True
        st.session_state.is_long_break = False
        if is_long_break:
            st.session_state.remaining_long_break_seconds = int(st.session_state.long_break_duration * 60)
        else:
            st.session_state.remaining_break_seconds = int(st.session_state.break_duration * 60)

    st.rerun()

# =====================================================
# 6. 메인 레이아웃
# =====================================================

apply_theme()

st.title("📚 공부법은 위대하다!")

# 상단 핵심 지표
col_coin, col_session, col_cycle, col_today = st.columns(4)
with col_coin:
    st.metric("💰 코인", f"{st.session_state.coins:,}원")
with col_session:
    st.metric("📖 총 세션", f"{st.session_state.total_sessions}회")
with col_cycle:
    st.metric("🍅 완료 사이클", f"{st.session_state.completed_cycles}세트")
with col_today:
    st.metric("📅 오늘 공부", f"{st.session_state.today_minutes}분")

# 사이클 진행 표시
if st.session_state.cycle_mode:
    cycle_count = st.session_state.current_cycle_count
    total_in_cycle = st.session_state.sessions_before_long_break
    st.markdown("**현재 사이클 진행:**")
    cycle_icons = ""
    for i in range(total_in_cycle):
        if i < cycle_count:
            cycle_icons += "🍅 "
        else:
            cycle_icons += "⬜ "
    st.markdown(f"{cycle_icons}  ← {total_in_cycle}개 완료 시 🛌 긴 휴식")

st.divider()

tab_timer, tab_stats, tab_achievements, tab_shop = st.tabs(["⏱️ 타이머", "📊 통계", "🏆 업적", "🛒 상점"])

# =====================================================
# 타이머 탭
# =====================================================
with tab_timer:

    input_placeholder = st.empty()
    button_placeholder = st.empty()
    st.divider()

    if not st.session_state.is_running:

        with input_placeholder.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                st.number_input(
                    "📚 공부 시간 (분)", min_value=1, max_value=180,
                    value=int(st.session_state.study_duration), step=1,
                    key='input_study', on_change=update_durations, format="%d"
                )
            with c2:
                st.number_input(
                    "☕ 짧은 휴식 (분)", min_value=1, max_value=30,
                    value=int(st.session_state.break_duration), step=1,
                    key='input_break', on_change=update_durations, format="%d"
                )
            with c3:
                st.number_input(
                    "🛌 긴 휴식 (분)", min_value=5, max_value=60,
                    value=int(st.session_state.long_break_duration), step=5,
                    key='input_long_break',
                    on_change=lambda: setattr(st.session_state, 'long_break_duration', max(5, st.session_state.input_long_break)),
                    format="%d"
                )

            col_mode, col_cycle_set = st.columns(2)
            with col_mode:
                st.session_state.cycle_mode = st.toggle("🔄 사이클 모드 (긴 휴식 자동 전환)", value=st.session_state.cycle_mode)
            with col_cycle_set:
                if st.session_state.cycle_mode:
                    st.session_state.sessions_before_long_break = st.number_input(
                        "🍅 긴 휴식까지 세션 수", min_value=2, max_value=8,
                        value=st.session_state.sessions_before_long_break, step=1, format="%d"
                    )

        # 현재 세션 상태
        if st.session_state.is_study:
            current_remaining = st.session_state.remaining_study_seconds
            full_duration_seconds = st.session_state.study_duration * 60
            session_name = "공부"
            button_type = "primary"
        elif st.session_state.is_long_break:
            current_remaining = st.session_state.remaining_long_break_seconds
            full_duration_seconds = st.session_state.long_break_duration * 60
            session_name = "긴 휴식"
            button_type = "secondary"
        else:
            current_remaining = st.session_state.remaining_break_seconds
            full_duration_seconds = st.session_state.break_duration * 60
            session_name = "휴식"
            button_type = "secondary"

        if current_remaining > 0 and current_remaining < full_duration_seconds:
            minutes = current_remaining // 60
            seconds = current_remaining % 60
            resume_text = f"▶️ {session_name} {minutes}분 {seconds}초 마저 하기"

            with button_placeholder.container():
                col_reset, col_resume = st.columns(2)
                if col_reset.button("🔄 초기화", use_container_width=True, key='reset_timer_button'):
                    st.session_state.remaining_study_seconds = int(st.session_state.study_duration * 60)
                    st.session_state.remaining_break_seconds = int(st.session_state.break_duration * 60)
                    st.session_state.remaining_long_break_seconds = int(st.session_state.long_break_duration * 60)
                    st.session_state.is_study = True
                    st.session_state.is_long_break = False
                    st.session_state.current_cycle_count = 0
                    st.warning("타이머가 초기화되었습니다.")
                    st.rerun()
                if col_resume.button(resume_text, type="warning", use_container_width=True, key='resume_button'):
                    st.session_state.is_running = True
                    st.rerun()
        else:
            if st.session_state.is_study:
                btn_text = f"▶️ {st.session_state.study_duration}분 공부 시작"
                btn_key = 'start_study_button'
            elif st.session_state.is_long_break:
                btn_text = f"🛌 {st.session_state.long_break_duration}분 긴 휴식 시작"
                btn_key = 'start_long_break_button'
            else:
                btn_text = f"☕ {st.session_state.break_duration}분 휴식 시작"
                btn_key = 'start_break_button'

            if button_placeholder.button(btn_text, type=button_type, use_container_width=True, key=btn_key):
                st.session_state.is_running = True
                st.rerun()

    else:
        input_placeholder.empty()

        if button_placeholder.button("⏹️ 중지하기", use_container_width=True, key='stop_timer_button'):
            st.session_state.is_running = False
            st.warning("타이머가 중지되었습니다.")
            st.rerun()

        if st.session_state.is_study:
            run_timer(is_study_session=True)
        elif st.session_state.is_long_break:
            run_timer(is_study_session=False, is_long_break=True)
        else:
            run_timer(is_study_session=False, is_long_break=False)

# =====================================================
# 통계 탭
# =====================================================
with tab_stats:
    st.subheader("📊 나의 공부 통계")

    # 전체 통계
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 세션", f"{st.session_state.total_sessions}회")
    with col2:
        hours = st.session_state.total_minutes // 60
        mins = st.session_state.total_minutes % 60
        st.metric("총 공부 시간", f"{hours}시간 {mins}분")
    with col3:
        st.metric("완료 사이클", f"{st.session_state.completed_cycles}세트")
    with col4:
        st.metric("총 획득 코인", f"{st.session_state.total_coins_earned:,}원")

    st.divider()

    # 오늘 통계
    st.markdown("### 📅 오늘의 기록")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("오늘 완료 세션", f"{st.session_state.today_sessions}회")
    with col_t2:
        t_hours = st.session_state.today_minutes // 60
        t_mins = st.session_state.today_minutes % 60
        st.metric("오늘 공부 시간", f"{t_hours}시간 {t_mins}분")

    st.divider()

    # 최근 세션 로그
    st.markdown("### 📋 최근 세션 기록")
    if st.session_state.session_log:
        log_data = list(reversed(st.session_state.session_log[-10:]))
        for entry in log_data:
            st.markdown(f"- **{entry['time']}** — {entry['duration']}분 공부 완료")
    else:
        st.info("아직 완료한 세션이 없어요. 지금 시작해볼까요? 🚀")

    st.divider()

    # 일별 기록
    st.markdown("### 📆 일별 기록")
    if st.session_state.daily_history:
        for day, data in sorted(st.session_state.daily_history.items(), reverse=True)[:7]:
            h = data['minutes'] // 60
            m = data['minutes'] % 60
            bar_len = min(data['sessions'], 10)
            bar = "🟩" * bar_len + "⬜" * (10 - bar_len)
            st.markdown(f"**{day}** | {data['sessions']}세션 | {h}시간 {m}분  \n{bar}")
    else:
        st.info("아직 기록이 없습니다.")

# =====================================================
# 업적 탭
# =====================================================
with tab_achievements:
    st.subheader("🏆 업적")

    unlocked = st.session_state.unlocked_achievements
    total = len(ACHIEVEMENTS)
    done = len(unlocked)

    st.progress(done / total)
    st.markdown(f"**{done} / {total}** 업적 달성")
    st.divider()

    for key, ach in ACHIEVEMENTS.items():
        col_a, col_b = st.columns([4, 1])
        with col_a:
            if key in unlocked:
                st.markdown(f"✅ **{ach['name']}** — {ach['desc']}")
            else:
                st.markdown(f"🔒 ~~{ach['name']}~~ — {ach['desc']}")
        with col_b:
            reward_text = f"+{ach['reward']:,}원"
            if key in unlocked:
                st.success(reward_text)
            else:
                st.caption(reward_text)

# =====================================================
# 상점 탭
# =====================================================
with tab_shop:
    st.subheader("🛒 아이템 상점")
    st.caption(f"현재 잔액: **{st.session_state.coins:,}원**")

    st.markdown("### 🖼️ 테마 및 디자인")
    for item_key, item_info in THEME_STYLES.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            status_emoji = "✨" if st.session_state.active_theme == item_key else ""
            st.markdown(f"**{item_info['name']} {status_emoji}** — {item_info['price']:,}원")
            st.caption(item_info['effect'])
        with col2:
            buy_shop_logic(item_key, item_info)

    st.markdown("---")

    st.markdown("### 📢 알림 및 효과")
    for item_key, item_info in OTHER_ITEMS.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{item_info['name']}** — {item_info['price']:,}원")
            st.caption(item_info['effect'])
        with col2:
            buy_shop_logic(item_key, item_info)
