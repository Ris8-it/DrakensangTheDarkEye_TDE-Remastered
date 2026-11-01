# Drakensang Item Expansion — Design Catalogue (brainstorm v1)

Status: **proposal, nothing built yet** (except the Ravenwing Saber and the Witch Hat fix).
Tags: **[P]** = uses a mechanic the game already uses on items (safe). **[T]** = engine supports the verbs but this use is untested; check it in the Phase 0 test pack first, and use the listed fallback if it fails.
Prices: D = ducats (Value = D × 100). "Found" means placed in chests, loot or pickpocket tables, not shops.

## 0. Design pillars

1. **Gold is scarce (≈1000 D per playthrough).** Shops sell only the "regular" tier (8–40 D). Everything stronger is found: dungeon chests, boss drops, pickpocket tables, or crafted. Sell values stay low (artifacts are worth little to merchants) so loot can't be farmed for gold.
2. **Respect the power curve.** Vanilla tiers: early Amazon Saber 1d6+6 · mid Kangrosha 1d6+6 / Nightwind · late Thaloshrom Skraja 1d6+9 · endgame Wyrm 1d6+8 AT/PA+1, Cyclopean 1d6+10 AT+2, Flamestrike 2d6+8. New items fit between those tiers; only artifacts go above them.
3. **Effects matter more than raw numbers.** The game lacks on-hit identity. Every magic item gets one clear hook: a proc, an aura, a talent focus, or a combo.
4. **Combos between party members.** Gwendala and the hero apply statuses (burning, wound, cold); Rhulana and Forgrimm carry weapons that punish those statuses (`HasStatusEffect` condition). This is new to the game and gives the party synergy.
5. **Built for this party:** hero mage, Rhulana (sabre + shield, bow, healer), Gwendala (elven bow + Blitz/Fulminictus/Armatrutz), Forgrimm (one-handed axe/mace, heavy armour). Other companions get a few pieces so alternative parties still work.
6. **Respect the mg979 class penalties.** Items reward the talent a class is already good at. They don't erase penalties.

---

## 1. Wyrm weapon upgrade (Purplewyrm Japhgur = fire dragon)

Small nudges that keep the stats and give the weapons a dragon identity.

| Weapon | Now | Proposed | Tag |
|---|---|---|---|
| Saber of the Wyrm | 1d6+8 AT+1 PA+1 INI+1, 5% wound | Wound 5→**10%**, plus **10% burning**, plus "Brennen" flash on proc | P |
| Spear of the Wyrm | 2d6+6, 5% wound | Wound **15%** (barbed tooth), **10% burning**, PA+1 | P |
| Bow of the Wyrm | 4d6+2, nothing | **+1d6 fire damage** on hit (Hurt dice, "Ignisphaero_Impact"), **8% burning** | P |
| Crossbow of the Wyrm | 3d6+12, nothing | **20% knockdown** (dragon-sinew punch), **8% burning** | P |
| all four | — | Wielder **immune to burning** (PeNotBurnable). Wyrm-touched. | P |

---

## 2. Ammunition ladder (fills the gap between +2 and Tenobaal's +20)

Crafted with Bowcraft (`rezept_*`). Recipes are sold cheaply (3–10 D) by the Ferdok/Tallon bowyers or found. Arrows and bolts each get a version.

| # | Ammo | Effect | Recipe (per batch) | Batch | Tier | Tag |
|---|---|---|---|---|---|---|
| A1 | Barbed Arrows / Bolts | 25% wound | elm, glue, arrow heads, goose feathers, metal parts | 20 | early | P |
| A2 | Stone-oak Arrows | +3 damage | stone oak, glue ×2, arrow heads ×2, goose | 20 | early-mid | P |
| A3 | Thunderhead Arrows | +1d6 magic damage, "Lightning" | yew, glue, arrow heads, harpy feathers, gemstones | 10 | mid | P |
| A4 | Frostfeather Arrows | +1, 20% Corpofrigo cold shock | yew, glue, arrow heads, harpy feathers ×2 | 10 | mid | T (fallback: +2 and freeze flash) |
| A5 | Sleepthorn Darts | 15% Somnigravis sleep | elm, glue, arrow heads, venom sac, goose | 10 | mid | T (fallback: weak poison) |
| A6 | Dwarven Steel Bolts | +4, 10% knockdown | dwarven steel, bolt heads ×2, glue, goose | 20 | late | P |
| A7 | Elfwood Moonsilver Arrows | +5, ignore cover (flat) | elf wood, gold leaf, harpy feathers, arrow heads | 10 | late | P |
| A8 | Wyrmfang Arrows / Bolts | +10, 15% burning | dragon tooth, dragon sinew, harpy ×3, glue ×3 | 5 | endgame | P |
| A9 | Tenobaal's Arrow | +20 (unchanged) | unchanged (rare recipe) | 5 | legend | — |

Support items: **Fletcher's Kit** (+5 Bowcraft) so Gwendala can craft A6–A8 reliably. Also a **bowyer in Tallon** who stocks A1/A2 in small amounts.

---

## 3. Thirty "regular" magic weapons (the affix family)

The idea is affix families, so magic gear feels systematic, like an ARPG:
- **Prefixes (stats):** Keen +1 TP · Balanced AT+1 INI+1 · Guarding PA+1 · Dwarf-forged BF 0 and +1 TP · Elven INI+2 and lighter · Runed +5 AE.
- **Suffixes (procs):** of Embers (burn) · of Bleeding (wound) · of Venom (poison) · of Thunder (+1d6 magic) · of Felling (knockdown) · of Frost (cold, T) · of Exhaustion (drains AU, T) · of the Leech (heals wielder, T).

### Early: Avestrue, Ferdok, Blood Mountains (8–20 D or found)
| # | Name | Talent | Stats | Effect | Where | Tag |
|---|---|---|---|---|---|---|
| 1 | Keen Saber | Sabre | 1d6+5 INI+1 | +1 dmg on hit | Ferdok weaponsmith 14 D | P |
| 2 | Saber of Embers | Sabre | 1d6+4 | 8% burning | Blood Mountain Ruins chest | P |
| 3 | Guarding Saber | Sabre | 1d6+4 PA+1 | — (shield-friendly) | Golden Lance tavern Amazon (pickpocket) | P |
| 4 | Bleeding Hatchet | Axes | 1d6+4 | 12% wound | Old Mineshaft chest (Avestrue) | P |
| 5 | Dwarf-forged Warhammer | Axes/maces | 1d6+5 BF0 | 8% knockdown | Ferdok smith 18 D | P |
| 6 | Runed Walking Staff | Staves | 1d6+2 PA+1 | +5 AE | Rakorium pickpocket | P |
| 7 | Keen Hunting Bow | Bows | short bow +1 | +1 dmg on hit | Avestrue hunter | P |
| 8 | Viper's Kiss | Daggers | 1d6+2 AT+1 | 10% weapon poison | Cellar Vault chest | P |
| 9 | Short Sword of Thunder | Swords | 1d6+3 | 8% +1d6 magic, "Lightning" | Sewers chest | P |
| 10 | Balanced Longsword | Swords | 1d6+4 AT+1 INI+1 | — | Ducal Citadel armoury | P |

### Mid: Moorbridge, Silver Falls castle, Tallon (found, a few at 25–35 D)
| # | Name | Talent | Stats | Effect | Where | Tag |
|---|---|---|---|---|---|---|
| 11 | Saber of Bleeding | Sabre | 1d6+6 AT+1 | 15% wound | Moorbridge Crypts | P |
| 12 | Rimefang Saber | Sabre | 1d6+6 | 10% Corpofrigo | Castle Vaults | T (fallback: +1d6 cold) |
| 13 | Felling Axe | Axes | 1d6+7 PA-1 | 12% knockdown | Tallon bandit captain loot | P |
| 14 | Ember Axe | Axes | 1d6+6 | 10% burning | Forest Cave chest | P |
| 15 | Thunder Stonesplitter | 2H axes | 2d6+4 | 10% +1d6+2 magic | Stinking Caves | P |
| 16 | Wearying Greataxe | 2H axes | 2d6+3 | drains 3 AU per hit | Tallon ogre camp | T |
| 17 | Spear of Felling | Spears | 2d6+3 | 15% knockdown | Moorbridge Marshes | P |
| 18 | Leech Rapier | Fencing | 1d6+4 AT+1 | heals wielder 1 LE per hit | Silver Falls noble (pickpocket) | T |
| 19 | Ember Longbow | Bows | longbow +1 | 10% burning | Tallon chest | P |
| 20 | Keen War Bow | Bows | war bow +1 | +1 dmg | Tallon bowyer 32 D | P |
| 21 | Felling Light Crossbow | Crossbows | light xbow | 15% knockdown | Castle Inner Ward | P |
| 22 | Staff of Leeching Stars | Staves | 1d6+4 PA+1 | restores 1 AE per hit | Temple of Peraine (Tallon) | T |
| 23 | Throwing Axes of Felling (stack 5) | Throwing | — | 10% knockdown | Murolosh entry merchant | P |

### Late: Murolosh, Deeps of Gruldur, Fire Falls (found only)
| # | Name | Talent | Stats | Effect | Where | Tag |
|---|---|---|---|---|---|---|
| 24 | Ember Battle Axe | Axes | 1d6+8 BF0 | 12% burning | Deeps of Gruldur | P |
| 25 | Runed Skraja of Thunder | Axes | 1d6+8 AT+1 | 10% +1d6+2 magic | Grazima's Storage | P |
| 26 | Saber of Venom | Sabre | 1d6+8 AT+1 | 15% weapon poison | Murolosh black market (pickpocket) | P |
| 27 | Dwarven Bolt-thrower | Crossbows | 2d6+10 | 20% knockdown | Throne Room vault | P |
| 28 | Elven Longbow of Thunder | Bows | 3d6+5 | 10% +1d6 magic | Aldessia's Chambers | P |
| 29 | Andergast Blade of Bleeding | 2H swords | 3d6+3 | 20% wound | Mushroom Garden | P |
| 30 | Archmage's Ember Staff | Staves | 1d6+5 PA+1 | 10% chance to cast Ignifaxius | Behind the Fire Falls | T (fallback: +1d6 fire + burn) |

---

## 4. Ten "good magic effect" items (non-weapon)

| # | Name | Slot | Effect | For | Where | Tag |
|---|---|---|---|---|---|---|
| E1 | Ring of the Astral Well | Ring | AE+10, faster AE regen (Reg_AE_freq −2) | Hero | Temple of Hesinde chest | P (negative freq = faster, per Potion of Power) |
| E2 | Amulet of the Unbowed | Amulet | Immune to knockdown, MU+1 | Gwendala/hero | Blood Mountains | P |
| E3 | Bracers of the Long Shot | Arms | Bows +2, Crossbows +2 | Gwendala/Rhulana | Tallon bowyer quest chest | P |
| E4 | Belt of the Ox | Belt/jewel | KK+1, KO+1, LE+5 | Forgrimm | Murolosh | P |
| E5 | Fox-step Boots | Feet | GE+1, Dodge+1, Sneak+3 | anyone | Cellar Vault | P |
| E6 | Circlet of Clarity | Head | KL+1, IN+1, Magic Lore+3 | Hero | Rakorium pickpocket | P |
| E7 | Gloves of Peraine | Hands | Treat Wounds+4, Treat Poison+2, LE regen | Rhulana (healer 6!) | Temple of Peraine | P |
| E8 | Apron of Ingerimm | Torso (light) | Smithing+5, immune to burning | Forgrimm (crafting) | Murolosh smithy | P |
| E9 | Fletcher's Kit | Ring slot "tool" | Bowcraft+5 | Gwendala | Tallon bowyer 12 D | P |
| E10 | Summoner's Torc | Amulet | Helpful Paw +4, Skelettarius +2, Elemental Servant +2, AE+5 | Hero/Gwendala | Forest Cave (druid hideout) | P |

Helpful Paw note: the torc raises the spell value, which improves the success roll and leftover points. As you said, the level gate on the modifier stays, so it's a quality-of-life item. A separate optional global tweak can make the summoned beasts (`summon_*_01..11`) slightly tougher.

---

## 5. Ten unique items (party-tailored, found only)

| # | Name | Slot | Stats | Hook | Where | Tag |
|---|---|---|---|---|---|---|
| U1 | **Lioness's Claw** | Sabre (Rhulana) | 1d6+9 AT+1 PA+1 | 15% wound; **+1d6 vs burning targets** (combo with Gwendala's fire) | Castle Vaults, Silver Falls | P + T (combo) |
| U2 | **Kurkum Aegis** | Shield | Amazon shield +1 PA | Immune to knockdown, LE+5 | Blood Mountain Ruins boss | P |
| U3 | **Moonthread** | Elven bow (Gwendala) | 4d6+1 reload 1 | Bows +2, **10% Somnigravis** | Moorbridge Crypts | T (fallback: 10% +1d6 magic) |
| U4 | **Shardstring Armguard** | Arms (Gwendala) | — | Blitz +2, Fulminictus +2, AE+5 | Forest Cave | P |
| U5 | **Orcbane** | Axe (Forgrimm) | 1d6+9 BF0 | **+1d6 vs orcs/goblins** (IsRace), MU+1 | Tallon ogre/orc camp | T (fallback: 15% wound) |
| U6 | **Anvil-heart Cuirass** | Torso heavy (Forgrimm) | dwarven chain + RS | Immune to burning, KO+1, LE+10 | Deeps of Gruldur | P |
| U7 | **Staff of the Seven Gazes** | Staff (hero) | 1d6+4 PA+2 | AE+15, Hesinde spells +2, 8% Fulminictus on hit | Temple of Hesinde secret | P + T (cast) |
| U8 | **Song-circlet of the Sala** | Head (hero or Gwendala) | — | Helpful Paw +4, Armatrutz +2, Blitz +2, IN+1 | Elf trainer pickpocket (`rob_unique_npc_elfentrainer`) | P |
| U9 | **Phex's Whisper** | Rapier (Dranor/rogue) | 1d6+5 AT+1 INI+1 | Pickpocket+4, Locks+2, 10% stun | Thieves' Cellar Vault reward | P + T (stun) |
| U10 | **Gardianum Pendant** | Amulet | — | Immune to poison, MR+2, Self-control +3 | Aldessia's Chambers | P (MR is a vanilla ModifyAttribute name) |

---

## 6. Ten endgame sets

There is **no native set-bonus mechanic**. Each piece is strong on its own, and the full set is designed as a build. An optional experiment: the set's main piece checks `HasItem`/`IsInInventory` for the others and adds a bonus **[T]**. Every set gets a shared colour or aura identity through icons.

1. **Sunscale of the Lioness (Rhulana):** Helm (MU+1, immune to fear), Scale Cuirass (RS, LE+10), Bracers (Sabre +2), Greaves (dodge+1), plus U1/U2. *Set idea:* Armatrutz aura while all are worn.
2. **Leafshadow of the Spellweaver (Gwendala):** Circlet (IN+1, AE+5), Jerkin (Sneak+3, light), Bracers (Bows +2), Boots (GE+1), plus Moonthread. *Set:* faster AE regen.
3. **Forgefather's Panoply (Forgrimm):** Dwarven plate pieces each with KK/KO +1, fire immunity on the cuirass, gauntlets with Axes +2, plus Orcbane. Found across Murolosh and Gruldur, so you **don't have to spend the 400 D** on dwarven plate.
4. **Robes of the Hesinde Archon (hero mage):** Hat (KL+1, AE+5), Robe (AE+10, spell resistance), Gloves (Fulminictus/Ignifaxius +2), Boots, Ring of the Astral Well, plus Staff of the Seven Gazes.
5. **Shadow of Phex (rogue):** Hood, Shadow Armour+, Gloves (Pickpocket+3), Boots (Sneak+5), plus Phex's Whisper.
6. **Praios' Radiance (temple/anti-undead):** Mace "Sunburst" (+1d6 vs undead), Helm, Tabard (immune to fear), Shield. Found in Tallon Crypt / Moorbridge Crypts.
7. **Firun's Winter (hunter):** Frost-themed: Rimefang Saber, Frostfeather quiver, white furs (cold resist), +Wilderness lore.
8. **Wyrmhunter's Harness (dragon-themed):** From Japhgur's lair and Parzalon. Wyrm-scale armour (fire immune), Wyrmfang ammo, upgraded Wyrm weapons.
9. **Grolm-crystal Regalia (magic/defence):** Crystal circlet, bracers and amulet with AE, MR and Armatrutz +; dropped by the Grolm king.
10. **Vestments of the Ardakor Cult (cursed power):** Huge bonuses with **drawbacks**, a new idea for this game. For example: Robe AE+25 but LE−10; Dagger 1d6+8 with 20% poison but CH−3; Mask with fear immunity and Horriphobus +4 but Etiquette −5. Dropped by cultists near the end.

---

## 7. Artifacts (god tier, one each, endgame)

| Name | For | Power | Where |
|---|---|---|---|
| **Fang of the Lioness (Rondra)** | Rhulana | Sabre 1d6+12 AT+2 PA+1, 20% wound, 10% knockdown, MU+2, immune to fear, Armatrutz aura | Drakensang Mountain final hoard |
| **First-Forge Hammer of Angrosch** | Forgrimm | Mace 1d6+12 BF0, 15% knockdown, 10% burning, KK+2, immune to burning | Pal'Na'Thar's treasure (Behind the Fire Falls) |
| **Eye of Hesinde** | Hero | Staff 1d6+6 PA+2, AE+30, all spells +1, 10% Fulminictus on hit, blue glow (`Extrofx_Umbracor_Glow_Blue`) | Temple of Hesinde → final chamber |
| **Bow of Sala Mandra** | Gwendala | 4d6+6, no reload, +1d6 magic, 15% sleep, IN+2 | Moorbridge elven ruin, behind a hard lock |
| **Heart-shard of Umbracor** | anyone | Amulet: all attributes +1, AE+20, LE+20, immune to burning, red/blue glow | Dragon's Lair, Japhgur's hoard |

Sell value for artifacts: 1–5 D, so they are kept, not sold.

---

## 8. Consumable coatings (alchemy; reuses the whetstone/balm system)

Ten hits each, crafted from existing ingredients:
- Oil of Embers (20% burn)
- Frost Rime (20% cold, T)
- Thunder Salts (+1d6 magic)
- Bleeding Grit (25% wound)
- Holy Oil (+3 vs undead, T)
- Wyrm-spit Venom (hard poison)

These give mages and alchemists something to brew, and give Rhulana and Forgrimm burst damage in boss fights.

---

## 9. Placement and economy plan

- **Shops:** only regulars #1, 5, 20 and the bowyer stock/recipes (≈100 D total if you buy everything).
- **Found:** about 80% of the items, spread across ~30 dungeon chests, ~10 named-boss loot tables, and ~10 pickpocket tables (the thieves' route is rewarded).
- **Chapter gating** follows the tables above, so power arrives on schedule.
- **Saves:** content needs a new game, or a patched save.

## 10. Icons and visuals

- Icons: 128×128 DXT3 `.dds` in `export\textures\icons\`. Generate art with ChatGPT/Codex image generation in the existing style (item on a parchment square). Convert PNG→DDS with `texconv.exe` (DirectXTex) or ImageMagick, then set `IconBrush`.
- Families share a palette: Embers orange, Frost pale blue, Thunder violet, Wyrm purple-gold, artifacts gilded.
- Auras: permanent status effect with `State_Effect` (Armatrutz/Attributo glow) **[T]**. Glowing weapon models aren't feasible.

## 11. Phase 0: mechanics test pack (do first)

Give it to Rhulana in a new game, alongside the Ravenwing test. One item per [T] mechanic:
1. `RandomChance` syntax with custom % (copy from magical_axe)
2. `SetStatusEffect` corpofrigo / somnigravis / stun / horriphobus from a weapon
3. `CastSpell` Fulminictus from a weapon hit (does it need/consume AE? does it need the spell known?)
4. `Heal` / `RestoreAsP` / `ReduceEndurance` on hit
5. `HasStatusEffect` combo bonus (+1d6 if target burning)
6. `IsRace` bane (vs orc)
7. Aura: permanent effect with `State_Effect`
8. Custom icon `.dds`
9. Set-bonus check via `HasItem`/`IsInInventory` while equipped
10. Armor `ScriptOverride` events (when the wearer is hit?)

## 12. Decisions (user, 2026-10-28)

1. Main hero: **still open.** The user's reply kept the template placeholder `[race + profession]`. Ask again before Phase 3 (hero items, Helpful Paw/Torc targeting).
2. Balance: **a bit stronger than vanilla, still challenging.**
3. Set bonuses: **try the experimental set bonus** (Phase 0 T9). If it fails, ship the pieces independently.
4. Cursed Ardakor set: **in.**
5. Ravenwing Saber: **stays at Cano for 30 D.**

Phase 0 test pack built and installed: `mods/phase0_testpack` (see its README for the in-game checklist; results go into ENGINE_REFERENCE §9).
