from .deck import Deck
from .discard_tray import DiscardTray
from .player_dealer import Player, Dealer
from .logger import logger


class GameOrchestrator:
    def __init__(
        self,
        players: list[str],
        start_budget: int,
        deck_size: int = 6,
        ai_mode: bool = False,
    ):
        self._players: list[Player] = [
            Player(name, starting_budget=start_budget) for name in players
        ]
        self._dealer: Dealer = Dealer()
        self._deck: Deck = Deck(deck_size=deck_size)
        self._discard_tray: DiscardTray = DiscardTray()
        self._ai_mode: bool = False

    @property
    def player(self) -> list[Player]:
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

    def phase_deck_preparation(self, pos_cut_card) -> None:
        self._deck.shuffle()
        self._deck.set_cutcard(pos=pos_cut_card)
        self._deck.set_end_of_shoe()

        logger.info("Deck is shuffled and split cards are set")

    def phase_bet(self, ai_mode):
        if ai_mode:
            pass
        else:
            pass

    def distribute_cards(self):
        pass

    def step_phase(self):
        pass

    def dealer_phase(self):
        pass

    def payout_phase(self):
        pass

    def collect_tray(self):
        pass
