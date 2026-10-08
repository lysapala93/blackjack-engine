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

from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto

from .card import Card
from .deck import Deck
from .hand import Hand
from .discard_tray import DiscardTray
from .player_dealer import Player, Dealer
from .logger import logger


PEEK_RANKS = ("Ace", "10", "Jack", "Queen", "King")


class Phase(Enum):
    BETTING = auto()
    PLAYER_TURN = auto()
    ROUND_END = auto()
    INSURANCE = auto()
    DEALER_PEEK = auto()


class Action(Enum):
    HIT = auto()
    STAND = auto()
    DOUBLE = auto()
    SPLIT = auto()
    INSURANCE = auto()
    DECLINE_INSURANCE = auto()


@dataclass
class RoundResult:
    """Snapshot of one hand's outcome, captured just before hands are
    discarded, so any driver (CLI or RL agent) can display/reward it.

    A player who split holds several hands, so one round produces one
    RoundResult per hand; `hand_index` tells them apart."""

    player: Player
    hand_index: int
    player_hand: Hand
    player_score: int
    dealer_cards: list[Card]
    dealer_score: int
    bet: int
    payout: int

    @property
    def net(self) -> int:
        return self.payout - self.bet

    @property
    def player_cards(self) -> list[Card]:
        """Cards in the saved hand, retained for callers that only need cards."""
        return list(self.player_hand.hand)


class Game:
    def __init__(
        self,
        players: list[str],
        start_budget: int,
        deck_size: int = 6,
        hit_on_soft_17: bool = False,
        max_splittings: int = 3,
        re_splitting: bool = True,
        insurance: bool = True,
    ):
        self._players: list[Player] = [
            Player(name=name, starting_budget=start_budget) for name in players
        ]
        self._dealer: Dealer = Dealer()
        self._deck: Deck = Deck(deck_size=deck_size)
        self._discard_tray: DiscardTray = DiscardTray()
        self._hit_on_soft_17: bool = hit_on_soft_17

        self._game_started: bool = False
        self._phase: Phase = Phase.BETTING
        self._player_index: int = 0
        self._max_splittings: int = max_splittings
        self._re_splitting: bool = re_splitting
        self._insurance: bool = insurance
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
    def max_splittings(self) -> int:
        return self._max_splittings

    @property
    def re_splitting(self) -> bool:
        return self._re_splitting

    @property
    def insurance(self) -> bool:
        return self._insurance

    @property
    def current_actor(self) -> Player | None:
        """The player whose decision is currently pending, or None."""
        if self._phase not in (Phase.PLAYER_TURN, Phase.INSURANCE):
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
        if player.active_hand.bet != 0:
            raise ArithmeticError(f"{player} has already placed a bet this round")

        player.place_bet(amount)

        if all(participant.active_hand.bet != 0 for participant in self.players):
            self._start_round()

    # ---------------------------------------------
    # Insurance + dealer peek
    # ---------------------------------------------
    @staticmethod
    def _insurance_stake(player: Player) -> int:
        """Insurance is at most half of the original bet."""
        return player.active_hand.bet // 2

    def take_insurance(self, player: Player, amount: int) -> None:
        """Place a custom insurance bet (0 declines), up to half the player's
        bet. Players decide in seating order."""
        if self._phase != Phase.INSURANCE:
            raise ArithmeticError(f"Cannot place insurance during phase {self._phase}")
        if player not in self._players:
            raise ValueError(f"{player} is not part of this game")
        if player is not self.current_actor:
            raise ArithmeticError(f"It is not {player.name}'s turn to decide")

        player.take_insurance(amount)
        self._player_index += 1
        if self._player_index >= len(self._players):
            self._dealer_peek()

    def _decide_insurance(self, player: Player, take: bool) -> None:
        self.take_insurance(player, self._insurance_stake(player) if take else 0)

    def _dealer_peek(self) -> None:
        """Dealer checks the hole card when showing an Ace or a ten-value card.

        With a blackjack the round ends immediately (insurance pays 2:1);
        otherwise insurance is lost and the players' turns begin."""
        self._phase = Phase.DEALER_PEEK
        if self._dealer.active_hand.blackjack:
            logger.info("Dealer has blackjack.")
            self._finish_round()
            return

        self._phase = Phase.PLAYER_TURN
        self._player_index = 0
        self._advance_to_next_actor()

    # ---------------------------------------------
    # Round flow (internal)
    # ---------------------------------------------
    def _phase_deck_preparation(self, pos_cut_card: int) -> None:
        self._deck.prepare_shoe(cut_pos=pos_cut_card)
        logger.info("Deck is shuffled and split cards are set")

    def _start_round(self) -> None:
        self._distribute_cards()
        self._player_index = 0
        up_card = self._dealer.active_hand.visible_hand[0]
        if self._insurance and up_card.rank == "Ace":
            self._phase = Phase.INSURANCE
        elif up_card.rank in PEEK_RANKS:
            self._dealer_peek()
        else:
            self._phase = Phase.PLAYER_TURN
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

        if self._phase == Phase.INSURANCE:
            stake = self._insurance_stake(player)
            if stake > 0 and player.budget >= stake:
                return [Action.INSURANCE, Action.DECLINE_INSURANCE]
            return [Action.DECLINE_INSURANCE]

        actions = [Action.HIT, Action.STAND]
        can_afford_double = player.budget >= player.active_hand.bet
        logger.debug(f"Player {player.name} can affort double: {can_afford_double}")
        if len(player.active_hand) == 2 and can_afford_double:
            logger.debug("Player is able to double")
            actions.append(Action.DOUBLE)
        if (
            player.active_hand.splitting_possible
            and can_afford_double
            and (len(player.hands) <= self.max_splittings)
        ):
            logger.debug("Player is able to split")
            actions.append(Action.SPLIT)
        return actions

    def act(self, action: Action) -> None:
        player = self.current_actor
        if player is None:
            raise ArithmeticError("No decision is pending right now.")
        if action not in self.legal_actions():
            raise ValueError(f"Action {action} is not legal right now.")

        if action in (Action.INSURANCE, Action.DECLINE_INSURANCE):
            self._decide_insurance(player, take=action == Action.INSURANCE)
            return

        if action == Action.HIT:
            player.hit(self._deck)
            if player.active_hand.bust or player.active_hand.score == 21:
                player.stand()

        elif action == Action.STAND:
            player.stand()

        elif action == Action.DOUBLE:
            player.place_bet(player.active_hand.bet)
            player.hit(self._deck)
            player.stand()

        elif action == Action.SPLIT:
            player.split(self._deck)
            player.charge(amount=player.active_hand.bet)
            for hand in player.hands:
                if (
                    not all(card.rank == "Ace" for card in hand)
                    and any(card.rank == "Ace" for card in hand)
                ) or (hand.bust or hand.score == 21):
                    player.stand()
                if not self.re_splitting:
                    player.stand()

        self._advance_to_next_actor()

    def _advance_to_next_actor(self) -> None:
        while self._player_index < len(self._players) and all(
            hand.stand for hand in self._players[self._player_index].hands
        ):
            self._player_index += 1

        if self._player_index >= len(self._players):
            self._finish_round()

    def _finish_round(self) -> None:
        self._dealer_phase()
        self._payout_phase()
        self._collect_tray()

    # ---------------------------------------------
    # Dealer + payout
    # ---------------------------------------------
    def _dealer_phase(self) -> None:
        self._dealer.active_hand.reveal()
        # House rules: always hit below 17. If hit_on_soft_17 is enabled,
        # also hit on a soft 17 (e.g. Ace+6) instead of standing on it.
        while self._dealer.active_hand.score < 17 or (
            self._hit_on_soft_17
            and self._dealer.active_hand.score == 17
            and self._dealer.active_hand.soft
        ):
            self._dealer.hit(self._deck)
        self._dealer.stand()

    def _payout_phase(self) -> None:
        dealer_hand = self._dealer.active_hand
        self._last_round_results = []
        for player in self._players:
            for hand_index, hand in enumerate(player.hands):
                payout = self._settle(hand, dealer_hand, hand.bet)
                insurance = hand.insurance or 0
                if dealer_hand.blackjack:
                    payout += insurance * 3  # stake back plus 2:1
                player.add_winnings(payout)
                self._last_round_results.append(
                    RoundResult(
                        player=player,
                        hand_index=hand_index,
                        player_hand=deepcopy(hand),
                        player_score=hand.score,
                        dealer_cards=list(dealer_hand.hand),
                        dealer_score=dealer_hand.score,
                        bet=hand.bet + insurance,
                        payout=payout,
                    )
                )
        self._phase = Phase.ROUND_END

    @staticmethod
    def _settle(player_hand, dealer_hand, bet: int) -> int:
        if player_hand.bust:
            return 0
        if dealer_hand.blackjack and not player_hand.blackjack:
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
            for hand in player.hands:
                self._discard_tray.discard(hand.discard())
        self._discard_tray.discard(self._dealer.active_hand.discard())

        for player in self._players:
            player.reset_for_new_round()
        self._dealer.reset_for_new_round()

        self._player_index = 0

        if self._deck.end_game:
            self._deck.collect_discard_pile(self._discard_tray.reset())
            self._deck.prepare_shoe()
            logger.info("End of shoe reached: shoe collected and reshuffled.")

        self._phase = Phase.BETTING
