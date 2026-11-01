# Description review

Reviewed all 90 tiered item descriptions against the generator and sampled vanilla
descriptions for Amazon sabers, skrajas, elven bows, staves, rings and mage hats.

Polished 45 lore passages, including every rare and legendary item. Retained
suitable short descriptions elsewhere. Removed misleading promises of guaranteed
hits, unlimited range, kill-triggered visuals, an outnumbered bonus, and other
unsupported behaviour from flavor text. Divine provenance is presented as tradition
or attribution rather than established fact. New lore is original mod fiction,
not a claim to official setting canon.

Custom effect explanations are derived from STATUS data and included with the items
that refer to them. Timed modifiers list their duration. Repeating effects list
pulse count, magnitude, and spacing. Passive bonuses say 'While equipped'.
Regeneration frequency modifiers are labelled as interval reductions rather than
an ambiguous positive speed number.

Checked every tiered item for its expected lore and custom effect descriptions,
literal game newline encoding and valid cp1252 text. Longest generated text:
723 characters. Gameplay/placement SQL and their undo files are byte-identical
to their pre-review versions. Only locale.sql was applied to the live game.
All 428 generated locale rows match the installed database; integrity check: ok.

The updated catalogue includes lore as well as effects. Source lore overrides:
tools/armory_lore.json. Rendering of the longest tooltips still needs an in-game
visual check. No save files were edited.

Locale backup: D:\Steam\steamapps\common\Drakensang\export\db\locale_before_description_review_20261028_214628.db4
