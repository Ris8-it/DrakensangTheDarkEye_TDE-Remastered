# Thieves' Guild expansion and tougher special enemies (plan, 2 Nov)

The player asked for: four guild jobs from Cano unlocked after Dark Forest, Grimmzahn, Tallon and Murolosh; new gear and
plans for thieves and light fighters that unlock with them (daggers, fencing weapons, throwing weapons, traps, light
shields, gloves, hoods, amulets, greaves, boots), upgrades of the Gloves of Shadow, Iryan-style black leather; and much
tougher special enemies with more attacks, spells, auras and escorts.

## How the guild grows (only mechanics already proven in the pack)

- Cano's own stock is not touched. His two vanilla versions (before/after Grimmzahn) stand in the same hall and the game
  picks one; giving items "to Cano" by name could hit the hidden one (a missing entity is what crashed Flim Flam).
- Instead each finished job brings a new guild member into the hall (parked NPC + TransferEntity, like the Crimson Circle),
  each with their own shop. The hall fills up as the hero rises in the guild.
- Jobs are new options in Cano's vanilla dialog (extend_dialog), each gated by the chapter quest:

| Job | Unlocks after | Where | Gang (arrives on accept) | Brings |
|---|---|---|---|---|
| 1 The Dark Eyes' Strongbox | `Loc03_Main` (Dark Forest) | Ferdok harbour, the old Dark Eye deal spot | Dark Eye remnants: a lieutenant and four thugs | Silas Quickfingers, fence |
| 2 The Grimmzahn Silver | `Burg_Grimmzahn` | Above the Silver Falls | deserters who looted the castle | Ravik Blackstitch, tailor |
| 3 The Silent Hand | `loc08_gerling` (Tallon) | outside Tallon | a rival guild of Tallon | Velane the Shade, blade master (trainer) |
| 4 Aldessia's Hoard | `Loc09_Aldessia` | Murolosh, Aldessia's house | her apprentices, looting it | Old Fox Wendrik, forger |

- Every prize is carried by the gang's boss: the hero can **pick his pocket** (the boss can be robbed; the prize is in his
  stolen-goods table) or **fight the gang** (it drops on death). Bringing it to Cano closes the job: gold, XP, a unique
  piece, and the new guild member walks in.

## Items (armory_data_v28.py, keys `tg_*`)

Stages follow DESIGN_RULES §1/§4 (armour caps by slot and class). Plans have no vanilla seller: the guild members stock them.

- Gloves of Shadow line (vanilla `handschuhe_des_diebes`, arms 1/1, Dexterity bonus): Night Hand (job 1 plan) ->
  Velvet Hand (job 2) -> Shadow Hand (job 3) -> Hands of Phex (job 4, one-off reforge). Each plan consumes the previous pair.
- Nightrunner set (Iryan black leather): hood, jerkin, breeches, boots; plans from Ravik.
- Weapons: guild stiletto, a parrying dagger, a fencing sword, throwing stars and knives; one unique per job.
- Light shields: a cutpurse buckler; amulets of Phex; traps and poisons plans from Velane.

## Tougher special enemies

- Beasts: higher stats, their own species' special moves at higher rates, auras where they fit, and escorts of their kind
  around them (Marsh Queen + troll-toads, Ember Queen + fireflies, Grimtusk + boars, Ashpelt + bears, Broodmother + spiders).
- Humans (Crimson Circle, Rakorium's Echo, the new gangs): bodyguards, full ability sets, and real spells for the casters
  (AE + spell values; the engine casts with simple/clever fighters too).
- Fix: Rakorium's Echo had `Umreissen 1.0.0` (typo, the move never fired).
