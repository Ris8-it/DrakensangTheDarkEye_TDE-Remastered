# Smarter Foes (optional)

Enemy AI tuning through the game's own state machines (see `docs/ENGINE_ARCHITECTURE.md` section 6).
Every edit is a guarded change of one vanilla statement; Uninstall restores the exact text.

| Machine | Scope | Change |
|---|---|---|
| simple_fighter | 4 statements | wounded -15, casters +15, armour -10, archers +10 (vanilla 0 / 0 / 0 / 0) |
| stupid_fighter | 4 statements | wounded -8 (vanilla 0) |
| lay_bandit | 29 bandit/robber kinds | stupid_fighter + flee once below 20% LE for 8 s |

Works on existing saves (the machines are static data), except the bandit machine on bandits already placed in a save.

## Status: needs an in-game test

1. Target choice of human enemies (they should go for the mage and the wounded).
2. Bandits fleeing (StartEscape inside a transition: vanilla uses StartEscape in a state; the transition statement block is
   the same mechanism vanilla uses 3 times).
