import streamlit as st
import pandas as pd
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Laboratorio de Tenis", layout="centered", page_icon="🎾")

# ==========================================
# --- MOTOR LÓGICO DIDÁCTICO ---
# ==========================================

def simular_punto_m1(p_win):
    res = 1 if random.random() < p_win else 0
    return ("General", res)

def simular_punto_m2(p_win_serve, p_win_return, punto_idx):
    is_serving = (punto_idx % 2 == 0)
    if is_serving:
        res = 1 if random.random() < p_win_serve else 0
        return ("Al Saque", res)
    else:
        res = 1 if random.random() < p_win_return else 0
        return ("Al Resto", res)

def simular_punto_m3(p_s1, p_g_s1, p_g_s2, is_expanded=False, p_s2=0.0, p_g_s2_in=0.0):
    if not is_expanded:
        if random.random() < p_s1:
            res = 1 if random.random() < p_g_s1 else 0
            return ("1º Saque", res)
        else:
            res = 1 if random.random() < p_g_s2 else 0
            return ("2º Saque", res)
    else:
        if random.random() < p_s1:
            res = 1 if random.random() < p_g_s1 else 0
            return ("1º Saque", res)
        else:
            if random.random() < p_s2:
                res = 1 if random.random() < p_g_s2_in else 0
                return ("2º Saque (Juego)", res)
            else:
                return ("Doble Falta (Tuya)", 0) # Pierdes automáticamente

def simular_punto_m4(p_s1_r, p_g_s1_r, p_g_s2_r, is_expanded=False, p_s2_r=0.0, p_g_s2_r_in=0.0):
    if not is_expanded:
        if random.random() < p_s1_r:
            res = 1 if random.random() < p_g_s1_r else 0
            return ("Rival - 1º Saque", res)
        else:
            res = 1 if random.random() < p_g_s2_r else 0
            return ("Rival - 2º Saque", res)
    else:
        if random.random() < p_s1_r:
            res = 1 if random.random() < p_g_s1_r else 0
            return ("Rival - 1º Saque", res)
        else:
            if random.random() < p_s2_r:
                res = 1 if random.random() < p_g_s2_r_in else 0
                return ("Rival - 2º Saque (Juego)", res)
            else:
                return ("Doble Falta (Rival)", 1) # Ganas automáticamente

def simular_punto_m5(p_s1, p_g_s1, p_g_s2, p_s1_r, p_g_s1_r, p_g_s2_r, punto_idx, is_expanded=False, p_s2=0.0, p_g_s2_in=0.0, p_s2_r=0.0, p_g_s2_r_in=0.0):
    is_serving = (punto_idx % 2 == 0)
    if is_serving:
        if not is_expanded:
            if random.random() < p_s1:
                return ("Saque - 1º", 1 if random.random() < p_g_s1 else 0)
            else:
                return ("Saque - 2º", 1 if random.random() < p_g_s2 else 0)
        else:
            if random.random() < p_s1:
                return ("Saque - 1º", 1 if random.random() < p_g_s1 else 0)
            else:
                if random.random() < p_s2:
                    return ("Saque - 2º (Juego)", 1 if random.random() < p_g_s2_in else 0)
                else:
                    return ("Doble Falta (Tuya)", 0)
    else:
        if not is_expanded:
            if random.random() < p_s1_r:
                return ("Resto - 1º", 1 if random.random() < p_g_s1_r else 0)
            else:
                return ("Resto - 2º", 1 if random.random() < p_g_s2_r else 0)
        else:
            if random.random() < p_s1_r:
                return ("Resto - 1º", 1 if random.random() < p_g_s1_r else 0)
            else:
                if random.random() < p_s2_r:
                    return ("Resto - 2º (Juego)", 1 if random.random() < p_g_s2_r_in else 0)
                else:
                    return ("Doble Falta (Rival)", 1)

# ==========================================
# --- MOTOR VISUAL Y DIDÁCTICO ---
# ==========================================

def ejecutar_y_mostrar_simulacion(resultados, p_teorica, n_simulations, modelo_id, is_expanded=False):
    # 1. Procesamiento de datos
    df = pd.DataFrame(resultados, columns=["Camino", "Resultado_Punto"])
    df.index = df.index + 1 
    df["Frecuencia_Acumulada (Simulación)"] = df["Resultado_Punto"].expanding().mean()
    df["Probabilidad_Teorica (Mates)"] = p_teorica
    
    # 2. Métricas y Gráfica (Ley de los Grandes Números)
    st.markdown("---")
    st.subheader("📈 Ley de los Grandes Números (Convergencia)")
    st.markdown("Fíjate en la línea azul: si juegas pocos puntos (ej. 30 en clase de EF), el azar domina. A medida que el número de puntos jugados aumenta, la frecuencia relativa acumulada (línea azul) tiende a estabilizarse en torno a un valor teórico fijo que es la probabilidad (línea roja).")
    
    col1, col2, col3 = st.columns(3)
    frecuencia_final = df["Frecuencia_Acumulada (Simulación)"].iloc[-1]
    col1.metric(label="Probabilidad Teórica", value=f"{p_teorica:.3f}")
    col2.metric(label="Frecuencia Acumulada (Simulada)", value=f"{frecuencia_final:.3f}", 
                delta=f"{(frecuencia_final - p_teorica):.3f} error", delta_color="off")
    col3.metric(label="Puntos Jugados (n)", value=n_simulations)

    st.line_chart(df[["Frecuencia_Acumulada (Simulación)", "Probabilidad_Teorica (Mates)"]], color=["#1f77b4", "#d62728"])

    # 3. Autopsia Empírica (Rastreo de Caminos)
    st.markdown("---")
    st.subheader("🔍 Explicación Matemática")
    st.markdown("¿De dónde sale tu probabilidad de ganar? Vamos a ver qué pasó realmente en la simulación:")
    
    agrupado = df.groupby("Camino")["Resultado_Punto"].agg(["count", "sum"]).reset_index()
    total_ganados = df["Resultado_Punto"].sum()
    
    cols = st.columns(len(agrupado))
    for i, row in agrupado.iterrows():
        with cols[i]:
            st.info(f"**{row['Camino'].upper()}**\n\n"
                    f"Jugados: {row['count']} pts\n\n"
                    f"✅ Ganados: **{row['sum']}**")
            
    st.success(f"🏆 **TOTAL GANADOS:** {total_ganados} (un **{(total_ganados/n_simulations)*100:.1f}%** de los {n_simulations} jugados)")

    # 4. Revelación Matemática
    with st.expander("🎓 Ver la fórmula matemática formal"):
        st.markdown("Lo que acabas de ver empíricamente es la **Probabilidad Compuesta**. Aquí tienes la fórmula pura que hemos usado para calcular la línea roja de teoría:")
        
        if modelo_id == "m1":
            st.latex(r"P(Ganar) = P(Win)")
            st.markdown("En este modelo no hay sucesos condicionados, es probabilidad simple.")
        
        elif modelo_id == "m2":
            st.latex(r"P(Ganar) = P(Saque) \cdot P(G|Saque) + P(Resto) \cdot P(G|Resto)")
            st.markdown("Asume que la mitad de las veces sacas y la otra mitad restas (eventos independientes equiprobables).")
        
        elif modelo_id == "m3":
            if not is_expanded:
                st.latex(r"P(Ganar) = P(S_1) \cdot P(G|S_1) + (1 - P(S_1)) \cdot P(G|\overline{S_1})")
                st.markdown("🙋 **Modo Simplificado:** Combina lo que ganas si entra el primero, con lo que ganas si fallas el primero (Teorema de la Probabilidad Total aplicado a tu saque). Notamos el fallo del primer saque como el suceso complementario $\overline{S_1}$ o $(1 - P(S_1))$.")
            else:
                st.latex(r"P(Ganar) = P(S_1) \cdot P(G|S_1) + (1 - P(S_1)) \cdot P(S_2) \cdot P(G|S_2)")
                st.markdown("🧠 **Modo Avanzado:** Desglosa el segundo saque, castigando directamente las dobles faltas.")
        
        elif modelo_id == "m4":
            if not is_expanded:
                st.latex(r"P(Ganar) = P(S_{1R}) \cdot P(G|S_{1R}) + (1 - P(S_{1R})) \cdot P(G|\overline{S_{1R}})")
                st.markdown("🙋 **Modo Simplificado:** Teorema de la Probabilidad Total aplicado al resto. Depende de las estadísticas de primer saque de tu rival, agrupando todo lo que pasa después en el suceso complementario $\overline{S_{1R}}$.")
            else:
                st.latex(r"P(Ganar) = P(S_{1R}) \cdot P(G|S_{1R}) + (1 - P(S_{1R})) \cdot [P(S_{2R}) \cdot P(G|S_{2R}) + (1 - P(S_{2R}))]")
                st.markdown("🧠 **Modo Avanzado al resto:** Incluye explícitamente los puntos que ganas automáticamente cuando el rival comete doble falta $(1 - P(S_{2R}))$.")
        
        elif modelo_id == "m5":
            if not is_expanded:
                st.latex(r"P(Ganar) = P(Saque) \cdot [P(S_1)P(G|S_1) + (1 - P(S_1))P(G|\overline{S_1})]_{saque} + P(Resto) \cdot [P(S_{1R})P(G|S_{1R}) + (1 - P(S_{1R}))P(G|\overline{S_{1R}})]_{resto}")
                st.markdown("🙋 **Modo Simplificado:** El modelo completo comprimido: combina las probabilidades totales de tu saque y las del saque de tu rival usando los sucesos complementarios.")
            else:
                st.latex(r"\begin{aligned} P(Ganar) &= P(Saque) \cdot [P(S_1)P(G|S_1) + (1-P(S_1))P(S_2)P(G|S_2)] \\ &+ P(Resto) \cdot [P(S_{1R})P(G|S_{1R}) + (1-P(S_{1R}))(P(S_{2R})P(G|S_{2R}) + (1-P(S_{2R})))] \end{aligned}")
                st.markdown("🧠 **Modo Avanzado:** El árbol gigante de probabilidad compuesto por sus **5 caminos reales**, incluyendo el desglose de dobles faltas tuyas y del rival.")

# ==========================================
# --- VISTA PRINCIPAL ---
# ==========================================

def vista_probabilidad_punto():
    st.title("🎾 La probabilidad de ganar un punto")
    st.markdown("Habéis jugado puntos reales en clase de Educación Física. Usad vuestros porcentajes reales aquí para ver cómo se comportan las matemáticas a gran escala.")
    st.markdown("---")
    
    opciones_modelo = {
        "m1": "Modelo 1: Simple (1 parámetro)",
        "m2": "Modelo 2: Saque vs Resto (2 parámetros)",
        "m3": "Modelo 3: Detalle al Saque (3 parámetros)",
        "m4": "Modelo 4: Detalle al Resto (3 parámetros)",
        "m5": "Modelo 5: Detalle Total (6 parámetros)"
    }
    
    st.subheader("⚙️ Configuración del Modelo")
    seleccion = st.selectbox("Selecciona la complejidad de los datos que recogisteis:", list(opciones_modelo.values()))
    
    st.write("") 
    
    # Variables globales para los argumentos de la simulación
    is_expanded = False
    p_teorica = 0.0
    kwargs_sim = {}

    if seleccion == opciones_modelo["m1"]:
        modelo_id = "m1"
        p_win = st.number_input("P(Ganar el punto)", min_value=0.0, max_value=1.0, value=0.50, step=0.05)
        p_teorica = p_win
        kwargs_sim = {'p_win': p_win}
        
    elif seleccion == opciones_modelo["m2"]:
        modelo_id = "m2"
        st.info("💡 Jugaremos alternando: un punto al saque y uno al resto. Así garantizamos que exactamente la mitad (0.5) se juegan sacando.")
        col1, col2 = st.columns(2)
        with col1: p_win_serve = st.number_input("P(Ganar sirviendo)", value=0.65, step=0.05, key="m2_s")
        with col2: p_win_return = st.number_input("P(Ganar restando)", value=0.35, step=0.05, key="m2_r")
        p_teorica = (0.5 * p_win_serve) + (0.5 * p_win_return)
        kwargs_sim = {'p_win_serve': p_win_serve, 'p_win_return': p_win_return}

    elif seleccion == opciones_modelo["m3"]:
        modelo_id = "m3"
        st.info("💡 Asumimos que estás SACANDO en todos los puntos para aislar y estudiar tu efectividad al servicio.")
        is_expanded = st.checkbox("🧠 Modo Avanzado: Desglosar 2º Saque y Dobles Faltas", key="exp3")
        
        if not is_expanded:
            col1, col2, col3 = st.columns(3)
            with col1: p_s1 = st.number_input("P(Entra tu 1º saque)", value=0.60, step=0.05, key="m3_1")
            with col2: p_g_s1 = st.number_input("P(Ganas | Entra tu 1º)", value=0.70, step=0.05, key="m3_2")
            with col3: p_g_s2 = st.number_input("P(Ganas | Fallas tu 1º)", value=0.40, step=0.05, key="m3_3")
            p_teorica = (p_s1 * p_g_s1) + ((1 - p_s1) * p_g_s2)
            kwargs_sim = {'p_s1': p_s1, 'p_g_s1': p_g_s1, 'p_g_s2': p_g_s2, 'is_expanded': False}
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1: p_s1 = st.number_input("P(Entra 1º saque)", value=0.60, step=0.05, key="m3_e1")
            with col2: p_g_s1 = st.number_input("P(Ganas | Entra 1º)", value=0.70, step=0.05, key="m3_e2")
            with col3: p_s2 = st.number_input("P(Entra 2º saque)", value=0.80, step=0.05, key="m3_e3")
            with col4: p_g_s2_in = st.number_input("P(Ganas | Entra 2º)", value=0.50, step=0.05, key="m3_e4")
            p_teorica = (p_s1 * p_g_s1) + ((1 - p_s1) * p_s2 * p_g_s2_in)
            kwargs_sim = {'p_s1': p_s1, 'p_g_s1': p_g_s1, 'p_g_s2': 0, 'is_expanded': True, 'p_s2': p_s2, 'p_g_s2_in': p_g_s2_in}

    elif seleccion == opciones_modelo["m4"]:
        modelo_id = "m4"
        st.info("💡 Asumimos que estás RESTANDO en todos los puntos para aislar y estudiar tu efectividad frente al servicio rival.")
        is_expanded = st.checkbox("🧠 Modo Avanzado: Desglosar 2º Saque y Dobles Faltas del Rival", key="exp4")
        
        if not is_expanded:
            col1, col2, col3 = st.columns(3)
            with col1: p_s1_r = st.number_input("P(Rival mete 1º saque)", value=0.60, step=0.05, key="m4_1")
            with col2: p_g_s1_r = st.number_input("P(Ganas | Rival mete 1º)", value=0.30, step=0.05, key="m4_2")
            with col3: p_g_s2_r = st.number_input("P(Ganas | Rival falla 1º)", value=0.50, step=0.05, key="m4_3")
            p_teorica = (p_s1_r * p_g_s1_r) + ((1 - p_s1_r) * p_g_s2_r)
            kwargs_sim = {'p_s1_r': p_s1_r, 'p_g_s1_r': p_g_s1_r, 'p_g_s2_r': p_g_s2_r, 'is_expanded': False}
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1: p_s1_r = st.number_input("P(Rival mete 1º)", value=0.60, step=0.05, key="m4_e1")
            with col2: p_g_s1_r = st.number_input("P(Ganas | Mete 1º)", value=0.30, step=0.05, key="m4_e2")
            with col3: p_s2_r = st.number_input("P(Rival mete 2º)", value=0.80, step=0.05, key="m4_e3")
            with col4: p_g_s2_r_in = st.number_input("P(Ganas | Mete 2º)", value=0.40, step=0.05, key="m4_e4")
            p_teorica = (p_s1_r * p_g_s1_r) + ((1 - p_s1_r) * ((p_s2_r * p_g_s2_r_in) + (1 - p_s2_r)))
            kwargs_sim = {'p_s1_r': p_s1_r, 'p_g_s1_r': p_g_s1_r, 'p_g_s2_r': 0, 'is_expanded': True, 'p_s2_r': p_s2_r, 'p_g_s2_r_in': p_g_s2_r_in}

    elif seleccion == opciones_modelo["m5"]:
        modelo_id = "m5"
        st.info("💡 El modelo definitivo. Jugaremos alternando: un punto al saque y uno al resto.")
        is_expanded = st.checkbox("🧠 Modo Avanzado: Desglosar 2º Saque y Dobles Faltas", key="exp5")
        
        st.markdown("#### 🎾 Tus datos al Saque")
        if not is_expanded:
            c1, c2, c3 = st.columns(3)
            with c1: p_s1 = st.number_input("P(Entra tu 1º saque)", value=0.60, step=0.05, key="m5_s1")
            with c2: p_g_s1 = st.number_input("P(Ganas | Entra tu 1º)", value=0.70, step=0.05, key="m5_gs1")
            with c3: p_g_s2 = st.number_input("P(Ganas | Fallas tu 1º)", value=0.50, step=0.05, key="m5_gs2")
            p_teorica_saque = (p_s1 * p_g_s1) + ((1 - p_s1) * p_g_s2)
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: p_s1 = st.number_input("P(Entra tu 1º)", value=0.60, step=0.05, key="m5_e1")
            with c2: p_g_s1 = st.number_input("P(Ganas | Entra 1º)", value=0.70, step=0.05, key="m5_e2")
            with c3: p_s2 = st.number_input("P(Entra tu 2º)", value=0.80, step=0.05, key="m5_e3")
            with c4: p_g_s2_in = st.number_input("P(Ganas | Entra 2º)", value=0.50, step=0.05, key="m5_e4")
            p_teorica_saque = (p_s1 * p_g_s1) + ((1 - p_s1) * p_s2 * p_g_s2_in)

        st.write("") 
        
        st.markdown("#### 🛡️ Tus datos al Resto")
        if not is_expanded:
            c4, c5, c6 = st.columns(3)
            with c4: p_s1_r = st.number_input("P(Rival mete 1º saque)", value=0.60, step=0.05, key="m5_s1r")
            with c5: p_g_s1_r = st.number_input("P(Ganas | Rival mete 1º)", value=0.30, step=0.05, key="m5_gs1r")
            with c6: p_g_s2_r = st.number_input("P(Ganas | Rival falla 1º)", value=0.50, step=0.05, key="m5_gs2r")
            p_teorica_resto = (p_s1_r * p_g_s1_r) + ((1 - p_s1_r) * p_g_s2_r)
            kwargs_sim = {'p_s1': p_s1, 'p_g_s1': p_g_s1, 'p_g_s2': p_g_s2, 'p_s1_r': p_s1_r, 'p_g_s1_r': p_g_s1_r, 'p_g_s2_r': p_g_s2_r, 'is_expanded': False}
        else:
            c4, c5, c6, c7 = st.columns(4)
            with c4: p_s1_r = st.number_input("P(Rival mete 1º)", value=0.60, step=0.05, key="m5_er1")
            with c5: p_g_s1_r = st.number_input("P(Ganas | Mete 1º)", value=0.30, step=0.05, key="m5_er2")
            with c6: p_s2_r = st.number_input("P(Rival mete 2º)", value=0.80, step=0.05, key="m5_er3")
            with c7: p_g_s2_r_in = st.number_input("P(Ganas | Mete 2º)", value=0.40, step=0.05, key="m5_er4")
            p_teorica_resto = (p_s1_r * p_g_s1_r) + ((1 - p_s1_r) * ((p_s2_r * p_g_s2_r_in) + (1 - p_s2_r)))
            kwargs_sim = {'p_s1': p_s1, 'p_g_s1': p_g_s1, 'p_g_s2': 0, 'p_s1_r': p_s1_r, 'p_g_s1_r': p_g_s1_r, 'p_g_s2_r': 0, 'is_expanded': True, 'p_s2': p_s2, 'p_g_s2_in': p_g_s2_in, 'p_s2_r': p_s2_r, 'p_g_s2_r_in': p_g_s2_r_in}
        
        p_teorica = (0.5 * p_teorica_saque) + (0.5 * p_teorica_resto)

    st.markdown("### 📊 Simulador de Puntos")
    n_simulations = st.slider("Número de puntos a simular (n)", min_value=10, max_value=1000, value=30, step=10,
                              help="Déjalo en 30 para replicar lo que pasó en clase. Luego súbelo a 1000 para ver la magia de los grandes números.")

    if st.button("Simular Puntos", type="primary"):
        with st.spinner("Jugando puntos..."):
            if modelo_id == "m1":
                res = [simular_punto_m1(**kwargs_sim) for _ in range(n_simulations)]
            elif modelo_id == "m2":
                res = [simular_punto_m2(punto_idx=i, **kwargs_sim) for i in range(n_simulations)]
            elif modelo_id == "m3":
                res = [simular_punto_m3(**kwargs_sim) for _ in range(n_simulations)]
            elif modelo_id == "m4":
                res = [simular_punto_m4(**kwargs_sim) for _ in range(n_simulations)]
            elif modelo_id == "m5":
                res = [simular_punto_m5(punto_idx=i, **kwargs_sim) for i in range(n_simulations)]
            
            ejecutar_y_mostrar_simulacion(res, p_teorica, n_simulations, modelo_id, is_expanded)


def vista_simulador_partidos():
    st.title("🏆 Simulador de Partidos")
    st.info("Próximamente.")

# ==========================================
# --- ENRUTADOR NATIVO DE STREAMLIT ---
# ==========================================
pagina_1 = st.Page(vista_probabilidad_punto, title="Simulador de Puntos", icon="🎾")
pagina_2 = st.Page(vista_simulador_partidos, title="Simulador de Partidos", icon="🏆")
pg = st.navigation([pagina_1, pagina_2])
pg.run()