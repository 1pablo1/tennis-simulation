# import streamlit as st
# import numpy as np
# import matplotlib.pyplot as plt

# # Simula para distintos valores de probabilidad de punto
# from match import simulate


# def simulate_range(simulate_func, n_simulations: int, p_min=0.4, p_max=0.7, steps=20):
#     probabilities = np.linspace(p_min, p_max, steps)
#     win_rates = [simulate_func(p, n_simulations)[1] for p in probabilities]
#     return probabilities, win_rates

# st.set_page_config(page_title="Simulador de Tenis", layout="centered")

# st.title("🎾 Simulador de partidos de tenis")

# st.markdown("""
# Este simulador calcula la probabilidad empírica de que un jugador gane un partido
# en función de su probabilidad de ganar un punto.
# """)

# # Parámetros de entrada
# n_simulations = st.number_input("Número de simulaciones por punto", min_value=100, max_value=10000, value=1000, step=100)
# p_min = st.slider("Probabilidad mínima de ganar un punto", 0.0, 1.0, 0.5)
# p_max = st.slider("Probabilidad máxima de ganar un punto", 0.0, 1.0, 0.6)
# steps = st.slider("Resolución (cantidad de puntos a evaluar)", 5, 100, 21)

# if p_min >= p_max:
#     st.warning("La probabilidad mínima debe ser menor que la máxima.")
# else:
#     if st.button("Simular"):
#         with st.spinner("Simulando partidos..."):
#             # Usa tu función 'simulate' aquí
#             probs, win_rates = simulate_range(simulate, n_simulations, p_min, p_max, steps)

#         st.success("¡Simulación completada!")

#         fig, ax = plt.subplots()
#         ax.plot(probs, win_rates, marker='o', color='navy')
#         ax.set_title("Probabilidad de ganar el partido vs. Probabilidad de ganar un punto")
#         ax.set_xlabel("Probabilidad de ganar un punto")
#         ax.set_ylabel("Probabilidad de ganar el partido")
#         ax.grid(True)

#         st.pyplot(fig)

#         # Datos tabulares
#         st.subheader("📋 Datos")
#         st.dataframe({
#             "Probabilidad de ganar un punto": probs,
#             "Probabilidad de ganar el partido": win_rates
#         })

import streamlit as st
import pandas as pd
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Laboratorio de Tenis", layout="centered", page_icon="🎾")

# --- FUNCIONES LÓGICAS (El Motor de la Simulación) ---
def simular_punto(p_s1, p_g_s1, p_g_s2):
    """
    Simula un punto de tenis usando probabilidad condicionada.
    Devuelve 1 si el jugador gana el punto, 0 si lo pierde.
    """
    # ¿Entra el primer saque?
    if random.random() < p_s1:
        # Sí entró. ¿Gana el punto con este saque?
        return 1 if random.random() < p_g_s1 else 0
    else:
        # Falló el primero. Juega con el segundo. ¿Gana el punto?
        return 1 if random.random() < p_g_s2 else 0

# --- INTERFAZ DE USUARIO (Sidebar) ---
st.sidebar.header("⚙️ Parámetros del Tenista")
st.sidebar.markdown("Introduce los datos recogidos en la pista:")

p_s1 = st.sidebar.number_input("P(Entra 1º saque)", min_value=0.0, max_value=1.0, value=0.60, step=0.05)
p_g_s1 = st.sidebar.number_input("P(Gana | Entra 1º)", min_value=0.0, max_value=1.0, value=0.70, step=0.05)
p_g_s2 = st.sidebar.number_input("P(Gana | Falla 1º)", min_value=0.0, max_value=1.0, value=0.40, step=0.05)

st.sidebar.markdown("---")
st.sidebar.header("📊 Opciones de Simulación")
n_simulations = st.sidebar.slider("Número de puntos a simular (N)", min_value=10, max_value=5000, value=1000, step=10)

# --- CUERPO PRINCIPAL ---
st.title("🎾 Laboratorio de Probabilidad: El Punto")
st.markdown("""
En esta simulación no estamos jugando un partido completo, sino **analizando la anatomía de un solo punto**. 
Vamos a comprobar si la probabilidad teórica (matemática) coincide con la realidad empírica (simulación) cuando jugamos muchos puntos, demostrando la **Ley de los Grandes Números**.
""")

# Botón para ejecutar (le da interactividad)
if st.button("Simular Puntos", type="primary"):
    with st.spinner("Simulando y calculando frecuencias..."):
        
        # 1. EJECUCIÓN DE LA SIMULACIÓN
        resultados = [simular_punto(p_s1, p_g_s1, p_g_s2) for _ in range(n_simulations)]
        
        # 2. PROCESAMIENTO DE DATOS CON PANDAS
        df = pd.DataFrame(resultados, columns=["Resultado_Punto"])
        df.index = df.index + 1 # Para que el eje X empiece en el punto 1, no en el 0
        df.index.name = "Punto_Jugado"
        
        # Cálculo Crítico: Frecuencia Relativa Acumulada
        df["Frecuencia_Acumulada (Simulación)"] = df["Resultado_Punto"].expanding().mean()
        
        # Cálculo Teórico (Teorema de la Probabilidad Total)
        p_teorica = (p_s1 * p_g_s1) + ((1 - p_s1) * p_g_s2)
        df["Probabilidad_Teorica (Mates)"] = p_teorica
        
        # 3. RESULTADOS MATEMÁTICOS (Métricas)
        st.subheader("Resultados del Experimento")
        col1, col2, col3 = st.columns(3)
        
        frecuencia_final = df["Frecuencia_Acumulada (Simulación)"].iloc[-1]
        
        col1.metric(label="Probabilidad Teórica P(G)", value=f"{p_teorica:.3f}")
        col2.metric(label="Frecuencia Final (Simulada)", value=f"{frecuencia_final:.3f}", 
                    delta=f"{(frecuencia_final - p_teorica):.3f} error", delta_color="off")
        col3.metric(label="Puntos Jugados (N)", value=n_simulations)

        # 4. VISUALIZACIÓN GRÁFICA (Convergencia)
        st.subheader("Gráfica de Convergencia")
        st.markdown("Observa cómo la línea azul (azar) busca estabilizarse en la línea roja (teoría).")
        st.line_chart(df[["Frecuencia_Acumulada (Simulación)", "Probabilidad_Teorica (Mates)"]], color=["#1f77b4", "#d62728"])

# --- TRANSPARENCIA DIDÁCTICA (Caja Blanca) ---
st.markdown("---")
with st.expander("🔍 ¿Cómo funciona esta simulación (Lógica del Modelo)?"):
    st.markdown("Para evitar que esto sea una 'caja mágica', aquí tienes el código exacto que decide si ganas o pierdes cada punto:")
    st.code("""
def simular_punto(p_s1, p_g_s1, p_g_s2):
    # ¿Entra el primer saque?
    if random.random() < p_s1:
        # Sí entró. ¿Gana el punto con este saque?
        return 1 if random.random() < p_g_s1 else 0
    else:
        # Falló el primero. Juega con el segundo. ¿Gana el punto?
        return 1 if random.random() < p_g_s2 else 0
    """, language="python")
    st.markdown("*Nota: `random.random()` genera un número al azar entre 0 y 1. Si ese número es menor que tu probabilidad, el suceso ocurre.*")