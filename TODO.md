# TODO – Blackjack Simulator

## Card Class
- [X] Represent a single playing card
- [X] Include suit and rank
- [X] Provide method to get card value(s) (consider Ace as 1 or 11)

## Deck Class
- [ ] Contain 6 decks of 52 cards each
- [ ] Implement card-drawing algorithm (deck gets smaller after draw)
- [ ] Handle player and dealer split cards
- [ ] Shuffle when a split occurs
- [ ] Include all cards with their correct values

## Hand Class
- [ ] Distinguish between dealer and player hands
- [ ] Player hand shows all cards
- [ ] Dealer hand shows one card (open) and one card (hidden)
- [ ] Calculate hand values
- [ ] Handle Ace logic (soft/hard)
- [ ] Detect blackjack
- [ ] Detect bust

## Player Class
- [ ] Manage own hand (show hand)
- [ ] Hit (pull a card)
- [ ] Stand
- [ ] Split 
- [ ] Double down
- [ ] Account handling (bankroll)
- [ ] Track statistics

## Dealer Class
- [ ] Manage own hand (show hand)
- [ ] Follow rules for soft 17
- [ ] Reveal hidden card after all players have acted

## Game Class
- [ ] Manage overall game flow
- [ ] Manage rounds and turns
- [ ] Manage multiple players
- [ ] Handle rewards and bets
- [ ] Track rounds and statistics
- [ ] Provide user interface (optional GUI)
- [ ] Distribution logic: deal first to player, then dealer