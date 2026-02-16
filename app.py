import streamlit as st
import pandas as pd
import random
import os
import streamlit.components.v1 as components
import time

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Wybór Imienia", layout="centered")

# --- CSS: STYLIZACJA ---
st.markdown("""
    <style>
    /* 1. Globalne tło */
    .stApp {
        background-color: #FDFBF7;
        color: #333333;
    }
    
    /* 2. Stylizacja przycisków (KARTY IMION) */
    /* Nadpisujemy domyślne style Streamlita, żeby przyciski były wyższe */
    .stButton > button {
        height: 70px !important; /* Wymuszona wysokość */
        border-radius: 12px !important;
        font-size: 24px !important; 
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        /* WAŻNE: width jest teraz kontrolowane przez parametr Pythona, ale dla pewności: */
        width: 100%; 
    }

    /* 3. STAN NIEAKTYWNY (Biały) */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        color: #4A4A4A !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #FAFAFA !important;
        border-color: #D0D0D0 !important;
    }

    /* 4. STAN AKTYWNY (Zielony - Zaznaczony) */
    .stButton > button[kind="primary"] {
        background-color: #E8F5E9 !important;
        border: 3px solid #2E7D32 !important; /* Grubsza ramka */
        color: #1B5E20 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #C8E6C9 !important;
    }

    /* 5. Przycisk nawigacji (DALEJ) */
    div[data-testid="stForm"] .stButton > button {
        background-color: #A69065 !important;
        color: white !important;
        border: none !important;
        height: 60px !important;
        margin-top: 15px !important;
    }
    
    /* Link w wynikach */
    .wiki-link {
        text-decoration: none;
        color: #0068C9;
        font-weight: bold;
        padding: 8px 15px;
        border: 1px solid #dbeefc;
        border-radius: 15px;
        background-color: #f0f7ff;
        font-size: 1rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNKCJA JS DO SCROLLOWANIA ---
def scroll_to_top():
    # Timestamp wymusza odświeżenie skryptu
    timestamp = int(time.time() * 1000)
    js = f"""
    <script>
        var doc = window.parent.document;
        // Próbujemy przewinąć różne kontenery
        var targets = doc.querySelectorAll('.stApp, .main, .block-container');
        targets.forEach(function(target) {{
            target.scrollTop = 0;
        }});
        // Fallback
        window.scrollTo(0, 0);
    </script>
    <div style="display:none;">{timestamp}</div>
    """
    components.html(js, height=0)

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
if 'temp_selections' not in st.session_state: st.session_state.temp_selections = set()
if 'trigger_scroll' not in st.session_state: st.session_state.trigger_scroll = False

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- OBSŁUGA SCROLLA ---
if st.session_state.trigger_scroll:
    scroll_to_top()
    st.session_state.trigger_scroll = False

# =========================================================
# EKRAN 1: PŁEĆ
# =========================================================
if st.session_state.step == 1:
    st.title("Wybór Imienia 👶")
    st.markdown("Wybierz płeć dziecka:")
    st.write("---")
    
    # use_container_width=True -> TO JEST KLUCZ DO SUKCESU
    if st.button("Chłopiec 👦", type="secondary", use_container_width=True):
        st.session_state.selected_gender = 'male'
        st.session_state.step = 2
        st.rerun()
        
    if st.button("Dziewczynka 👧", type="secondary", use_container_width=True):
        st.session_state.selected_gender = 'female'
        st.session_state.step = 2
        st.rerun()

# =========================================================
# EKRAN 2: ZAKRES
# =========================================================
elif st.session_state.step == 2:
    st.title("Zakres poszukiwań")
    st.write("Ile imion chcesz przejrzeć?")
    
    mapping = {"Top 30": 30, "Top 50": 50, "Top 100": 100, "Top 200": 200}
    choice = st.selectbox("Liczba imion:", list(mapping.keys()), index=1)
    limit = mapping[choice]
    
    st.write("") 
    
    if st.button("Rozpocznij 🚀", type="primary", use_container_width=True):
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
            st.session_state.temp_selections = set()
            st.rerun()

# =========================================================
# EKRAN 3 i 4: SELEKCJA (LISTA)
# =========================================================
elif st.session_state.step in [3, 4]:
    if st.session_state.step == 3:
        header = "Runda 1"
        desc = "Kliknij imiona, które Ci się podobają."
    else:
        header = "Runda 2"
        desc = "Zostaw tylko te najlepsze."

    st.title(header)
    st.caption(desc)
    
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
                st.warning("Nic nie wybrano! Restart.")
                if st.button("Restart", use_container_width=True): reset_app()
            else:
                st.session_state.candidate_list = st.session_state.kept_names
                st.session_state.kept_names = []
                st.session_state.temp_selections = set()
                st.session_state.current_index = 0
                st.session_state.step = 4
                st.session_state.trigger_scroll = True
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

    def toggle_selection(name_key):
        if name_key in st.session_state.temp_selections:
            st.session_state.temp_selections.remove(name_key)
        else:
            st.session_state.temp_selections.add(name_key)

    # Generowanie przycisków
    for item in batch:
        name = item['Imie']
        is_selected = name in st.session_state.temp_selections
        
        btn_type = "primary" if is_selected else "secondary"
        label = f"✅  {name}" if is_selected else name
        
        # use_container_width=True ROZCIĄGA PRZYCISK NA MAXA
        st.button(
            label, 
            key=f"btn_{name}_{st.session_state.step}", 
            type=btn_type,
            on_click=toggle_selection,
            args=(name,),
            use_container_width=True
        )

    st.write("")
    
    if st.button("Zatwierdź i pokaż kolejne ➡", type="primary", key="next_batch_btn", use_container_width=True):
        st.session_state.kept_names = [
            item for item in st.session_state.candidate_list 
            if item['Imie'] in st.session_state.temp_selections
        ]
        
        st.session_state.current_index += BATCH_SIZE
        st.session_state.trigger_scroll = True
        st.rerun()

# =========================================================
# EKRAN 5: TURNIEJ
# =========================================================
elif st.session_state.step == 5:
    st.title("⚔️ Finałowy Turniej")
    
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
    
    st.write("Które wolisz?")
    
    # Tutaj też full width
    if st.button(f"{f1['Imie']}", key="btn1", type="secondary", use_container_width=True):
        st.session_state.round_winners.append(f1)
        st.session_state.candidate_list = candidates[2:]
        st.rerun()
        
    st.markdown("<div style='text-align: center; font-weight:bold; margin: 10px 0; font-size: 1.2em;'>VS</div>", unsafe_allow_html=True)

    if st.button(f"{f2['Imie']}", key="btn2", type="secondary", use_container_width=True):
        st.session_state.round_winners.append(f2)
        st.session_state.candidate_list = candidates[2:]
        st.rerun()
    
    st.caption(f"Pozostało par: {len(candidates)//2}")

# =========================================================
# EKRAN 6: WYNIKI
# =========================================================
elif st.session_state.step == 6:
    st.balloons()
    st.title("🎉 Wybrane Imiona")
    
    if st.session_state.candidate_list:
        finalists = st.session_state.candidate_list
    elif st.session_state.kept_names:
        finalists = st.session_state.kept_names
    else:
        names_set = st.session_state.temp_selections
        finalists = []
        for n in names_set:
            finalists.append({'Imie': n, 'Wikipedia_Url': f'https://pl.wikipedia.org/wiki/{n}'})

    for item in finalists:
        st.markdown(f"""
        <div style="
            background-color: #E8F5E9;
            border: 2px solid #2E7D32;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        ">
            <span style="font-size: 22px; font-weight: bold; color: #1B5E20;">{item['Imie']}</span>
            <a href="{item['Wikipedia_Url']}" target="_blank" class="wiki-link">Wiki</a>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Zacznij od nowa", type="secondary", use_container_width=True):
        reset_app()
