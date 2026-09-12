"""
cli.py

A terminal interface for playing Blackjack interactively.

This module contains NO game logic — it only reads input, calls the public
Game engine API (start / place_bet / current_actor / legal_actions / act /
last_round_results), and prints the result. Anything that decides outcomes
lives in game_orchestrator.py, so a future RL agent driver can reuse the
exact same engine without duplicating rules here.
"""

from .game_orchestrator import Game, Action

ACTION_KEYS = {
    "h": Action.HIT,
    "s": Action.STAND,
    "d": Action.DOUBLE,
}
ACTION_LABELS = {
    Action.HIT: "(h)it",
    Action.STAND: "(s)tand",
    Action.DOUBLE: "(d)ouble",
}

MIN_BET = 1
DEFAULT_BUDGET = 1000


def _prompt_int(prompt: str, default: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print("Please enter a whole number.")


def _prompt_players() -> list[str]:
    raw = input("Player name(s), comma separated [You]: ").strip()
    if not raw:
        return ["You"]
    return [name.strip() for name in raw.split(",") if name.strip()]


def _format_cards(cards) -> str:
    return ", ".join(str(card) for card in cards if card) if cards else "(none)"


def _set_cutcard(game: Game) -> None:
    print("\n-- New Shoe --")
    pos_cutcard = _prompt_int(
        f"{game.players[0].name}, please insert the cutcard between 1 and {len(game.deck)}: "
    )
    game._phase_deck_preparation(pos_cutcard)


def _run_betting(game: Game) -> None:
    print("\n-- Betting --")
    for player in game.players:
        while True:
            amount = _prompt_int(
                f"{player.name} (budget {player.budget}), bet amount: "
            )
            try:
                game.place_bet(player, amount)
                break
            except (ValueError, ArithmeticError) as exc:
                print(f"Invalid bet: {exc}")


def _run_player_turns(game: Game) -> None:
    while game.current_actor is not None:
        player = game.current_actor
        print(f"\n{player.name}'s turn")
        print(
            f"  Your hand:    {_format_cards(player.hand.hand)} (score: {player.hand.score})"
        )
        print(f"  Dealer shows: {_format_cards(game.dealer.hand.visible_hand)}")

        actions = game.legal_actions()
        labels = " / ".join(ACTION_LABELS[a] for a in actions)
        while True:
            choice = input(f"  Choose {labels}: ").strip().lower()
            action = ACTION_KEYS.get(choice)
            if action in actions:
                break
            print("  Invalid or unavailable action.")

        game.act(action)

        if player.hand.bust:
            print(f"  {player.name} busts with {player.hand.score}!")


def _print_results(game: Game) -> None:
    results = game.last_round_results
    if not results:
        return

    print("\n-- Round result --")
    print(
        f"Dealer: {_format_cards(results[0].dealer_cards)} (score: {results[0].dealer_score})"
    )

    for result in results:
        if result.net > 0:
            outcome = f"WIN (+{result.net})"
        elif result.net == 0:
            outcome = "PUSH"
        else:
            outcome = f"LOSE ({result.net})"

        print(
            f"  {result.player.name}: {_format_cards(result.player_cards)} "
            f"(score: {result.player_score}) -> {outcome} | budget: {result.player.budget}"
        )


def main() -> None:
    print("=== Blackjack CLI ===")
    names = _prompt_players()
    budget = _prompt_int(
        f"Starting budget per player [{DEFAULT_BUDGET}]: ", default=DEFAULT_BUDGET
    )

    game = Game(players=names, start_budget=budget)
    game.start()
    _set_cutcard(game)

    while True:
        if any(player.budget < MIN_BET for player in game.players):
            # TODO: support seating broke players out instead of ending the
            # whole session; the engine currently requires every player to
            # bet before a round can start.
            print("\nA player is out of budget. Ending session.")
            break

        _run_betting(game)
        _run_player_turns(game)
        _print_results(game)

        again = input("\nPlay another round? [Y/n]: ").strip().lower()
        if again in ("n", "no"):
            break

    print("\n=== Final budgets ===")
    for player in game.players:
        print(f"  {player.name}: {player.budget}")


if __name__ == "__main__":
    main()
