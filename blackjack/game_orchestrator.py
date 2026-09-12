"""
game_orchestrator.py

Implements the Blackjack game engine as an explicit phase state machine.

Design principle: the engine NEVER blocks on input()/print() and never runs an
internal "while True" game loop. It only exposes a small, synchronous API:

    game.start()
    game.place_bet(player, amount)
    game.current_actor              -> whose decision is pending (or None)
    game.legal_actions()            -> list[Action] valid right now
    game.act(action)                -> apply exactly one decision

Everything else (dealing, dealer play, payout, reshuffling) happens
automatically inside these calls whenever no decision is required. This
lets the exact same engine be driven by a human CLI loop or by a
reinforcement-learning agent loop without any duplicated game logic.
"""

from dataclasses import dataclass
from enum import Enum, auto

from .card import Card
from .deck import Deck
from .discard_tray import DiscardTray
from .player_dealer import Player, Dealer
from .logger import logger


class Phase(Enum):
    BETTING = auto()
    PLAYER_TURN = auto()
    ROUND_END = auto()


class Action(Enum):
    HIT = auto()
    STAND = auto()
    DOUBLE = auto()
    # SPLIT is intentionally not implemented yet: it requires Player to hold
    # multiple concurrent hands instead of a single one. Left as a TODO.


@dataclass
class RoundResult:
    """Snapshot of one player's outcome, captured just before hands are
    discarded, so any driver (CLI or RL agent) can display/reward it."""

    player: Player
    player_cards: list[Card]
    player_score: int
    dealer_cards: list[Card]
    dealer_score: int
    bet: int
    payout: int

    @property
    def net(self) -> int:
        return self.payout - self.bet


class Game:
    def __init__(
        self,
        players: list[str],
        start_budget: int,
        deck_size: int = 6,
        hit_on_soft_17: bool = False,
    ):
        self._players: list[Player] = [
            Player(name, starting_budget=start_budget) for name in players
        ]
        self._dealer: Dealer = Dealer()
        self._deck: Deck = Deck(deck_size=deck_size)
        self._discard_tray: DiscardTray = DiscardTray()
        self._hit_on_soft_17: bool = hit_on_soft_17

        self._game_started: bool = False
        self._phase: Phase = Phase.BETTING
        self._bets: dict[Player, int] = {}
        self._player_index: int = 0
        self._last_round_results: list[RoundResult] = []

    # ---------------------------------------------
    # Properties
    # ---------------------------------------------
    @property
    def players(self) -> list[Player]:
        return self._players

    @property
    def dealer(self) -> Dealer:
        return self._dealer

    @property
    def deck(self) -> Deck:
        return self._deck

    @property
    def discard_tray(self) -> DiscardTray:
        return self._discard_tray

    @property
    def game_started(self) -> bool:
        return self._game_started

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def current_actor(self) -> Player | None:
        """The player whose decision is currently pending, or None."""
        if self._phase != Phase.PLAYER_TURN:
            return None
        if self._player_index >= len(self._players):
            return None
        return self._players[self._player_index]

    @property
    def last_round_results(self) -> list[RoundResult]:
        """Results of the most recently completed round (empty before any
        round has finished)."""
        return self._last_round_results

    # ---------------------------------------------
    # Setup
    # ---------------------------------------------
    def config(self, **kwargs) -> None:
        if self._game_started:
            raise ArithmeticError("Cannot reconfigure a game that has already started.")

        if "deck_size" in kwargs:
            self._deck = Deck(deck_size=kwargs["deck_size"])

        if "start_budget" in kwargs:
            self._players = [
                Player(player.name, starting_budget=kwargs["start_budget"])
                for player in self._players
            ]

    def start(self, pos_cut_card: int = 100) -> None:
        self._game_started = True
        self._phase_deck_preparation(pos_cut_card)
        self._phase = Phase.BETTING
        logger.info("Game started, waiting for bets.")

    # ---------------------------------------------
    # Betting phase
    # ---------------------------------------------
    def place_bet(self, player: Player, amount: int) -> None:
        if self._phase != Phase.BETTING:
            raise ArithmeticError(f"Cannot place a bet during phase {self._phase}")
        if player not in self._players:
            raise ValueError(f"{player} is not part of this game")
        if player in self._bets:
            raise ArithmeticError(f"{player} has already placed a bet this round")

        player.place_bet(amount)
        self._bets[player] = amount

        if len(self._bets) == len(self._players):
            self._start_round()

    # ---------------------------------------------
    # Round flow (internal)
    # ---------------------------------------------
    def _phase_deck_preparation(self, pos_cut_card: int) -> None:
        self._deck.prepare_shoe(cut_pos=pos_cut_card)
        logger.info("Deck is shuffled and split cards are set")

    def _start_round(self) -> None:
        self._distribute_cards()
        self._phase = Phase.PLAYER_TURN
        self._player_index = 0
        self._advance_to_next_actor()

    def _distribute_cards(self) -> None:
        # Casino order: one card round-robin to each player then the dealer,
        # repeated twice. The dealer's second card stays hidden (see Hand).
        for _ in range(2):
            for player in self._players:
                player.hit(self._deck)
            self._dealer.hit(self._deck)

    def legal_actions(self) -> list[Action]:
        player = self.current_actor
        if player is None:
            return []

        actions = [Action.HIT, Action.STAND]
        can_afford_double = player.budget >= self._bets[player]
        if len(player.hand) == 2 and can_afford_double:
            actions.append(Action.DOUBLE)
        return actions

    def act(self, action: Action) -> None:
        player = self.current_actor
        if player is None:
            raise ArithmeticError("No decision is pending right now.")
        if action not in self.legal_actions():
            raise ValueError(f"Action {action} is not legal right now.")

        if action == Action.HIT:
            player.hit(self._deck)
            if player.hand.bust or player.hand.score == 21:
                player.stand()

        elif action == Action.STAND:
            player.stand()

        elif action == Action.DOUBLE:
            extra = self._bets[player]
            player.place_bet(extra)
            self._bets[player] += extra
            player.hit(self._deck)
            player.stand()

        self._advance_to_next_actor()

    def _advance_to_next_actor(self) -> None:
        while (
            self._player_index < len(self._players)
            and self._players[self._player_index].standing
        ):
            self._player_index += 1

        if self._player_index >= len(self._players):
            self._dealer_phase()
            self._payout_phase()
            self._collect_tray()

    # ---------------------------------------------
    # Dealer + payout
    # ---------------------------------------------
    def _dealer_phase(self) -> None:
        self._dealer.hand.reveal()
        # House rules: always hit below 17. If hit_on_soft_17 is enabled,
        # also hit on a soft 17 (e.g. Ace+6) instead of standing on it.
        while self._dealer.hand.score < 17 or (
            self._hit_on_soft_17
            and self._dealer.hand.score == 17
            and self._dealer.hand.soft
        ):
            self._dealer.hit(self._deck)
        self._dealer.stand()

    def _payout_phase(self) -> None:
        dealer_hand = self._dealer.hand
        self._last_round_results = []
        for player in self._players:
            bet = self._bets[player]
            payout = self._settle(player.hand, dealer_hand, bet)
            player.add_winnings(payout)
            self._last_round_results.append(
                RoundResult(
                    player=player,
                    player_cards=list(player.hand.hand),
                    player_score=player.hand.score,
                    dealer_cards=list(dealer_hand.hand),
                    dealer_score=dealer_hand.score,
                    bet=bet,
                    payout=payout,
                )
            )
        self._phase = Phase.ROUND_END

    @staticmethod
    def _settle(player_hand, dealer_hand, bet: int) -> int:
        if player_hand.bust:
            return 0
        if player_hand.blackjack and not dealer_hand.blackjack:
            return bet + (bet * 3) // 2  # 3:2 blackjack payout
        if dealer_hand.bust:
            return bet * 2
        if player_hand.score > dealer_hand.score:
            return bet * 2
        if player_hand.score == dealer_hand.score:
            return bet  # push
        return 0  # loss

    def _collect_tray(self) -> None:
        for player in self._players:
            self._discard_tray.discard(player.hand.discard())
        self._discard_tray.discard(self._dealer.hand.discard())

        for player in self._players:
            player.reset_for_new_round()
        self._dealer.reset_for_new_round()

        self._bets.clear()
        self._player_index = 0

        if self._deck.end_game:
            self._deck.collect_discard_pile(self._discard_tray.reset())
            self._deck.prepare_shoe()
            logger.info("End of shoe reached: shoe collected and reshuffled.")

        self._phase = Phase.BETTING
