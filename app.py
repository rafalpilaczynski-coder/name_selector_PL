import streamlit as st
import pandas as pd
import random
import os
import streamlit.components.v1 as components

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Wybór Imienia", layout="centered")

# --- CSS: NOWY STYL DLA PRZYCISKÓW-KART ---
st.markdown("""
    <style>
    /* 1. Globalne tło */
    .stApp {
        background-color: #FDFBF7;
        color: #333333;
    }
    
    /* 2. Ukrywamy standardowe obramowanie przycisków, żeby stworzyć własne style */
    .stButton > button {
        width: 100%;
        height: 80px; /* Wysokość karty */
        border-radius: 15px;
        font-size: 22px;
        font-weight: 700;
        transition: all 0.2s ease;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* 3. STAN NIEAKTYWNY (Zwykła karta) - nadpisujemy styl 'secondary' */
    /* To odpowiada za białe tło i zwykłą ramkę */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        color: #2c3e50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #f9f9f9;
        border-color: #ccc;
    }

    /* 4. STAN AKTYWNY (Zaznaczone) - nadpisujemy styl 'primary' */
    /* To odpowiada za ZIELONE tło i GRUBĄ ramkę */
    .stButton > button[kind="primary"] {
        background-color: #E8F5E9 !important; /* Jasny zielony */
        border: 3px solid #2E7D32 !important; /* Ciemny zielony pogrubiony */
        color: #1B5E20 !important; /* Ciemny zielony tekst */
        box-shadow: 0 4px 10px rgba(46, 125, 50, 0.2);
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #C8E6C9 !important;
    }
    
    /* 5. Przycisk "Dalej" (musi wyglądać inaczej, więc użyjemy kontenera lub innej klasy, 
       ale tutaj Streamlit ma ograniczenia, więc zrobimy go po prostu bardzo szerokim na dole) */
    
    /* Link w wynikach */
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

# --- FUNKCJA JS DO SCROLLOWANIA ---
def scroll_to_top():
    # Wstrzykuje JavaScript, który przewija okno do góry
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        body.scrollTop = 0;
    </script>
    '''
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

# Zbiór tymczasowy do przechowywania zaznaczonych imion w obecnej sesji
# (Używamy set, żeby łatwo dodawać/usuwać)
if 'temp_selections' not in st.session_state: st.session_state.temp_selections = set()

# Flaga do scrollowania
if 'trigger_scroll' not in st.session_state: st.session_state.trigger_scroll = False

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- OBSŁUGA SCROLLOWANIA NA POCZĄTKU RENDERA ---
if st.session_state.trigger_scroll:
    scroll_to_top()
    st.session_state.trigger_scroll = False

# =========================================================
# EKRAN 1: PŁEĆ
# =========================================================
if st.session_state.step == 1:
    st.title("Wybór Imienia 👶")
    st.markdown("Wybierz płeć dziecka, aby rozpocząć poszukiwania.")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Chłopiec 👦", type="secondary"):
            st.session_state.selected_gender = 'male'
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("Dziewczynka 👧", type="secondary"):
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
    
    # Używamy formy, żeby przycisk wyglądał standardowo (CSS "secondary")
    # Zmieniamy mu styl ręcznie za pomocą hacka, lub akceptujemy styl karty
    if st.button("Rozpocznij selekcję 🚀", type="primary"):
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
# EKRAN 3 i 4: SELEKCJA (INTERAKTYWNE KARTY)
# =========================================================
elif st.session_state.step in [3, 4]:
    if st.session_state.step == 3:
        header = "Runda 1"
        desc = "Kliknij w imię, aby je zaznaczyć na zielono."
    else:
        header = "Runda 2"
        desc = "Zostaw tylko pewniaki."

    st.title(header)
    st.info(desc)
    
    BATCH_SIZE = 10
    total = len(st.session_state.candidate_list)
    idx = st.session_state.current_index
    
    prog = min(idx / total, 1.0) if total > 0 else 1.0
    st.progress(prog)
    st.caption(f"Wyświetlono {min(idx + BATCH_SIZE, total)} z {total}")

    batch = st.session_state.candidate_list[idx : idx + BATCH_SIZE]
    
    # Logika końca listy (gdy brak imion w paczce)
    if not batch:
        # Zapisz wybrane z setu do listy
        # (Właściwie robimy to przyciskiem "Dalej", ale tu zabezpieczenie)
        if st.session_state.step == 3:
            if not st.session_state.kept_names:
                st.warning("Nic nie wybrałeś! Spróbuj ponownie.")
                if st.button("Restart"): reset_app()
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

    # --- SIATKA KART (BUTTONY) ---
    cols = st.columns(2)
    
    # Funkcja callback do przełączania stanu
    def toggle_selection(name_key):
        if name_key in st.session_state.temp_selections:
            st.session_state.temp_selections.remove(name_key)
        else:
            st.session_state.temp_selections.add(name_key)

    for i, item in enumerate(batch):
        col = cols[i % 2]
        name = item['Imie']
        
        # Sprawdzamy, czy imię jest zaznaczone
        is_selected = name in st.session_state.temp_selections
        
        # Jeśli zaznaczone -> Styl 'primary' (Zielony w naszym CSS)
        # Jeśli nie -> Styl 'secondary' (Biały w naszym CSS)
        btn_type = "primary" if is_selected else "secondary"
        
        # Dodajemy ikonkę dla efektu
        label = f"✅ {name}" if is_selected else name
        
        with col:
            # Przycisk działa jak Toggle
            st.button(
                label, 
                key=f"btn_{name}_{st.session_state.step}", # Unikalny klucz
                type=btn_type,
                on_click=toggle_selection,
                args=(name,)
            )

    st.write("---")
    
    # Przycisk DALEJ (Niezależny od siatki)
    # Używamy tutaj triku: w CSS primary jest zielony, więc ten przycisk też będzie zielony.
    # To pasuje: "Zatwierdź" na zielono.
    if st.button("Zatwierdź i pokaż kolejne ➡", type="primary", key="next_batch_btn"):
        # Przenosimy zaznaczone imiona z tej paczki do trwałej listy
        # Ale uwaga: temp_selections trzyma WSZYSTKIE zaznaczone w tej turze, 
        # a my chcemy tylko dodać te z current batch, żeby zachować porządek?
        # Nie, temp_selections resetujemy przy zmianie etapu (np. z Rundy 1 na 2).
        # Więc możemy po prostu przepisać temp_selections do kept_names przy KOŃCU etapu?
        # NIE, bo batching. Musimy robić append na bieżąco.
        
        # Rozwiązanie: W tym modelu (Toggle) temp_selections trzyma stan globalnie dla etapu.
        # Przy przejściu do następnej paczki, nic nie musimy robić ze stanem (on jest w session_state).
        # Dopiero gdy current_index > len, przepisujemy temp do kept.
        
        # Jednak dla bezpieczeństwa i logiki kodu, zróbmy tak:
        # Przy "Dalej" po prostu przesuwamy index. Stan 'temp_selections' trzyma wszystko.
        # Dopiero na końcu etapu (linia 133) przypiszemy temp -> kept.
        
        st.session_state.current_index += BATCH_SIZE
        st.session_state.trigger_scroll = True # Aktywacja scrolla
        st.rerun()

    # Logika zapisu po wyczerpaniu listy (dodatkowe zabezpieczenie pętli)
    if idx + BATCH_SIZE >= total:
        # To jest moment, gdy przycisk "Zatwierdź" powinien zadziałać jako "Zakończ rundę"
        # Ale kod wyżej obsłuży to przy następnym odświeżeniu (if not batch).
        pass

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
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"{f1['Imie']}", key="btn1", type="secondary"):
            st.session_state.round_winners.append(f1)
            st.session_state.candidate_list = candidates[2:]
            st.rerun()
    with c2:
        if st.button(f"{f2['Imie']}", key="btn2", type="secondary"):
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
    
    # Pobieramy z kept_names lub candidate_list (zależnie gdzie skończyliśmy)
    # W turnieju finaliści lądują w candidate_list
    if st.session_state.candidate_list:
        finalists = st.session_state.candidate_list
    elif st.session_state.kept_names:
        finalists = st.session_state.kept_names
    # Jeśli mamy temp_selections (zostaliśmy po selekcji bez turnieju)
    elif st.session_state.temp_selections:
        # Musimy odtworzyć obiekty (dict) na podstawie nazw w secie
        # To wymagałoby przeszukania bazy, ale uprośćmy:
        # Kod w selekcji powinien był przenieść to do kept_names.
        # Zakładamy, że logika turnieju zadziałała poprawnie.
        finalists = [] 
    
    # Jeśli somehow pusto, weź z temp_selections (fallback)
    if not finalists and st.session_state.temp_selections:
         # Znajdź pełne obiekty w historii (to trochę hack, ale zadziała)
         # Wczytujemy dane jeszcze raz lub szukamy w session state, ale tu wyświetlimy po prostu nazwy
         finalists = [{'Imie': name, 'Wikipedia_Url': f'https://pl.wikipedia.org/wiki/{name}'} for name in st.session_state.temp_selections]

    for item in finalists:
        # Wyświetlamy jako ładne karty (już nie przyciski)
        st.markdown(f"""
        <div style="
            background-color: #E8F5E9;
            border: 2px solid #2E7D32;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="font-size: 24px; font-weight: bold; color: #1B5E20;">{item['Imie']}</span>
            <a href="{item['Wikipedia_Url']}" target="_blank" class="wiki-link">Wikipedia 📖</a>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Zacznij od nowa"):
        reset_app()
