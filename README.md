# Blackjack Engine

A Python-based simulation engine for the card game Blackjack. This project provides a flexible, well-tested framework for building Blackjack games and implementing player strategies.

## Features

- **Card & Deck Management**: Complete card representation with suits, ranks, and values. Multi-deck shoe support with realistic casino mechanics.
- **Player & Dealer**: Flexible player and dealer implementation with hand management.
- **Shuffle Mechanics**: Full deck shuffling with cut card and end-of-shoe markers.
- **Game Framework**: Base game structure for implementing different Blackjack variants.
- **Discard Tray**: Track discarded cards for card counting strategies.
- **Logging**: Comprehensive logging for debugging and monitoring.

## Project Structure

```
blackjack-engine/
├── blackjack/              # Main package
│   ├── card.py            # Card class with suit, rank, and value
│   ├── deck.py            # Deck/shoe management and shuffling
│   ├── hand.py            # Player hand representation
│   ├── player.py          # Player class
│   ├── dealer.py          # Dealer class
│   ├── discard_tray.py    # Discarded cards tracking
│   ├── game.py            # Game orchestration
│   ├── logger.py          # Logging configuration
│   └── __init__.py        # Package exports
├── tests/                 # Unit tests
│   ├── test_card.py
│   ├── test_deck.py
│   └── test_discard_tray.py
├── demo/                  # Demo scripts (TBD)
├── pyproject.toml         # Project configuration
└── README.md             # This file
```

## Installation

### Prerequisites
- Python 3.14+
- pip or uv package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd blackjack-engine

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and dependencies
pip install -e .
```

## Usage

### Basic Setup

```python
from blackjack import Deck, Card, Hand, Player, Dealer

# Create a deck (6-deck shoe)
deck = Deck(size=6)

# Shuffle the deck
deck.shuffle()

# Set cut card (cassino-style)
deck.set_cutcard(pos=100)

# Set end-of-shoe marker
deck.set_end_of_shoe(remaining_min=50, remaining_max=80)

# Draw cards
card = deck.draw()
print(card)  # Output: "2 of Hearts"
```

### Working with Cards

```python
from blackjack import Card

# Create a card
card = Card("Hearts", "King")

# Access properties
print(card.suit)    # "Hearts"
print(card.rank)    # "King"
print(card.value)   # 10

# Ace value is a tuple
ace = Card("Spades", "Ace")
print(ace.value)    # (1, 11)
```

### Game Components

```python
# Create player and dealer
player = Player(name="Alice", initial_bankroll=1000)
dealer = Dealer()

# Create hands
player_hand = Hand()
dealer_hand = Hand()

# Add cards to hand
player_hand.add_card(card)
```

## Testing

Run the test suite using pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_deck.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=blackjack
```

## Development

### Branch Structure
- `main`: Stable release
- `feature/deck`: Deck implementation and mechanics
- `feature/discard_tray`: Discard tray functionality

### Contributing
1. Create a feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass
4. Submit a pull request

## Architecture

### Card System
The `Card` class represents individual playing cards with:
- **Suit**: Hearts, Diamonds, Clubs, Spades
- **Rank**: 2-10, Jack, Queen, King, Ace
- **Value**: Numeric value for game logic (Ace = 1 or 11)

### Deck Management
The `Deck` class handles:
- Multi-deck shoe initialization
- Card shuffling
- Cut card placement (casino-style deck cutting)
- End-of-shoe marker for reshuffle triggers
- Card drawing with validation

### Hand Management
The `Hand` class manages:
- Card collection for a player or dealer
- Hand value calculation
- Blackjack detection

## Dependencies

- **numpy** (≥2.3.5): Numerical operations
- **pytest** (≥9.0.1): Testing framework

## License

MIT License - See LICENSE file for details

## Future Work

- Complete `Game` class implementation
- Demo scripts and examples
- Advanced strategy implementations
- Card counting simulation
- Performance benchmarks
- Additional game variants (Spanish 21, etc.)