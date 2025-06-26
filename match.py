from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
from random import random, choice


class TennisPoint(Enum):
    LOVE = 0
    FIFTEEN = 15
    THIRTY = 30
    FORTY = 40
    ADVANTAGE = 'A'
    GAME = 'G'

    @classmethod
    def score_to_point(cls, score: int) -> 'TennisPoint':
        if score >= 3:
            return cls.FORTY
        return [cls.LOVE, cls.FIFTEEN, cls.THIRTY, cls.FORTY][score]


@dataclass
class Player:
    name: str
    delta_on_important_pts: float = 0

    def __str__(self):
        return self.name


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

    def other_player(self, player: Player) -> Player:
        return self.player2 if player == self.player1 else self.player1

    def predict(self):
        """Predict set until is over. Set the winner and result in the
        process."""
        while not self.is_over():
            # This will set the result
            self.predict_set()
        self.set_winner()

    def predict_set(self) -> 'Set':
        _set = Set(self, self.server)
        _set.predict()
        self.sets.append(_set)
        self.set_result()
        return _set

    @property
    def server(self):
        if not self.sets:
            return choice([self.player1, self.player2])
        # This will return the next player to serve
        return self.sets[-1].server

    def is_over(self, set_result: bool = False) -> bool:
        """Check if one of the players won the Match."""
        if set_result or self.result is None:
            self.set_result()
        return any(score >= self.needed_sets for score in self.result)

    def set_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for _set in self.sets:
            if not _set.winner:
                continue
            if _set.winner == self.player1:
                scores[0] += 1
            else:
                scores[1] += 1
        self.result = tuple(scores)
        return self.result

    def set_winner(self):
        """Once the Match is over, set which players win it."""
        self.winner = self.player1 if self.result[0] > self.result[1] \
            else self.player2

    @property
    def needed_sets(self):
        return self.max_sets // 2 + 1

    def formatted_result(self) -> str:
        first_score = self.winner == self.player1
        set_results = ' '.join(
            _set.formatted_result(first_score) for _set in self.sets
        )
        if self.winner is None:
            return set_results
        return f'{self.winner} win: {set_results}'


@dataclass
class Set:
    match: Match
    first_server: Player
    games: List['Game'] = field(default_factory=list)
    result: Tuple[int, int] | None = None
    winner: Player | None = None

    def predict(self):
        """Predict set until is over. Set the winner and result in the
        process."""
        while not self.is_over():
            # This will set the result
            self.predict_game()
        self.set_winner()

    @property
    def server(self) -> Player:
        played_games = sum(1 for game in self.games if game.winner)
        if played_games % 2 == 0:
            return self.first_server
        return self.match.other_player(self.first_server)

    def predict_game(self) -> 'Game':
        game = Game(
            self.server,
            self.match,
            is_tiebreak=self.next_game_is_tie_break())
        game.predict()
        self.games.append(game)
        self.set_result()
        return game

    def set_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for game in self.games:
            if not game.winner:
                continue
            if game.winner == self.match.player1:
                scores[0] += 1
            else:
                scores[1] += 1
            if self.check_if_is_won(*scores) or \
                    self.check_if_is_won(*scores[::-1]):
                break
        self.result = tuple(scores)
        return self.result

    def next_game_is_tie_break(self) -> bool:
        return self.result == (6, 6)

    @staticmethod
    def check_if_is_won(
            first_score: int,
            second_score: int
    ) -> bool:
        return first_score >= 7 or (
                first_score >= 6 and second_score + 2 <= first_score
        )

    def is_over(self, set_result: bool = False) -> bool:
        """Check if one of the players won the Set."""
        if set_result or self.result is None:
            self.set_result()
        return self.check_if_is_won(max(self.result), min(self.result))

    def set_winner(self):
        """Once the set is over, set which players win it."""
        self.winner = self.match.player1 if self.result[0] > self.result[1] \
            else self.match.player2

    @property
    def tie_break_points(self) -> int:
        return self.match.tie_break_points

    def formatted_result(self, player_one_first: bool = True) -> str:
        if player_one_first:
            return f'{self.result[0]}-{self.result[1]}'
        return f'{self.result[1]}-{self.result[0]}'


@dataclass
class Game:
    player_serving: Player
    match: Match
    winner: Player | None = None
    result: Tuple[TennisPoint, TennisPoint] | Tuple[int, int] | None = None
    points: List['Point'] = field(default_factory=list)
    is_tiebreak: bool = False

    def predict(self):
        """Predict game until is over. Set the winner and result in the
        process."""
        while not self.is_over():
            # This will set the result
            self.predict_point()
        self.set_winner()

    def set_winner(self):
        """Once the game is over, set which players win it."""
        winner = self.match.player1
        if self.is_tiebreak:
            if self.result[1] > self.result[0]:
                winner = self.match.player2
        elif self.result[1] == TennisPoint.GAME:
            winner = self.match.player2
        self.winner = winner

    def add_point(self) -> 'Point':
        if any(point.winner is None for point in self.points):
            raise ValueError(
                'Can not add a point if there are still points without winner.'
            )
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
        if not self.is_tiebreak:
            return self.player_serving
        total_points = sum(1 for point in self.points if point.winner)
        # Server changes after every 2 points, starting from the second point
        if ((total_points + 1) // 2) % 2 == 1:
            return self.match.other_player(self.player_serving)
        return self.player_serving

    @property
    def is_critic_point(self) -> bool:
        return False

    def check_if_is_won(
            self,
            first_score: int,
            second_score: int,
            needed_points: int = 4) -> bool:
        """Check if the game is over considering the first score as winner.

        To be clear, this only returns True if the first score wins the game.
        """
        if self.is_tiebreak:
            # Thi may change if set dynamic tie-break points.
            needed_points = self.match.tie_break_points
        return first_score >= needed_points and second_score + 2 <= first_score

    def is_over(self, set_result: bool = False) -> bool:
        """Check if one of the players won the game."""
        if set_result or self.result is None:
            self.set_result()
        if self.is_tiebreak:
            return self.check_if_is_won(max(self.result), min(self.result))
        return TennisPoint.GAME in self.result

    def set_result(self):
        if self.is_tiebreak:
            self.result = self.tie_break_result()
        else:
            self.result = self.normal_game_result()

    def normal_game_result(self) -> Tuple[TennisPoint, TennisPoint]:
        scores = [0, 0]
        for point in self.points:
            if not point.winner:
                continue
            if point.winner == self.match.player1:
                scores[0] += 1
            else:
                scores[1] += 1
            if scores[0] > scores[1] and self.check_if_is_won(*scores):
                return TennisPoint.GAME, TennisPoint.score_to_point(scores[1])
            elif scores[1] > scores[0] and self.check_if_is_won(*scores[::-1]):
                return TennisPoint.score_to_point(scores[0]), TennisPoint.GAME

        return self.get_not_finished_game_result(scores)

    @staticmethod
    def get_not_finished_game_result(
            scores: List[int]) -> Tuple[TennisPoint, TennisPoint]:
        if scores[0] > scores[1] >= 3:
            return TennisPoint.ADVANTAGE, TennisPoint.FORTY
        if scores[1] > scores[0] >= 3:
            return TennisPoint.FORTY, TennisPoint.ADVANTAGE
        if scores[0] == scores[1] > 3:
            return TennisPoint.FORTY, TennisPoint.FORTY
        return (
            TennisPoint.score_to_point(scores[0]),
            TennisPoint.score_to_point(scores[1])
        )

    def tie_break_result(self) -> Tuple[int, int]:
        scores = [0, 0]
        for point in self.points:
            if not point.winner:
                continue
            if point.winner == self.match.player1:
                scores[0] += 1
            else:
                scores[1] += 1
            if self.check_if_is_won(*scores) or \
                    self.check_if_is_won(*scores[::-1]):
                break
        return tuple(scores)

    @property
    def is_break(self):
        return not self.is_tiebreak and self.winner and \
            self.winner != self.serving


@dataclass
class Point:
    winner: Player | None
    serving: Player
    game: Game | None

    def predict(self):
        player_1_wins = random() <= self.get_player_1_probability()
        self.winner = self.player1 if player_1_wins else self.player2
        return self.winner

    @property
    def is_critic_point(self) -> bool:
        return self.game.is_critic_point if self.game else False

    @property
    def player1(self) -> Player:
        return self.game.match.player1

    @property
    def player2(self) -> Player:
        return self.game.match.player2

    def get_player_1_probability(self):
        if self.serving == self.player1:
            probability = self.game.match.probability_1_on_serve
        else:
            probability = self.game.match.probability_1_receiving
        if self.is_critic_point:
            probability += (
                    self.player1.delta_on_important_pts -
                    self.player2.delta_on_important_pts
            )
        return probability


def simulate(win_probability: float, num_simulations: int):
    player_1 = Player('P1')
    player_2 = Player('P2')
    matches = []
    winned_matches = 0
    for _ in range(num_simulations):
        match = Match(
            player_1,
            player_2,
            probability_1_on_serve=win_probability,
            probability_1_receiving=win_probability,
            max_sets=3
        )
        match.predict()
        if match.winner == match.player1:
            winned_matches += 1
    return matches, winned_matches / num_simulations


if __name__ == '__main__':

    _, win_percentage = simulate(0.5, 1000)
    print(win_percentage)
