import streamlit as st
import pandas as pd
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
from random import random as rand_float, choice
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Laboratorio de Tenis", layout="centered", page_icon="🎾")

# ==========================================
# --- MOTOR LÓGICO DIDÁCTICO (PUNTOS) ---
# ==========================================

def simular_punto_m1(p_win):
    res = 1 if rand_float() < p_win else 0
    return ("General", res)

def simular_punto_m2(p_win_serve, p_win_return, punto_idx):
    is_serving = (punto_idx % 2 == 0)
    if is_serving:
        res = 1 if rand_float() < p_win_serve else 0
        return ("Al Saque", res)
    else:
        res = 1 if rand_float() < p_win_return else 0
        return ("Al Resto", res)

def simular_punto_m3(p_s1, p_g_s1, p_g_s2, is_expanded=False, p_s2=0.0, p_g_s2_in=0.0):
    if not is_expanded:
        if rand_float() < p_s1:
            res = 1 if rand_float() < p_g_s1 else 0
            return ("1º Saque", res)
        else:
            res = 1 if rand_float() < p_g_s2 else 0
            return ("2º Saque", res)
    else:
        if rand_float() < p_s1:
            res = 1 if rand_float() < p_g_s1 else 0
            return ("1º Saque", res)
        else:
            if rand_float() < p_s2:
                res = 1 if rand_float() < p_g_s2_in else 0
                return ("2º Saque (Juego)", res)
            else:
                return ("Doble Falta (Tuya)", 0)

def simular_punto_m4(p_s1_r, p_g_s1_r, p_g_s2_r, is_expanded=False, p_s2_r=0.0, p_g_s2_r_in=0.0):
    if not is_expanded:
        if rand_float() < p_s1_r:
            res = 1 if rand_float() < p_g_s1_r else 0
            return ("Rival - 1º Saque", res)
        else:
            res = 1 if rand_float() < p_g_s2_r else 0
            return ("Rival - 2º Saque", res)
    else:
        if rand_float() < p_s1_r:
            res = 1 if rand_float() < p_g_s1_r else 0
            return ("Rival - 1º Saque", res)
        else:
            if rand_float() < p_s2_r:
                res = 1 if rand_float() < p_g_s2_r_in else 0
                return ("Rival - 2º Saque (Juego)", res)
            else:
                return ("Doble Falta (Rival)", 1)

def simular_punto_m5(p_s1, p_g_s1, p_g_s2, p_s1_r, p_g_s1_r, p_g_s2_r, punto_idx, is_expanded=False, p_s2=0.0, p_g_s2_in=0.0, p_s2_r=0.0, p_g_s2_r_in=0.0):
    is_serving = (punto_idx % 2 == 0)
    if is_serving:
        if not is_expanded:
            if rand_float() < p_s1:
                return ("Saque - 1º", 1 if rand_float() < p_g_s1 else 0)
            else:
                return ("Saque - 2º", 1 if rand_float() < p_g_s2 else 0)
        else:
            if rand_float() < p_s1:
                return ("Saque - 1º", 1 if rand_float() < p_g_s1 else 0)
            else:
                if rand_float() < p_s2:
                    return ("Saque - 2º (Juego)", 1 if rand_float() < p_g_s2_in else 0)
                else:
                    return ("Doble Falta (Tuya)", 0)
    else:
        if not is_expanded:
            if rand_float() < p_s1_r:
                return ("Resto - 1º", 1 if rand_float() < p_g_s1_r else 0)
            else:
                return ("Resto - 2º", 1 if rand_float() < p_g_s2_r else 0)
        else:
            if rand_float() < p_s1_r:
                return ("Resto - 1º", 1 if rand_float() < p_g_s1_r else 0)
            else:
                if rand_float() < p_s2_r:
                    return ("Resto - 2º (Juego)", 1 if rand_float() < p_g_s2_r_in else 0)
                else:
                    return ("Doble Falta (Rival)", 1)

# ==========================================
# --- MOTOR DE JUEGOS (PESTAÑA 2) ---
# ==========================================
def simular_un_juego(p_win_pt, punto_oro=False):
    p1_pts = 0
    p2_pts = 0
    while True:
        if rand_float() < p_win_pt:
            p1_pts += 1
        else:
            p2_pts += 1
        
        if punto_oro:
            if p1_pts == 4:
                if p2_pts == 0: cam = "En blanco (40-0)"
                elif p2_pts == 1: cam = "A 15 (40-15)"
                elif p2_pts == 2: cam = "A 30 (40-30)"
                else: cam = "Punto de Oro (40-40)"
                return (cam, 1)
            if p2_pts == 4: return ("Perdido", 0)
        else:
            if p1_pts >= 4 and (p1_pts - p2_pts) >= 2:
                if p2_pts == 0: cam = "En blanco (40-0)"
                elif p2_pts == 1: cam = "A 15 (40-15)"
                elif p2_pts == 2: cam = "A 30 (40-30)"
                else: cam = "Tras el Deuce"
                return (cam, 1)
            if p2_pts >= 4 and (p2_pts - p1_pts) >= 2: return ("Perdido", 0)

# ==========================================
# --- MOTOR DE PARTIDOS (MATCH.PY) ---
# ==========================================

class TennisPoint(Enum):
    LOVE = 0
    FIFTEEN = 15
    THIRTY = 30
    FORTY = 40
    ADVANTAGE = 'A'
    GAME = 'G'

    @classmethod
    def score_to_point(cls, score: int) -> 'TennisPoint':
        if score >= 3: return cls.FORTY
        return [cls.LOVE, cls.FIFTEEN, cls.THIRTY, cls.FORTY][score]

@dataclass
class Player:
    name: str
    delta_on_important_pts: float = 0
    def __str__(self): return self.name

@dataclass
class Match:
    player1: Player
    player2: Player
    probability_1_on_serve: float
    probability_1_receiving: float
    sets: List['Set'] = field(default_factory=list)
    result: Tuple[int, int] | None = None
    winner: Player | None = None
    tie_break_points: int = 7
    max_sets: int = 3
    history: List[Tuple[int, int, int, int, int, int, bool]] = field(default_factory=list) 

    def other_player(self, player: Player) -> Player:
        return self.player2 if player == self.player1 else self.player1

    def predict(self):
        while not self.is_over():
            self.predict_set()
        self.set_winner()

    def predict_set(self) -> 'Set':
        _set = Set(self, self.server)
        self.sets.append(_set)
        _set.predict()
        self.set_result()
        return _set

    @property
    def server(self):
        if not self.sets: return choice([self.player1, self.player2])
        return self.sets[-1].server

    def is_over(self, set_result: bool = False) -> bool:
        if set_result or self.result is None: self.set_result()
        return any(score >= self.needed_sets for score in self.result)

    def set_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for _set in self.sets:
            if not _set.winner: continue
            if _set.winner == self.player1: scores[0] += 1
            else: scores[1] += 1
        self.result = tuple(scores)
        return self.result

    def set_winner(self):
        self.winner = self.player1 if self.result[0] > self.result[1] else self.player2

    @property
    def needed_sets(self):
        return self.max_sets // 2 + 1

@dataclass
class Set:
    match: Match
    first_server: Player
    games: List['Game'] = field(default_factory=list)
    result: Tuple[int, int] | None = None
    winner: Player | None = None

    def predict(self):
        while not self.is_over():
            self.predict_game()
        self.set_winner()

    @property
    def server(self) -> Player:
        played_games = sum(1 for game in self.games if game.winner)
        if played_games % 2 == 0: return self.first_server
        return self.match.other_player(self.first_server)

    def predict_game(self) -> 'Game':
        game = Game(self.server, self.match, is_tiebreak=self.next_game_is_tie_break())
        self.games.append(game)
        game.predict()
        self.set_result()
        return game

    def set_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for game in self.games:
            if not game.winner: continue
            if game.winner == self.match.player1: scores[0] += 1
            else: scores[1] += 1
            if self.check_if_is_won(*scores) or self.check_if_is_won(*scores[::-1]): break
        self.result = tuple(scores)
        return self.result

    def next_game_is_tie_break(self) -> bool: return self.result == (6, 6)

    @staticmethod
    def check_if_is_won(first_score: int, second_score: int) -> bool:
        return first_score >= 7 or (first_score >= 6 and second_score + 2 <= first_score)

    def is_over(self, set_result: bool = False) -> bool:
        if set_result or self.result is None: self.set_result()
        return self.check_if_is_won(max(self.result), min(self.result))

    def set_winner(self):
        self.winner = self.match.player1 if self.result[0] > self.result[1] else self.match.player2

@dataclass
class Game:
    player_serving: Player
    match: Match
    winner: Player | None = None
    result: Tuple[TennisPoint, TennisPoint] | Tuple[int, int] | None = None
    points: List['Point'] = field(default_factory=list)
    is_tiebreak: bool = False

    def predict(self):
        while not self.is_over():
            s1 = sum(1 for s in self.match.sets if s.winner == self.match.player1)
            s2 = sum(1 for s in self.match.sets if s.winner == self.match.player2)
            current_set = self.match.sets[-1] if self.match.sets else None
            g1 = sum(1 for g in current_set.games if g.winner == self.match.player1) if current_set else 0
            g2 = sum(1 for g in current_set.games if g.winner == self.match.player2) if current_set else 0
            p1_pts = sum(1 for p in self.points if p.winner == self.match.player1)
            p2_pts = sum(1 for p in self.points if p.winner == self.match.player2)
            
            is_p1_serving_game = (self.player_serving == self.match.player1)
            self.match.history.append((s1, s2, g1, g2, p1_pts, p2_pts, is_p1_serving_game))
            self.predict_point()
        self.set_winner()

    def set_winner(self):
        winner = self.match.player1
        if self.is_tiebreak:
            if self.result[1] > self.result[0]: winner = self.match.player2
        elif self.result[1] == TennisPoint.GAME:
            winner = self.match.player2
        self.winner = winner

    def add_point(self) -> 'Point':
        point = Point(None, self.serving, self)
        self.points.append(point)
        return point

    def predict_point(self) -> 'Point':
        point = self.add_point()
        point.predict()
        self.set_result()
        return point

    @property
    def serving(self) -> Player:
        if not self.is_tiebreak: return self.player_serving
        total_points = sum(1 for point in self.points if point.winner)
        if ((total_points + 1) // 2) % 2 == 1:
            return self.match.other_player(self.player_serving)
        return self.player_serving

    @property
    def is_critic_point(self) -> bool: return False

    def check_if_is_won(self, first_score: int, second_score: int, needed_points: int = 4) -> bool:
        if self.is_tiebreak: needed_points = self.match.tie_break_points
        return first_score >= needed_points and second_score + 2 <= first_score

    def is_over(self, set_result: bool = False) -> bool:
        if set_result or self.result is None: self.set_result()
        if self.is_tiebreak: return self.check_if_is_won(max(self.result), min(self.result))
        return TennisPoint.GAME in self.result

    def set_result(self):
        if self.is_tiebreak: self.result = self.tie_break_result()
        else: self.result = self.normal_game_result()

    def normal_game_result(self) -> Tuple[TennisPoint, TennisPoint]:
        scores = [0, 0]
        for point in self.points:
            if not point.winner: continue
            if point.winner == self.match.player1: scores[0] += 1
            else: scores[1] += 1
            if scores[0] > scores[1] and self.check_if_is_won(*scores):
                return TennisPoint.GAME, TennisPoint.score_to_point(scores[1])
            elif scores[1] > scores[0] and self.check_if_is_won(*scores[::-1]):
                return TennisPoint.score_to_point(scores[0]), TennisPoint.GAME
        return self.get_not_finished_game_result(scores)

    @staticmethod
    def get_not_finished_game_result(scores: List[int]) -> Tuple[TennisPoint, TennisPoint]:
        if scores[0] > scores[1] >= 3: return TennisPoint.ADVANTAGE, TennisPoint.FORTY
        if scores[1] > scores[0] >= 3: return TennisPoint.FORTY, TennisPoint.ADVANTAGE
        if scores[0] == scores[1] > 3: return TennisPoint.FORTY, TennisPoint.FORTY
        return (TennisPoint.score_to_point(scores[0]), TennisPoint.score_to_point(scores[1]))

    def tie_break_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for point in self.points:
            if not point.winner: continue
            if point.winner == self.match.player1: scores[0] += 1
            else: scores[1] += 1
            if self.check_if_is_won(*scores) or self.check_if_is_won(*scores[::-1]): break
        return tuple(scores)

@dataclass
class Point:
    winner: Player | None
    serving: Player
    game: Game | None

    def predict(self):
        player_1_wins = rand_float() <= self.get_player_1_probability()
        self.winner = self.player1 if player_1_wins else self.player2
        return self.winner

    @property
    def is_critic_point(self) -> bool:
        return self.game.is_critic_point if self.game else False

    @property
    def player1(self) -> Player: return self.game.match.player1

    @property
    def player2(self) -> Player: return self.game.match.player2

    def get_player_1_probability(self):
        if self.serving == self.player1: probability = self.game.match.probability_1_on_serve
        else: probability = self.game.match.probability_1_receiving
        if self.is_critic_point:
            probability += (self.player1.delta_on_important_pts - self.player2.delta_on_important_pts)
        return probability

# ==========================================
# --- MOTOR VISUAL (AISLADO POR PESTAÑAS) ---
# ==========================================

# RENDERIZADOR EXACTO ORIGINAL (Para Pestaña 1)
def mostrar_simulacion_puntos(resultados, p_teorica, n_simulations, modelo_id, is_expanded=False):
    df = pd.DataFrame(resultados, columns=["Camino", "Resultado_Punto"])
    df.index = df.index + 1 
    df["Frecuencia_Acumulada (Simulación)"] = df["Resultado_Punto"].expanding().mean()
    df["Probabilidad_Teorica (Mates)"] = p_teorica
    
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

    st.markdown("---")
    st.subheader("🔍 Explicación Matemática")
    st.markdown("¿De dónde sale tu probabilidad de ganar? Vamos a ver qué pasó realmente en la simulación:")
    
    agrupado = df.groupby("Camino")["Resultado_Punto"].agg(["count", "sum"]).reset_index()
    total_ganados = df["Resultado_Punto"].sum()
    
    if not agrupado.empty:
        cols = st.columns(len(agrupado))
        for i, row in agrupado.iterrows():
            with cols[i]:
                st.info(f"**{row['Camino'].upper()}**\n\nJugados: {row['count']} pts\n\n✅ Ganados: **{row['sum']}**")
            
    st.success(f"🏆 **TOTAL GANADOS:** {total_ganados} (un **{(total_ganados/n_simulations)*100:.1f}%** de los {n_simulations} jugados)")

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


# RENDERIZADOR NUEVO (Para Pestaña 2)
def mostrar_simulacion_juegos(resultados, p_teorica, n_simulations, punto_de_oro):
    df = pd.DataFrame(resultados, columns=["Camino", "Resultado"])
    df.index = df.index + 1 
    df["Frecuencia_Acumulada (Simulación)"] = df["Resultado"].expanding().mean()
    df["Probabilidad_Teorica (Mates)"] = p_teorica
    
    st.markdown("---")
    st.subheader("📈 Ley de los Grandes Números (Convergencia)")
    st.markdown("Fíjate en la línea azul: si juegas pocos juegos, el azar domina. A medida que el número de juegos aumenta, la frecuencia relativa acumulada (línea azul) tiende a estabilizarse en torno a un valor teórico fijo que es la probabilidad (línea roja).")
    
    col1, col2, col3 = st.columns(3)
    frecuencia_final = df["Frecuencia_Acumulada (Simulación)"].iloc[-1]
    col1.metric(label="Probabilidad Teórica", value=f"{p_teorica:.3f}")
    col2.metric(label="Frecuencia Acumulada (Simulada)", value=f"{frecuencia_final:.3f}", 
                delta=f"{(frecuencia_final - p_teorica):.3f} error", delta_color="off")
    col3.metric(label="Juegos Simulados (n)", value=n_simulations)

    st.line_chart(df[["Frecuencia_Acumulada (Simulación)", "Probabilidad_Teorica (Mates)"]], color=["#1f77b4", "#d62728"])

    st.markdown("---")
    st.subheader("🔍 Explicación Matemática")
    st.markdown("¿De dónde sale tu probabilidad de ganar? Vamos a ver qué pasó realmente en la simulación:")
    
    ganados = df[df["Resultado"] == 1]
    agrupado = ganados.groupby("Camino")["Resultado"].count().reset_index()
    total_ganados = df["Resultado"].sum()
    
    if not agrupado.empty:
        cols = st.columns(len(agrupado))
        for i, row in agrupado.iterrows():
            with cols[i]:
                jugados_camino = df[df["Camino"] == row['Camino']].shape[0]
                st.info(f"**{row['Camino'].upper()}**\n\nJugados: {jugados_camino} juegos\n\n✅ Ganados: **{row['Resultado']}**")
            
    st.success(f"🏆 **TOTAL GANADOS:** {total_ganados} (un **{(total_ganados/n_simulations)*100:.1f}%** de los {n_simulations} jugados)")
    
    with st.expander("🎓 Ver la fórmula matemática formal"):
        if not punto_de_oro:
            st.markdown("Calcular la probabilidad de un juego tradicional es complejo porque los caminos son infinitos (debido al Deuce). Usamos una fórmula basada en cadenas de Markov y series geométricas:")
            st.latex(r"P(Juego) = p^4 + 4p^4q + 10p^4q^2 + \frac{20p^3q^3 \cdot p^2}{1 - 2pq}")
            st.markdown("""
            Donde los coeficientes salen de usar técnicas de recuento (Combinatoria / Permutaciones con Repetición) para ver las formas de ordenar los puntos ganados ($p$) y perdidos ($q$) antes del punto decisivo:
            - **$p^4$**: Ganar en blanco (40-0). Solo hay 1 camino directo.
            - **$4p^4q$**: Ganar a 15 (40-15). Hay $C(4,3) = 4$ caminos para llegar al 40-15 y luego ganas el punto final.
            - **$10p^4q^2$**: Ganar a 30 (40-30). Hay $C(5,3) = 10$ caminos para llegar al 40-30 y luego ganas el punto final.
            - **El último término (Tras el Deuce)**: Hay $C(6,3) = 20$ caminos posibles para llegar al 40-40 ($20p^3q^3$). Desde ahí, la serie geométrica $\frac{p^2}{1 - 2pq}$ calcula los infinitos rebotes de ventajas hasta que por fin ganas dos puntos seguidos.
            """)
        else:
            st.markdown("Al jugar con **Punto de Oro**, el juego se convierte en un modelo estrictamente finito (máximo 7 puntos). Sumamos la probabilidad de los 4 caminos posibles:")
            st.latex(r"P(Juego) = p^4 + 4p^4q + 10p^4q^2 + 20p^4q^3")
            st.markdown("""
            Donde los coeficientes salen de la Combinatoria para contar las diferentes secuencias de puntos ganados ($p$) y perdidos ($q$):
            - **$p^4$**: Ganar en blanco. (1 único camino).
            - **$4p^4q$**: Ganar a 15. Combinatoria: $C(4,3) = 4$ formas de ir 40-15, multiplicado por $p$ (ganar el punto de juego).
            - **$10p^4q^2$**: Ganar a 30. Combinatoria: $C(5,3) = 10$ formas de ir 40-30, multiplicado por $p$ (ganar el punto de juego).
            - **$20p^4q^3$**: Ganar el Punto de Oro. Combinatoria: $C(6,3) = 20$ formas distintas de llegar empatados al 3-3 (40-40), multiplicado por $p$ (ganar el séptimo y decisivo punto).
            """)


# ==========================================
# --- PESTAÑA 1: PUNTOS ---
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
            with c3: p_g_s2 = st.number_input("P(Ganas | Fallas tu 1º)", value=0.40, step=0.05, key="m5_gs2")
            p_teorica_saque = (p_s1 * p_g_s1) + ((1 - p_s1) * p_g_s2)
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1: p_s1 = st.number_input("P(Entra tu 1º)", value=0.60, step=0.05, key="m5_e1")
            with c2: p_g_s1 = st.number_input("P(Ganas | Entra 1º)", value=0.70, step=0.05, key="m5_e2")
            with c3: p_s2 = st.number_input("P(Entra tu 2º)", value=0.80, step=0.05, key="m5_e3")
            with c4: p_g_s2_in = st.number_input("P(Ganas | Entra 2º)", value=0.50, step=0.05, key="m5_e4")
            p_teorica_saque = (p_s1 * p_g_s1) + ((1 - p_s1) * p_s2 * p_g_s2_in)
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
            if seleccion == opciones_modelo["m1"]: res = [simular_punto_m1(**kwargs_sim) for _ in range(n_simulations)]
            elif seleccion == opciones_modelo["m2"]: res = [simular_punto_m2(punto_idx=i, **kwargs_sim) for i in range(n_simulations)]
            elif seleccion == opciones_modelo["m3"]: res = [simular_punto_m3(**kwargs_sim) for _ in range(n_simulations)]
            elif seleccion == opciones_modelo["m4"]: res = [simular_punto_m4(**kwargs_sim) for _ in range(n_simulations)]
            elif seleccion == opciones_modelo["m5"]: res = [simular_punto_m5(punto_idx=i, **kwargs_sim) for i in range(n_simulations)]
            
            mostrar_simulacion_puntos(res, p_teorica, n_simulations, modelo_id, is_expanded)
            
            if p_teorica > 0:
                st.info(f"💡 Guarda este dato: tu probabilidad de ganar un punto es **{p_teorica:.3f}**. Úsalo en la siguiente pestaña.")

# ==========================================
# --- PESTAÑA 2: JUEGOS ---
# ==========================================

def vista_probabilidad_juego():
    st.title("💪 La probabilidad de ganar un juego")
    st.markdown("Bienvenido al simulador de juegos. Aquí conectamos tus probabilidades aisladas del punto para ver **cómo el sistema de puntuación del tenis actúa como un amplificador de pequeñas ventajas.")
    st.markdown("---")
    
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        p_win_pt = st.number_input("Probabilidad de ganar un PUNTO (usa el dato del simulador de puntos):", 
                                   min_value=0.01, max_value=0.99, value=0.50, step=0.01)
        punto_de_oro = st.checkbox("🥇 Jugar con 'Punto de Oro' (Sin ventajas en el 40-40)", value=False)
        
    with col_in2:
        n_sim_games = st.slider("Número de juegos a simular:", min_value=10, max_value=1000, value=100, step=10, 
                                help="Aumenta el número para ver la convergencia matemática.")

    p = p_win_pt
    q = 1 - p
    if not punto_de_oro:
        p_win_game_theo = p**4 + 4*(p**4)*q + 10*(p**4)*(q**2) + (20*(p**3)*(q**3) * (p**2 / (1 - 2*p*q)))
    else:
        p_win_game_theo = p**4 + 4*(p**4)*q + 10*(p**4)*(q**2) + 20*(p**4)*(q**3)

    if st.button("Simular Juegos", type="primary"):
        with st.spinner("Jugando juegos..."):
            res_juegos = [simular_un_juego(p_win_pt, punto_de_oro) for _ in range(n_sim_games)]
            mostrar_simulacion_juegos(res_juegos, p_win_game_theo, n_sim_games, punto_de_oro)

            if p_win_pt > 0.5:
                st.info(f"✨ **¡Efecto Lupa detectado!** Tu ventaja en el punto era del {(p_win_pt*100):.1f}%, pero en el juego ha subido al {(p_win_game_theo*100):.1f}%. El tenis premia la consistencia.")

# ==========================================
# --- PESTAÑA 3: PARTIDOS ---
# ==========================================

def get_tennis_score_label(p1: int, p2: int, is_tiebreak: bool = False) -> str:
    if is_tiebreak:
        return f"{p1}-{p2}"

    scores = {0: "0", 1: "15", 2: "30", 3: "40"}
    if p1 >= 4 and p1 - p2 >= 2: return f"JUEGO-{scores.get(p2, p2)}"
    if p2 >= 4 and p2 - p1 >= 2: return f"{scores.get(p1, p1)}-JUEGO"
    
    if p1 >= 3 and p2 >= 3:
        if p1 == p2: return "40-40"
        elif p1 - p2 == 1: return "AD-40"
        elif p2 - p1 == 1: return "40-AD"
        
    return f"{scores.get(p1, str(p1))}-{scores.get(p2, str(p2))}"

def is_node_visible(p1: int, p2: int, is_tiebreak: bool) -> bool:
    if is_tiebreak:
        if (p1 >= 7 and p1 - p2 >= 2) or (p2 >= 7 and p2 - p1 >= 2): return False
        return True
    else:
        if (p1 >= 4 and p1 - p2 >= 2) or (p2 >= 4 and p2 - p1 >= 2): return False
        if p1 >= 4 and p2 >= 4: return False 
        return True

def generar_opciones_juego_validas() -> List[str]:
    valid_games = []
    for i in range(7):
        for j in range(7):
            if (i >= 6 and i - j >= 2) or (j >= 6 and j - i >= 2): continue
            if i == 6 and j == 6: continue
            valid_games.append(f"{i}-{j}")
    valid_games.append("6-6")
    return valid_games

def vista_simulador_partidos():
    st.title("🏆 La probabilidad de ganar un partido")
    st.markdown("Bienvenido al simulador de partidos. Lleva tus datos al máximo nivel y experimenta con las probabilidades de ganar un partido (casi) real 😉.")
    st.markdown("---")
    
    st.markdown("### 📊 Tus estadísticas de entrada")
    tipo_input = st.radio("¿Qué datos obtuviste en el Simulador de Puntos?", 
                          ["🎯 Porcentaje Único", "🎾🛡️ Saque y Resto separados"], 
                          horizontal=True)
    
    if tipo_input == "🎯 Porcentaje Único":
        p_general = st.number_input("P(Ganar el punto general)", value=0.50, step=0.01, min_value=0.01, max_value=0.99)
        p_serve = p_general
        p_return = p_general
    else:
        col1, col2 = st.columns(2)
        with col1:
            p_serve = st.number_input("P(Ganar sirviendo)", value=0.65, step=0.05, min_value=0.01, max_value=0.99)
        with col2:
            p_return = st.number_input("P(Ganar restando)", value=0.35, step=0.05, min_value=0.01, max_value=0.99)
        
    num_matches = st.slider("Número de partidos a simular:", min_value=100, max_value=20000, value=1000, step=100)

    st.markdown("### 🔖 Filtros del Marcador")
    st.markdown("Selecciona el estado del partido que quieres inspeccionar en el gráfico:")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        set_filter = st.selectbox("Marcador de Sets", ["0-0", "1-0", "0-1", "1-1"])
    with f_col2:
        game_options = generar_opciones_juego_validas()
        game_filter = st.selectbox("Marcador de Juegos", game_options, index=0)
    with f_col3:
        serve_filter = st.selectbox("¿Quién saca en este juego?", ["Tú (Al Saque)", "Rival (Al Resto)"])

    s1_target, s2_target = map(int, set_filter.split("-"))
    g1_target, g2_target = map(int, game_filter.split("-"))
    is_p1_serving_target = (serve_filter == "Tú (Al Saque)")
    is_tiebreak_target = (g1_target == 6 and g2_target == 6)

    if st.button("Simular Partidos y Actualizar Gráfico", type="primary"):
        with st.spinner(f"Usando la Máquina del Tiempo para generar {num_matches} partidos..."):
            player_1 = Player('Tú')
            player_2 = Player('Rival')
            
            matches_won = 0
            state_wins = {} 
            
            for _ in range(num_matches):
                match = Match(player_1, player_2, probability_1_on_serve=p_serve, probability_1_receiving=p_return)
                
                # --- LA MÁQUINA DEL TIEMPO ---
                for _ in range(s1_target):
                    s = Set(match, player_1); s.winner = player_1; match.sets.append(s)
                for _ in range(s2_target):
                    s = Set(match, player_2); s.winner = player_2; match.sets.append(s)
                
                if match.is_over():
                    match.set_winner()
                else:
                    total_g = g1_target + g2_target
                    first_server = player_1 if (total_g % 2 == 0) == is_p1_serving_target else player_2
                    current_set = Set(match, first_server)
                    match.sets.append(current_set) 
                    
                    p1_w = g1_target
                    p2_w = g2_target
                    while p1_w > 0 or p2_w > 0:
                        if p1_w > 0:
                            g = Game(player_1, match); g.winner = player_1; current_set.games.append(g)
                            p1_w -= 1
                        if p2_w > 0:
                            g = Game(player_2, match); g.winner = player_2; current_set.games.append(g)
                            p2_w -= 1
                    
                    current_set.set_result() 
                    current_set.predict()
                    match.set_result()
                    match.predict()
                # -----------------------------
                
                p1_wins_match = int(match.winner == player_1)
                matches_won += p1_wins_match
                
                for s1, s2, g1, g2, p1_pts, p2_pts, is_p1_serving in match.history:
                    if s1 == s1_target and s2 == s2_target and g1 == g1_target and g2 == g2_target and is_p1_serving == is_p1_serving_target:
                        state_key = (p1_pts, p2_pts)
                        if state_key not in state_wins:
                            state_wins[state_key] = [0, 0]
                        state_wins[state_key][0] += p1_wins_match
                        state_wins[state_key][1] += 1

            st.markdown("---")
            win_rate = matches_won / num_matches
            st.success(f"#### 🏆 Has ganado {matches_won} de {num_matches} partidos (**{win_rate*100:.1f}%**)")
            
            st.markdown("---")
            st.markdown(f"#### 👉 Probabilidad de Ganar el Partido desde {set_filter} (Sets), {game_filter} (Juegos) - {serve_filter}")
            
            if not state_wins:
                st.warning("⚠️ No hay suficientes datos para dibujar este escenario. Prueba a aumentar el número de simulaciones a 10.000 o 20.000.")
            else:
                fig = go.Figure()
                x_coords = []
                y_coords = []
                texts = []
                colors = []
                hover_texts = []
                
                for (p1, p2), stats in state_wins.items():
                    if not is_node_visible(p1, p2, is_tiebreak_target): continue
                    
                    wins, total = stats
                    if total > 0:
                        prob = wins / total
                        points_elapsed = p1 + p2
                        point_diff = p1 - p2 
                        score_label = get_tennis_score_label(p1, p2, is_tiebreak_target)
                        
                        x_coords.append(points_elapsed)
                        y_coords.append(point_diff)
                        texts.append(f"{score_label}<br>{prob*100:.0f}%")
                        colors.append(prob)
                        hover_texts.append(f"Score: {score_label}<br>P(Win): {prob*100:.1f}%")

                if x_coords:
                    fig.add_trace(go.Scatter(
                        x=x_coords, y=y_coords, mode='markers+text',
                        marker=dict(size=40 if not is_tiebreak_target else 25, color=colors, colorscale='RdYlGn', cmin=0, cmax=1, showscale=True, colorbar=dict(title="% Win")),
                        text=texts, textposition="bottom center", textfont=dict(size=12 if not is_tiebreak_target else 10, color="black"),
                        hoverinfo="text", hovertext=hover_texts
                    ))
                    
                    for (p1, p2) in state_wins.keys():
                        if not is_node_visible(p1, p2, is_tiebreak_target): continue
                        
                        pts_elapsed = p1 + p2
                        diff = p1 - p2
                        
                        target1 = (p1+1, p2)
                        if target1 in state_wins and is_node_visible(target1[0], target1[1], is_tiebreak_target):
                            fig.add_shape(type="line", x0=pts_elapsed, y0=diff, x1=pts_elapsed+1, y1=diff+1, line=dict(color="lightgrey", width=1), layer="below")
                        
                        target2 = (p1, p2+1)
                        if target2 in state_wins and is_node_visible(target2[0], target2[1], is_tiebreak_target):
                            fig.add_shape(type="line", x0=pts_elapsed, y0=diff, x1=pts_elapsed+1, y1=diff-1, line=dict(color="lightgrey", width=1), layer="below")

                    fig.update_layout(
                        xaxis=dict(title="Puntos Transcurridos", showgrid=True, zeroline=False, dtick=1),
                        yaxis=dict(showgrid=True, zeroline=True, showticklabels=False, zerolinecolor="black", zerolinewidth=1),
                        height=600 if not is_tiebreak_target else 800, 
                        plot_bgcolor="white", margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Datos insuficientes para trazar la gráfica.")

# ==========================================
# --- NAVEGACIÓN ---
# ==========================================
pagina_1 = st.Page(vista_probabilidad_punto, title="Simulador de Puntos", icon="🎾")
pagina_2 = st.Page(vista_probabilidad_juego, title="Simulador de Juegos", icon="💪")
pagina_3 = st.Page(vista_simulador_partidos, title="Simulador de Partidos", icon="🏆")
pg = st.navigation([pagina_1, pagina_2, pagina_3])
pg.run()