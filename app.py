import streamlit as st
import pandas as pd
import random
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Wybór Imienia", layout="centered")

# --- CSS: STYLIZACJA (Poprawione centrowanie i wielkość) ---
st.markdown("""
    <style>
    /* 1. Globalne tło */
    .stApp {
        background-color: #FDFBF7;
        color: #333333;
    }
    
    /* 2. Karta imienia */
    .name-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 15px;
        padding: 15px 5px; /* Mniejszy padding góra/dół */
        text-align: center;
        margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .name-text {
        font-size: 26px; /* Jeszcze większe imię */
        font-weight: 800;
        color: #2c3e50;
        letter-spacing: 0.5px;
    }

    /* 3. CHECKBOX - CENTROWANIE I POWIĘKSZANIE (KLUCZOWA ZMIANA) */
    
    /* Wyśrodkowanie całego widgetu checkboxa w kolumnie */
    div[data-testid="stColumn"] div[data-testid="stCheckbox"] {
        display: flex;
        justify-content: center; /* Centruje w poziomie */
        align-items: center;     /* Centruje w pionie */
        width: 100%;
        margin-top: 5px;
        margin-bottom: 20px;     /* Odstęp od kolejnego wiersza */
    }

    /* Powiększenie samego kwadracika */
    div[data-baseweb="checkbox"] div {
        transform: scale(1.5);   /* Duży kwadrat */
        margin-right: 15px;      /* Odstęp od tekstu */
        border-color: #A69065 !important;
    }
    
    /* Powiększenie i stylizacja tekstu "Podoba mi się!" */
    div[data-baseweb="checkbox"] label p {
        font-size: 18px !important;  /* Duża czcionka */
        font-weight: 700 !important; /* Pogrubienie */
        color: #5D9C59 !important;   /* Zielony odcień */
    }
    
    /* 4. Przyciski */
    .stButton>button[kind="primary"] {
        width: 100%;
        height: 3.5em;
        background-color: #A69065;
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(166, 144, 101, 0.4);
        margin-top: 20px;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #8C7853;
    }
    
    .stButton>button {
        width: 100%;
        height: 3.5em;
        border-radius: 12px;
        border: 2px solid #E0E0E0;
        background-color: white;
        color: #333;
    }

    /* 5. Link w wynikach */
    .wiki-link {
        text-decoration: none;
        color: #0068C9;
        font-weight: bold;
        padding: 5px 10px;
        border: 1px solid #dbeefc;
        border-radius: 15px;
        background-color: #f0f7ff;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

# --- ŁADOWANIE DANYCH ---
@st.cache_data
def load_data():
    if not os.path.exists('imiona.csv'):
        return None
    try:
        df = pd.read_csv('imiona.csv')
        return df
    except Exception as e:
        st.error(f"Błąd pliku CSV: {e}")
        return None

# --- STAN APLIKACJI ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'selected_gender' not in st.session_state: st.session_state.selected_gender = None
if 'candidate_list' not in st.session_state: st.session_state.candidate_list = []
if 'kept_names' not in st.session_state: st.session_state.kept_names = []
if 'current_index' not in st.session_state: st.session_state.current_index = 0
if 'round_winners' not in st.session_state: st.session_state.round_winners = []

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =========================================================
# EKRAN 1: PŁEĆ
# =========================================================
if st.session_state.step == 1:
    st.title("Wybór Imienia 👶")
    st.markdown("Wybierz płeć dziecka, aby rozpocząć poszukiwania.")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Chłopiec 👦"):
            st.session_state.selected_gender = 'male'
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Dziewczynka 👧"):
            st.session_state.selected_gender = 'female'
            st.session_state.step = 2
            st.rerun()

# =========================================================
# EKRAN 2: ZAKRES
# =========================================================
elif st.session_state.step == 2:
    st.title("Wybierz zakres")
    st.write("Ile najpopularniejszych imion z Polski (2023/24) chcesz przejrzeć?")
    
    mapping = {"Top 30": 30, "Top 50": 50, "Top 100": 100, "Top 200": 200}
    choice = st.selectbox("Liczba imion:", list(mapping.keys()), index=1)
    limit = mapping[choice]
    
    if st.button("Rozpocznij selekcję", type="primary"):
        df = load_data()
        if df is None:
            st.error("Brak pliku imiona.csv!")
        else:
            filtered = df[df['Plec'] == st.session_state.selected_gender].copy()
            filtered = filtered.sort_values(by='Liczba', ascending=False)
            top_selection = filtered.head(limit)
            
            data_list = top_selection[['Imie', 'Wikipedia_Url']].to_dict('records')
            random.shuffle(data_list)
            
            st.session_state.candidate_list = data_list
            st.session_state.step = 3
            st.session_state.current_index = 0
            st.session_state.kept_names = []
            st.rerun()

# =========================================================
# EKRAN 3 i 4: SELEKCJA (PACZKI PO 10)
# =========================================================
elif st.session_state.step in [3, 4]:
    if st.session_state.step == 3:
        header = "Runda 1: Szybki wybór"
        desc = "Zaznacz imiona, które Ci się podobają. Te niezaznaczone odpadną."
    else:
        header = "Runda 2: Weryfikacja"
        desc = "Zostaw tylko te, które bierzesz pod uwagę na 100%."

    st.title(header)
    st.info(desc)
    
    BATCH_SIZE = 10
    total = len(st.session_state.candidate_list)
    idx = st.session_state.current_index
    
    prog = min(idx / total, 1.0) if total > 0 else 1.0
    st.progress(prog)
    st.caption(f"Wyświetlono {min(idx + BATCH_SIZE, total)} z {total}")

    batch = st.session_state.candidate_list[idx : idx + BATCH_SIZE]
    
    if not batch:
        if st.session_state.step == 3:
            if not st.session_state.kept_names:
                st.warning("Nic nie wybrałeś! Spróbuj ponownie.")
                if st.button("Restart"): reset_app()
            else:
                st.session_state.candidate_list = st.session_state.kept_names
                st.session_state.kept_names = []
                st.session_state.current_index = 0
                st.session_state.step = 4
                st.rerun()
        else:
            final = st.session_state.kept_names
            if len(final) < 2:
                st.session_state.candidate_list = final
                st.session_state.step = 6
                st.rerun()
            else:
                random.shuffle(final)
                st.session_state.candidate_list = final
                st.session_state.round_winners = []
                st.session_state.step = 5
                st.rerun()
        st.stop()

    with st.form(key=f"batch_{st.session_state.step}_{idx}"):
        cols = st.columns(2)
        
        for i, item in enumerate(batch):
            col = cols[i % 2]
            with col:
                # Karta imienia (tylko imię)
                st.markdown(f"""
                <div class='name-card'>
                    <div class='name-text'>{item['Imie']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Checkbox - tekst "Podoba mi się" jest teraz częścią widgetu
                # CSS wyżej dba o to, by był duży i wyśrodkowany
                st.checkbox(f"Podoba mi się!", key=f"chk_{item['Imie']}")
        
        st.write("---")
        if st.form_submit_button("Zatwierdź i pokaż kolejne ➡", type="primary"):
            for item in batch:
                if st.session_state.get(f"chk_{item['Imie']}", False):
                    st.session_state.kept_names.append(item)
            st.session_state.current_index += BATCH_SIZE
            st.rerun()

# =========================================================
# EKRAN 5: TURNIEJ
# =========================================================
elif st.session_state.step == 5:
    st.title("⚔️ Finałowy Turniej")
    st.markdown("Wybierz lepsze imię z pary.")
    
    candidates = st.session_state.candidate_list
    winners = st.session_state.round_winners
    
    if len(candidates) == 0:
        if len(winners) + len(candidates) <= 4:
            st.session_state.candidate_list = winners
            st.session_state.step = 6
            st.rerun()
        else:
            random.shuffle(winners)
            st.session_state.candidate_list = winners
            st.session_state.round_winners = []
            st.rerun()
            
    if len(candidates) == 1:
        st.session_state.round_winners.append(candidates[0])
        st.session_state.candidate_list = []
        st.rerun()

    f1 = candidates[0]
    f2 = candidates[1]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='name-card'><div class='name-text'>{f1['Imie']}</div></div>", unsafe_allow_html=True)
        if st.button("👈 Wybieram to", key="btn1", type="primary"):
            st.session_state.round_winners.append(f1)
            st.session_state.candidate_list = candidates[2:]
            st.rerun()
    with c2:
        st.markdown(f"<div class='name-card'><div class='name-text'>{f2['Imie']}</div></div>", unsafe_allow_html=True)
        if st.button("Wybieram to 👉", key="btn2", type="primary"):
            st.session_state.round_winners.append(f2)
            st.session_state.candidate_list = candidates[2:]
            st.rerun()
    
    st.caption(f"Pozostało par w tej rundzie: {len(candidates)//2}")

# =========================================================
# EKRAN 6: WYNIKI
# =========================================================
elif st.session_state.step == 6:
    st.balloons()
    st.title("🎉 Wybrane Imiona")
    
    finalists = st.session_state.candidate_list
    
    for item in finalists:
        st.markdown(f"""
        <div class="name-card" style="flex-direction: row; justify-content: space-between; padding: 20px;">
            <div class="name-text" style="margin:0;">{item['Imie']}</div>
            <a href="{item['Wikipedia_Url']}" target="_blank" class="wiki-link">Wikipedia 📖</a>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Zacznij od nowa"):
        reset_app()
