import streamlit as st
import pandas as pd
import random
import os

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Wybór Imienia", layout="centered")

# --- CSS: KOLORYSTYKA KREMOWA I WYGLĄD KART ---
st.markdown("""
    <style>
    /* Główne tło */
    .stApp {
        background-color: #FDFBF7; /* Ecru / Kremowy */
        color: #4A4A4A;
    }
    /* Nagłówki */
    h1, h2, h3 {
        color: #5D5D5D;
        font-family: 'Helvetica', sans-serif;
    }
    /* Karta imienia */
    .name-card {
        padding: 15px;
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 5px;
        font-size: 22px;
        font-weight: 600;
        color: #2c3e50;
    }
    /* Stylizacja przycisków standardowych */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #F0EBE0;
        color: #333;
        border: none;
    }
    .stButton>button:hover {
        background-color: #E6DFD0;
        color: #000;
    }
    /* Przyciski turniejowe (primary) */
    .stButton>button[kind="primary"] {
        background-color: #D4C5A5;
        color: white;
        font-size: 1.2em;
    }
    /* Link do wikipedii w raporcie */
    .wiki-link {
        text-decoration: none;
        color: #5C8D89; 
        font-size: 0.9em;
        font-weight: normal;
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

# --- ZARZĄDZANIE STANEM (SESSION STATE) ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'selected_gender' not in st.session_state:
    st.session_state.selected_gender = None
if 'candidate_list' not in st.session_state:
    # Lista słowników: [{'Imie': 'Jan', 'Wikipedia_Url': '...'}]
    st.session_state.candidate_list = []
if 'kept_names' not in st.session_state:
    st.session_state.kept_names = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'round_winners' not in st.session_state:
    st.session_state.round_winners = []

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =========================================================
# EKRAN 1: WYBÓR PŁCI
# =========================================================
if st.session_state.step == 1:
    st.title("Wybór Imienia dla Dziecka 👶")
    st.markdown("Witaj! Przejdziemy przez kilka etapów selekcji, aby znaleźć idealne imię.")
    st.write("---")
    st.subheader("Kogo się spodziewacie?")
    
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
# EKRAN 2: WYBÓR LICZBY IMION (TOP LISTA)
# =========================================================
elif st.session_state.step == 2:
    st.title("Baza Imion")
    st.write("Wybierz, jak szeroko chcesz szukać. Imiona pochodzą ze statystyk GUS (ostatnie 5 lat).")
    
    mapping = {"Top 30": 30, "Top 50": 50, "Top 100": 100, "Top 200": 200}
    choice = st.selectbox("Zakres poszukiwań:", list(mapping.keys()), index=1)
    limit = mapping[choice]
    
    if st.button("Rozpocznij selekcję"):
        df = load_data()
        if df is None:
            st.error("Nie znaleziono pliku imiona.csv! Upewnij się, że jest w repozytorium.")
        else:
            # Filtrowanie i sortowanie
            filtered = df[df['Plec'] == st.session_state.selected_gender].copy()
            filtered = filtered.sort_values(by='Liczba', ascending=False)
            
            # Pobranie top N i konwersja do listy słowników
            top_selection = filtered.head(limit)
            
            if top_selection.empty:
                st.warning("Brak danych dla wybranych kryteriów.")
            else:
                data_list = top_selection[['Imie', 'Wikipedia_Url']].to_dict('records')
                random.shuffle(data_list) # Mieszamy, żeby nie sugerować się rankingiem
                
                st.session_state.candidate_list = data_list
                st.session_state.step = 3
                st.session_state.current_index = 0
                st.session_state.kept_names = []
                st.rerun()

# =========================================================
# EKRAN 3 i 4: SELEKCJA (KCIUK W GÓRĘ / DÓŁ)
# =========================================================
elif st.session_state.step in [3, 4]:
    # Konfiguracja nagłówków zależnie od etapu
    if st.session_state.step == 3:
        header = "Runda 1: Wstępna Selekcja"
        desc = "Zaznacz 'Tak' (👍) przy imionach, które Ci się podobają. Reszta zostanie odrzucona."
    else:
        header = "Runda 2: Zawężanie Listy"
        desc = "Spośród wybranych imion, odrzuć te, do których masz wątpliwości."

    st.title(header)
    st.info(desc)
    
    # Pasek postępu
    total = len(st.session_state.candidate_list)
    current = st.session_state.current_index
    progress = min(current / total, 1.0) if total > 0 else 1.0
    st.progress(progress)
    
    # Pobieranie paczki 10 imion
    BATCH_SIZE = 10
    end_index = min(current + BATCH_SIZE, total)
    batch = st.session_state.candidate_list[current:end_index]
    
    # --- Logika przejścia dalej, gdy lista się skończy ---
    if not batch:
        if st.session_state.step == 3:
            # Koniec 1. rundy -> idź do 2. rundy
            if not st.session_state.kept_names:
                st.warning("Nie wybrałeś żadnego imienia! Spróbuj ponownie.")
                if st.button("Zrestartuj"): reset_app()
            else:
                st.session_state.candidate_list = st.session_state.kept_names
                st.session_state.kept_names = []
                st.session_state.current_index = 0
                st.session_state.step = 4
                st.rerun()
        else:
            # Koniec 2. rundy -> idź do turnieju
            final_pool = st.session_state.kept_names
            if len(final_pool) < 2:
                # Jeśli zostało za mało imion na turniej, idź od razu do wyników
                st.session_state.candidate_list = final_pool
                st.session_state.step = 6
                st.rerun()
            else:
                # Przygotowanie do turnieju
                random.shuffle(final_pool)
                st.session_state.candidate_list = final_pool
                st.session_state.round_winners = []
                st.session_state.step = 5
                st.rerun()
        st.stop() # Zatrzymujemy wykonanie reszty kodu w tym przebiegu

    # Formularz oceny
    with st.form(key=f"selection_form_{st.session_state.step}_{current}"):
        st.write(f"Imiona {current + 1} - {end_index} z {total}")
        
        # Słownik na decyzje użytkownika
        selections = {}
        
        for item in batch:
            name = item['Imie']
            c1, c2, c3 = st.columns([0.2, 0.6, 0.2])
            
            # Lewa kolumna: Czerwony kciuk (wizualny)
            with c1:
                st.markdown("<div style='text-align: right; font-size: 20px; padding-top: 15px;'>🟥</div>", unsafe_allow_html=True)
            
            # Środek: Karta imienia
            with c2:
                st.markdown(f"<div class='name-card'>{name}</div>", unsafe_allow_html=True)
            
            # Prawa kolumna: Checkbox (Kciuk w górę - Zielony)
            with c3:
                # Checkbox działa jako "Zatwierdź" / "Tak"
                is_selected = st.checkbox("👍", key=f"sel_{name}")
                selections[name] = is_selected

        st.write("---")
        submit = st.form_submit_button("Zatwierdź wybory")
        
        if submit:
            for item in batch:
                if selections[item['Imie']]:
                    st.session_state.kept_names.append(item)
            
            st.session_state.current_index += BATCH_SIZE
            st.rerun()

# =========================================================
# EKRAN 5: TURNIEJ (WALKI IMION)
# =========================================================
elif st.session_state.step == 5:
    st.title("⚔️ Turniej Imion")
    st.markdown("Wybierz lepsze imię z pary. Walczymy, aż zostaną 3-4 najlepsze.")
    
    candidates = st.session_state.candidate_list
    winners = st.session_state.round_winners
    
    # Sprawdzenie warunku końca całej gry (zostało <= 4 imion łącznie)
    total_remaining = len(candidates) + len(winners)
    
    if len(candidates) == 0:
        # Koniec rundy
        if total_remaining <= 4:
            # Mamy finalistów
            st.session_state.candidate_list = winners
            st.session_state.step = 6
            st.rerun()
        else:
            # Przejście do kolejnej rundy turnieju
            random.shuffle(winners)
            st.session_state.candidate_list = winners
            st.session_state.round_winners = []
            st.rerun()
            
    # Obsługa "wolnego losu" (jeśli została nieparzysta liczba)
    if len(candidates) == 1:
        # Ostatnie imię przechodzi automatycznie do zwycięzców rundy
        lucky_one = candidates[0]
        st.session_state.round_winners.append(lucky_one)
        st.session_state.candidate_list = [] # Pusta lista wymusi logikę końca rundy w następnym odświeżeniu
        st.rerun()

    # Walka: Wybierz dwa pierwsze imiona
    fighter_1 = candidates[0]
    fighter_2 = candidates[1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<div class='name-card' style='height: 100px; display: flex; align-items: center; justify-content: center;'>{fighter_1['Imie']}</div>", unsafe_allow_html=True)
        if st.button("Wybieram to 👈", key="btn1", type="primary"):
            st.session_state.round_winners.append(fighter_1)
            st.session_state.candidate_list = candidates[2:]
            st.rerun()
            
    with col2:
        st.markdown(f"<div class='name-card' style='height: 100px; display: flex; align-items: center; justify-content: center;'>{fighter_2['Imie']}</div>", unsafe_allow_html=True)
        if st.button("Wybieram to 👉", key="btn2", type="primary"):
            st.session_state.round_winners.append(fighter_2)
            st.session_state.candidate_list = candidates[2:]
            st.rerun()

    st.write(f"Pozostało par w tej rundzie: {len(candidates)//2}")

# =========================================================
# EKRAN 6: RAPORT KOŃCOWY
# =========================================================
elif st.session_state.step == 6:
    st.balloons()
    st.title("🎉 Twoja Lista Top Imion")
    st.markdown("Oto imiona, które przetrwały wszystkie etapy selekcji:")
    
    finalists = st.session_state.candidate_list
    
    for item in finalists:
        name = item['Imie']
        url = item['Wikipedia_Url']
        
        st.markdown(f"""
        <div class="name-card" style="text-align: left; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 24px;">{name}</span>
            <a href="{url}" target="_blank" class="wiki-link">
                📖 Zobacz opis
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    if st.button("Rozpocznij od nowa"):
        reset_app()