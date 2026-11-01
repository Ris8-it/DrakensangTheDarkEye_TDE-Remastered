# New-game setup - 28 October 2026

Player reports all Phase 0b test weapons work. B11 was separately confirmed:
MU +3 while the party possesses its ring; CH +1 when the ring is outside the party.
This is a possession check on amulet equip, not an equipped-set bonus.
Other individual non-weapon Phase 0b tests were not separately confirmed.

## Starting inventory
Removed 13 Phase 0b test items and the Ravenwing Saber test copy from Rhulana's
new-game inventory. Her five ordinary storage entries remain: arrows, bandage,
money, Haumesser, and short bow. Ravenwing remains elsewhere.
The removal is guarded and idempotent in mods/armory/sql/clear_rhulana_tests.sql,
called by Armory Install.bat. Test definitions are retained; only test placement
is removed. Running the test-pack installer again intentionally restores them.
Existing saves were not edited.

## Avestrue shop availability in Ferdok
Avestrue stock is preserved. Additional stock in Praios Square:
- Bow trainer: Huntress' Skinning Knife, Keen Hunting Bow, Hunter's Cap,
  Barbed Arrow instructions, and a 20-arrow stack.
- Weapons merchant: Amazon's Practice Saber.
Prices and effects are unchanged.
The additions are in the source generator/catalogue and generated install/undo SQL.

## Validation
Armory: 104 templates, 72 status effects, 24 loot entries, 83 placed items,
424 mod texts. All three database integrity checks passed.
Chest/NPC/PC owner count mismatches: zero.
Game placement and cleanup SQL were reapplied to check idempotency; Rhulana
still has five ordinary storage entries, and all six vendor entries remain in
both Avestrue and Ferdok.

Full pre-change databases:
D:/Steam/steamapps/common/Drakensang/export/db/before_new_game_20261028_211415

## Artwork
Rare and legendary custom inventory artwork is in assets/armory_icons_v1.
These are inventory-only overrides; original equipped 3D models are unchanged.
The converter writes 128x128 DXT3 DDS files and the Armory builder preserves them.

All 30 rare/legendary custom icons are installed and verified against their template references. Other 60 tiered items retain tinted vanilla icons. Source PNGs, prompts, rollback icons, DDS files, and contact sheet are preserved.
