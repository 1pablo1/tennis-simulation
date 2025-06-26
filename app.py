import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Simula para distintos valores de probabilidad de punto
from match import simulate


def simulate_range(simulate_func, n_simulations: int, p_min=0.4, p_max=0.7, steps=20):
    probabilities = np.linspace(p_min, p_max, steps)
    win_rates = [simulate_func(p, n_simulations)[1] for p in probabilities]
    return probabilities, win_rates

st.set_page_config(page_title="Simulador de Tenis", layout="centered")

st.title("🎾 Simulador de partidos de tenis")

st.markdown("""
Este simulador calcula la probabilidad empírica de que un jugador gane un partido
en función de su probabilidad de ganar un punto.
""")

# Parámetros de entrada
n_simulations = st.number_input("Número de simulaciones por punto", min_value=100, max_value=10000, value=1000, step=100)
p_min = st.slider("Probabilidad mínima de ganar un punto", 0.0, 1.0, 0.5)
p_max = st.slider("Probabilidad máxima de ganar un punto", 0.0, 1.0, 0.6)
steps = st.slider("Resolución (cantidad de puntos a evaluar)", 5, 100, 21)

if p_min >= p_max:
    st.warning("La probabilidad mínima debe ser menor que la máxima.")
else:
    if st.button("Simular"):
        with st.spinner("Simulando partidos..."):
            # Usa tu función 'simulate' aquí
            probs, win_rates = simulate_range(simulate, n_simulations, p_min, p_max, steps)

        st.success("¡Simulación completada!")

        fig, ax = plt.subplots()
        ax.plot(probs, win_rates, marker='o', color='navy')
        ax.set_title("Probabilidad de ganar el partido vs. Probabilidad de ganar un punto")
        ax.set_xlabel("Probabilidad de ganar un punto")
        ax.set_ylabel("Probabilidad de ganar el partido")
        ax.grid(True)

        st.pyplot(fig)

        # Datos tabulares
        st.subheader("📋 Datos")
        st.dataframe({
            "Probabilidad de ganar un punto": probs,
            "Probabilidad de ganar el partido": win_rates
        })