import random
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

# Zielbereiche je Schwierigkeitsgrad
target_ranges = {
    "leicht": (8, 12),
    "mittel": (11, 15),
    "schwer": (15, 19),
    "sehr schwer": (19, 22),
    "ultimativ": (23, 25),
}

# Hazard-Die Funktion
def roll_hazard_die():
    total = 0
    while True:
        r = random.randint(1, 6)
        total += r
        if r < 6:
            break
    return total

# Hauptfunktion zur Optimierung
def optimize_psi_use(total_dice, difficulty, required_kraftstufen):
    difficulty = difficulty.lower()
    if difficulty not in target_ranges:
        return {"error": "Ungültige Schwierigkeit. Erlaubt: leicht, mittel, schwer, sehr schwer, ultimativ."}

    base_min, base_max = target_ranges[difficulty]
    best_option = None
    best_success_rate = 0.0

    for num_rolled in range(1, total_dice - required_kraftstufen + 1):
        for zielbereich_erweiterung in range(0, total_dice - num_rolled - required_kraftstufen + 1):
            kraftstufen = total_dice - num_rolled - zielbereich_erweiterung
            if kraftstufen < required_kraftstufen:
                continue

            # Zielbereich für Anzeige und Berechnung
            min_target_raw = base_min - zielbereich_erweiterung
            max_target_raw = base_max + zielbereich_erweiterung
            min_target_calc = max(1, min_target_raw)
            max_target_calc = min(6 * num_rolled + 12, max_target_raw)  # +12 als grober Max-Puffer durch Hazard-Die

            if min_target_calc > max_target_calc:
                continue

            # Wahrscheinlichkeitsberechnung via Monte Carlo
            trials = 10000
            success_count = 0
            for _ in range(trials):
                rolls = [roll_hazard_die()] + [random.randint(1, 6) for _ in range(num_rolled - 1)]
                total_roll = sum(rolls)
                if min_target_calc <= total_roll <= max_target_calc:
                    success_count += 1
            success_rate = success_count / trials

            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_option = {
                    "würfel_gesamt": total_dice,
                    "würfel_werfen": num_rolled,
                    "zielbereich_erweitern": zielbereich_erweiterung,
                    "kraftstufen": kraftstufen,
                    "zielbereich": [min_target_raw, max_target_raw],
                    "erfolgswahrscheinlichkeit": round(success_rate * 100, 2)
                }

    return best_option or {"error": "Keine gültige Kombination gefunden."}

# Streamlit UI
st.set_page_config(page_title="NoReturn PSI-Optimierer", layout="centered")
st.markdown("""
    <style>
        .custom-card {
            background-color: #222;
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
            box-shadow: 0 0 10px rgba(255,255,255,0.1);
        }
        .custom-card h3 {
            margin-bottom: 0.25rem;
            font-size: 1rem;
            color: #aaa;
        }
        .custom-card p {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 NoReturn PSI-Optimierer")
st.markdown("""
<p style='font-size:18px;'>
Gib deine Parameter ein und erhalte die <b>beste Kombination</b> für das Wirken einer PSI-App.
</p>
""", unsafe_allow_html=True)

with st.form("psi_form"):
    col1, col2 = st.columns(2)
    with col1:
        total_dice = st.slider("Verfügbare Wü6", min_value=1, max_value=20, value=6)
        required_kraftstufen = st.slider("Gewünschte Kraftstufen", min_value=1, max_value=10, value=1)
    with col2:
        difficulty = st.selectbox(
            "Schwierigkeit der App",
            ["leicht", "mittel", "schwer", "sehr schwer", "ultimativ"]
        )
        st.markdown("""<small>Leicht: 8–12 | Mittel: 11–15 | Schwer: 15–19 | Sehr schwer: 19–22 | Ultimativ: 23–25</small>""", unsafe_allow_html=True)

    submitted = st.form_submit_button("🔍 Optimieren")

if submitted:
    result = optimize_psi_use(total_dice, difficulty, required_kraftstufen)
    if "error" in result:
        st.error(result["error"])
    else:
        st.success("Beste Kombination gefunden:")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='custom-card'><h3>🎲 Geworfene Würfel</h3><p>{result['würfel_werfen']}</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='custom-card'><h3>➕ Zielbereich erweitern</h3><p>{result['zielbereich_erweitern']}</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='custom-card'><h3>⚡ Kraftstufen</h3><p>{result['kraftstufen']}</p></div>", unsafe_allow_html=True)

        col4, col5 = st.columns(2)
        with col4:
            st.markdown(f"<div class='custom-card'><h3>🌟 Zielbereich</h3><p>{result['zielbereich'][0]} – {result['zielbereich'][1]}</p></div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div class='custom-card'><h3>✅ Erfolgswahrscheinlichkeit</h3><p>{result['erfolgswahrscheinlichkeit']}%</p></div>", unsafe_allow_html=True)
