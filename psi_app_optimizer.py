import itertools
import math
import random
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards

# Zielbereiche je Schwierigkeitsgrad
target_ranges = {
    "leicht": (8, 12),
    "mittel": (11, 15),
    "schwer": (15, 19),
    "ultimativ": (23, 25),
}

def optimize_psi_use(total_dice, difficulty, required_kraftstufen):
    difficulty = difficulty.lower()
    if difficulty not in target_ranges:
        return {"error": "Ungültige Schwierigkeit. Erlaubt: leicht, mittel, schwer, ultimativ."}

    base_min, base_max = target_ranges[difficulty]
    best_option = None
    best_success_rate = 0.0

    for num_rolled in range(1, total_dice - required_kraftstufen + 1):
        for zielbereich_erweiterung in range(0, total_dice - num_rolled - required_kraftstufen + 1):
            kraftstufen = total_dice - num_rolled - zielbereich_erweiterung
            if kraftstufen < required_kraftstufen:
                continue

            min_target = base_min - zielbereich_erweiterung
            max_target = base_max + zielbereich_erweiterung
            min_target = max(1, min_target)
            max_target = min(6 * num_rolled, max_target)

            if num_rolled > 8:
                trials = 100000
                success_count = 0
                for _ in range(trials):
                    roll = sum(random.randint(1, 6) for _ in range(num_rolled))
                    if min_target <= roll <= max_target:
                        success_count += 1
                success_rate = success_count / trials
            else:
                outcomes = itertools.product(range(1, 7), repeat=num_rolled)
                total = 0
                success = 0
                for outcome in outcomes:
                    total += 1
                    if min_target <= sum(outcome) <= max_target:
                        success += 1
                success_rate = success / total if total > 0 else 0

            if success_rate > best_success_rate:
                best_success_rate = success_rate
                best_option = {
                    "würfel_gesamt": total_dice,
                    "würfel_werfen": num_rolled,
                    "zielbereich_erweitern": zielbereich_erweiterung,
                    "kraftstufen": kraftstufen,
                    "zielbereich": [min_target, max_target],
                    "erfolgswahrscheinlichkeit": round(success_rate * 100, 2)
                }

    return best_option or {"error": "Keine gültige Kombination gefunden."}

# Streamlit UI
st.set_page_config(page_title="NoReturn PSI-Optimierer", layout="centered")
st.markdown("""
    <style>
        .metric-label, .metric-value {
            color: white !important;
            text-shadow: 1px 1px 2px black;
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
        difficulty = st.selectbox("Schwierigkeit der App", ["leicht", "mittel", "schwer", "ultimativ"])
        st.markdown("""<small>Leicht: 8–12 | Mittel: 11–15 | Schwer: 15–19 | Ultimativ: 23–25</small>""", unsafe_allow_html=True)

    submitted = st.form_submit_button("🔍 Optimieren")

if submitted:
    result = optimize_psi_use(total_dice, difficulty, required_kraftstufen)
    if "error" in result:
        st.error(result["error"])
    else:
        st.success("Beste Kombination gefunden:")
        col1, col2, col3 = st.columns(3)
        col1.metric("🎲 Geworfene Würfel", result["würfel_werfen"])
        col2.metric("➕ Zielbereich erweitern", result["zielbereich_erweitern"])
        col3.metric("⚡ Kraftstufen", result["kraftstufen"])
        st.metric("🎯 Zielbereich", f"{result['zielbereich'][0]}–{result['zielbereich'][1]}")
        st.metric("✅ Erfolgswahrscheinlichkeit", f"{result['erfolgswahrscheinlichkeit']} %")
        style_metric_cards()
