# Drakensang: The Dark Eye — Modding Engine Reference

Everything here was verified by reading the game's own databases (2026-10-28) unless tagged **[T]** (= plausible, must be tested in-game before relying on it).

## 1. Files and install

| What | Where |
|---|---|
| Game (Steam, v1.03, appid 12640) | `D:\Steam\steamapps\common\Drakensang\` |
| Databases (SQLite) | `export\db\static.db4`, `game.db4`, `locale.db4` |
| DB backups | `export\db\*.original` (made by mg979 mod), `export\db_backup_original\` (truly vanilla; sibling of `db`, not inside it), `export\db\ravenwing_backup\` (before Ravenwing), `export\db\phase0_backup\` (before the Phase 0 test pack = vanilla + mg979 + Ravenwing + Ravenwing test copy) |
| Loose-file overrides | `export\textures\icons\*.dds`, `export\gfxlib\...` — loose files override the `.npk` archives (proven: mg979 mod ships icons this way) |
| Profile / saves | `C:\Users\RC\Documents\Drakensang\profiles\default\` — `game.db4` = live world, `save\*\*.dsa` = SQLite copies of game.db4 |
| sqlite3.exe | `C:\Users\RC\Desktop\DrakensangMod2_1b\sqlite3.exe` (also copied into each mod folder). It is **v3.6.1**: no `-readonly`, no table-valued pragmas (`pragma_integrity_check`); use `PRAGMA integrity_check;`. Has `-bail`. Paths with forward slashes work from Git Bash. Kept as the writer because every working mod so far was installed with it |

**Hard rules**
- NEVER modify `drakensang.exe` — Steam DRM rejects it ("Application load error 3:0000065432"). No 4GB/LAA patch.
- Game must be closed when writing DBs.
- New world content (items in chests/shops/companions) only appears in a **new game**, or after patching a specific `.dsa` save (back it up first).
- Steam "Verify integrity" reverts everything.
- `locale.db4` text is **cp1252**; open with `text_factory = lambda b: b.decode('cp1252','replace')`. Newlines in item text are the literal two characters `\n`.
- In this shell, `cmd` won't run `sqlite3.exe` from the cwd because `NoDefaultCurrentDirectoryInExePath=1` is set. Use full paths (`"%~dp0sqlite3.exe"`) in .bat files. Same for running a .bat from Git Bash: `cmd //c call "<full windows path>\Install.bat" nopause`.
- In .bat files call `"%SystemRoot%\System32\find.exe"` / `tasklist.exe` by full path (from Git Bash, `find` resolves to Unix find). Keep .bat files CRLF. Don't edit them with `sed` (it turns `\t`/`\f` in paths into control characters).
- `drakensang.exe` is DRM-packed: no readable strings, so engine event names can't be read from it.
- Installed on top: mg979 "Gameplay Additions" v2.1b (mild preset) — class-specific weapon/talent penalties, reworked loot, Ergo's items. Our mods must be applied *after* it.

## 2. Currency

`Value` is in **heller**: 100 = 1 ducat (D). Calibration: dwarven heavy set ≈ 22000+5600+5000+3500+3300 ≈ 394 D (user says ≈400 D). A full playthrough earns ≈ **1000 D total**. Merchants buy at `PurchaseFactor` (usually 0.5). Keep sell values modest or new loot becomes a money exploit.

Reference prices: Amazon Saber 2000 (20 D), Longsword 700, Longbow 600, Andergast Blade 5000, Ring of astral accumulation 3500, Dwarven Plate 22000.

## 3. Item data model

| Layer | Table | Key columns |
|---|---|---|
| Definition | `static.db4: _Template_Weapon / _Armor / _Jewelry / _Shield / _Ammo / _Item / _Recipe` | `Id`, `Graphics`, `Physics`, `IconBrush`, `LookAtText`, `InfoIdentified`, `Value`, `Gew` (weight), `PermanentEffect`, `ScriptOverride`, `LimitedScript`, `IsMagical`, `IdentificationDifficulty`, `IsIdentified` |
| Weapon stats | same | `TaAttr` (talent), `EquipmentType` (OneHandWeapon/TwoHandWeapon), `WeaponAnimGroup`, `WpW6`/`WpW6plus` (dice/flat TP), `WpTPKK1/2` (strength bonus), `WpATmod`, `WpPAmod`, `WpINI`, `WpBF` (break factor), `WpDK` (distance class), `WpATRange`, `WpReload`, `WpAmmoCategory` |
| Text | `locale.db4: _Locale(LocaId PK, LocaText)` | `lookat_<id>` (name), `infoid_<id>` (description) |
| World placement | `game.db4: _Instance_<Type>` | full copy of template columns + `Guid` (16-byte PK, ON CONFLICT REPLACE!), `_Level`, `Transform`, `StorageGUID` (owner's Guid) |

**Placing an item in an inventory (merchant, chest, companion):** insert an `_Instance_*` row with `StorageGUID` = owner's `Guid`, and `UPDATE <owner table> SET StorageContentCount = StorageContentCount + 1`. Merchant infinite stacks use `StackCount = -1`.
**Guid collisions silently overwrite** (the mg979 mod lost its Witch Hat this way). Always use deterministic unique GUIDs, e.g. `uuid.uuid5(NAMESPACE_URL, 'drakensang/<item>/<owner>')`, and `INSERT OR IGNORE` + guarded count updates so installs are idempotent.

Other placement channels:
- `_DSA_LootTables(LootTableName, LootTableValue, LootTableContent)` — content format `Type/Id/chancePercent/amount/value/;` e.g. `Jewelry/ring_ff/100/1/2500/;`. Amount can be dice: `w6+4`.
- Pickpocket: each NPC has `StolenGoodsTable` → a loot table. 48 unique ones: `rob_unique_cuano, _rakorium, _arombolosch, _aldessia, _xolgorax, _parzalon, _thalya, _traldar, _grossinquisitor_da_vanya, _ingerimm_geweihter, _barla_dorkenschmied, ...`
- Monsters: `_Template_Monster/_Instance_Monster` columns `LootTable`, `SetupStorage`, `StolenGoodsTable`, `FurriersLootTable`, `IsLootable`.
- Chests: `_Instance_Chest` (+ `SetupStorage` on templates), placement by StorageGUID like merchants.
- Recipes: `_Template_Recipe.RecipeIngredients = 'Item/<id>/<n>;...'`, `RecipeResult = 'Ammo/<id>/<n>'`, `TaAttr`, `Difficulty`.

## 4. Scripts are data

Tables (static.db4): `_Scripts_ActionScripts(ScriptName, StatementRef, StatementBlock)`, `_Scripts_StatusEffectScripts`, `_Scripts_ConditionScripts`, `_Scripts_Statements(StatementGUID, StatementType, StatementContent, StatementBlockGUID)`, `_Scripts_Conditions(ConditionGUID, ConditionType, ConditionContent, ConditionBlockGUID)`, `_Template_LimitedScripts`.

Statement types: `Begin`, `Action`, `If`, `Then`, `Else`, `Condition` (references are `guid;guid` strings). Condition rows are `Atom` (a test), `Not`, `And`, `Or` or `Condition` (reference).

### Row encoding (decoded from magical_axe, zauberstab, waquiff, chargeble_*; decoder `tools/research/decode1.py`, `decode2.py`)
- Every PK in the script/template tables is `PRIMARY KEY ON CONFLICT REPLACE`. A plain INSERT with the same key replaces the row (so it's idempotent), and a colliding GUID **silently overwrites vanilla**. Check for collisions before generating.
- Blobs are 16-byte GUIDs. Text references are the **.NET GUID string of the blob** = `str(uuid.UUID(bytes_le=blob))` (lowercase, dashed). To write: `blob = u.bytes_le`, `ref = str(u)`.
- `_Scripts_ActionScripts(ScriptName, StatementRef = the Begin statement, StatementBlock = B)`. All statements of the script have `StatementBlockGUID = B`.
- `Begin` content = `child;child;…` (sequence). `Then`/`Else` content = `child;…`. `If` content = `<Condition stmt>;<Then>[;<Else>]`.
- `Condition` **statement** content = `<top condition row>;<condition block>`. Condition rows: `Atom` (the test), optionally `Not` → atom (or `And`/`Or` → `a;b;…`), and a final `Condition` row → top. All the rows of one If share one `ConditionBlockGUID`.
- One `Action` row may hold several verbs: `Hurt …; PlayVisualEffect …; ` (each ends with `; `; atoms end with `; ` too).
- Vanilla writes rows children-first (Condition stmt, Action, Then, If, Begin).
- Status-effect script (`_Scripts_StatusEffectScripts`: Guid, Id, Start/Trigger/Stop Ref+Block): each part is its own block with its own Begin. PeAE10 = Start `ModifyAttribute`, Trigger `WaitAction duration="1" permanent="true"`, Stop all-zero blobs. No Stop block is needed: modifiers are reverted on unequip. Plus a `_Template_Statuseffects` row (Id, State_Effect, State_Hardpoint, State_Texture, State_Categories='permanentEffect', Name/ShortDescription/LongDescription locale keys `<Id>_name/_short/_long`, State_Immunity).
- **Immunities are data, not script:** `PeNotBurnable` / `PeHelmOfFlames` have `State_Immunity='fire'`, `PeImmuneToKnockdown` has `'overthrown'`, `PeImmuneToPoison1` has `'poison'` (+ category `immunToPoison`).
- `tools/build_phase0.py` has a `Block` builder class that reproduces all of this; reuse it.

### Hooks
- Weapon/Ammo `ScriptOverride = 'on:Hit:<ActionScriptName>'` — runs on every hit.
- Any equipment `PermanentEffect = 'A;B'` — status-effect scripts that run while equipped (Start block applies, Trigger loops `WaitAction permanent="true"`).
- Consumable coatings: item `LimitedScript = 'Weapon_add_schleifstein:-1'` → action `AttachActionScript limitedScriptID="Weapon_schleifstein" charge="10" targetEntity="AimedEntity"` → per-hit script.
- Armor/Jewelry also have `ScriptOverride`; which events fire for them is unknown **[T]** (Phase 0 T10). Events actually used in vanilla data: Item `on:Use`, Trap `on:TriggerTrap`, Weapon/Ammo `on:Hit`, DestroyableEntity `on:Death`. No armour or jewelry uses ScriptOverride.

### Proven examples (copy these patterns)
```
PeAE10        Start: ModifyAttribute modifier="AEmax +10"
Dom2AE5       Start: ModifyAttribute modifier="AEmax +5 ZaHorriphobus +2 ZaHerrUeberDasTierreich +2 ZaSanftmut +2 ZaSomnigravis +2"
PeWpPA2       Start: ModifyAttribute modifier="PA +1"
generic_dmg_2 Hurt who="AimedEntity" fixedDamage="2" dice="6" diceAmount="0" showNoDamage="true"
tenobaal      Hurt ... fixedDamage="20"
zauberstab (Soulsplitter) Hurt who="AimedEntity" fixedDamage="0" dice="6" diceAmount="1" effect="Fulminictus_Impact" damageType="magic"
waffenbalsam  Hurt ... fixedDamage="1" ...; PlayVisualEffect effect="Waffen_Balsam" target="AimedEntity"
magical_axe   If(RandomChance percent="5") Then SetStatusEffect who="AimedEntity" id="wound"   (Wyrm saber & spear, hunting arrows/bolts)
magiscal_sword 25% wound · traldars_sword 50% wound · gotterdammerung 50% overthrown (same shape)
chargeble_burn.xml  If(Not HasStatusEffect category="immunToFire" who="AimedEntity") SetStatusEffect id="burning"   (no chance roll: every hit; fire arrows)
nasreddins_waquiff  If True → If Not immuneToPoison → If Not Probe KO 8 → SetStatusEffect id="poison_weapon"
grolmenhammer   SetStatusEffect who="AimedEntity" id="blitzDichFind"; ReduceEndurance who="ActingEntity" fixedDamage="0" dice="6" diceAmount="3" consoleOutputType="Item_Grolm_Weapon"   (enemy weapon: blinds target, drains wielder)
chargeble_fulminictus.xml  If(IsInRange entity="ActingEntity" target="AimedEntity" range="49") CastSpell who="ActingEntity" spellId="FulminictusDonnerkeil" target="AimedEntity" zfpUnused="5"
```
Exact action syntax seen in vanilla (copy verbatim):
```
Heal who="ActingEntity" fixedLE="1" dice="6" diceAmount="2" effect="Heal_Impact" consoleOutputType="Item_HealingPotion" actionSelection="script,quest,dialog";
RestoreAsP who="ActingEntity" fixedAsP="20" dice="0" diceAmount="0" consoleOutputType="Item_SpellPotion" actionSelection="script";
RestoreAU who="ActingEntity" fixedAU="15" dice="0" diceAmount="0" consoleOutputType="Item_Dark_Beer" actionSelection="script";
ReduceEndurance [who=…] fixedDamage="2" dice="6" diceAmount="2" consoleOutputType="Poison_Wound_Soft" …;
ShowOverHeadMessage msg="literal text" who="AimedEntity";
AttachPermanentEffect permanentEffectID="PeKnauf" actionSelection="script";
```
- `Hurt damageType=` values in vanilla: `physical`, `magic`, `fire`, `poison`. So "+1d6 fire" is **[P]**.
- `consoleOutputType="X"` prints locale `Console_Output_<Verb>_X` in the combat log (e.g. `Console_Output_Reduce_Endurance_Item_Grolm_Weapon` = "Grolm Weapon"). It's a free in-game readout for testing.
- Condition syntax: `RandomChance percent="N"` (vanilla uses 5…50). `HasStatusEffect` works by `id="burning" who="X"` or `category="fire" who="AimedEntity"` (+ optional `everybody=`, `amount=`). `IsRace who="…" race="Zwerg"`. `HasItem owner="PlayerParty" templateId="x" category="Item|Ammo|Book|Key|Money|Recipe" amount="1"` or `storable="x"`. `IsInInventory category="Item" templateId="x"`. `HealthCritical percent="0.25"`. `IsInRange entity= target= range=`. `Probe who= difficulty= attribute="KO"`. No "is equipped" atom exists (75 atoms, list via research scripts).
- **Race values** (`Race` column on NPC only; beasts/monsters have none): `Mittellaender`, `Zwerg`, `Elf`, `Tulamide`, `Thorwaler`, `Ork`, `Goblin`, `Oger`, `Troll`, `Grolm`, `Untoter`, `Kultist`, `Mantrake`, `Mensch`, `Wuehlschrat`, `Kobold`. Avestrue robbers (`Raeuber*_loc01`, FaFeind) are Mittellaender.
`ModifyAttribute` accepts any attribute name with `+N`/`-N`, several per string. Names used in vanilla: AEmax, AUmax, LEmax, MR, AT, PA, ATbasis, PAbasis, ATW6, FK, FKbasis, AW, MU, KL, IN, CH, FF, GE, KO, KK, Reg_AE/AU/LE, Reg_AE/AU/LE_freq, Ta* (talents, e.g. TaBogen, TaArmbrust, TaSchmieden), Za* (spells). **`Reg_*_freq` negative = faster regeneration** (Potion of Power: `Reg_LE_freq -5 Reg_AE_freq -5 Reg_AU_freq -3 ATW6 +1`).

### Action verbs available (137)
Combat-relevant: `Hurt`, `Heal`, `RestoreAsP`, `RestoreAU`, `ReduceEndurance`, `SetStatusEffect`, `RemoveStatusEffect`, `AttachPermanentEffect`, `AttachActionScript`, `CastSpell`, `ObjectSpell`, `ModifyAttribute`, `PlayVisualEffect`, `StopVisualEffect`, `PlaySound`, `PlayShakeEffect`, `ShowOverHeadMessage`, `PrintConsole`, `RunActionScript`, `RunActionScriptInRadius`, `RunScriptOnAllInside`, `CreateEntity`, `SpawnAtEncounter`, `Give`, `GiveGold`, `TeleportEntity`, `UseTalent`, `RandCounter`, `AddToCounter`, `StartTimer`.
Full list: ActivateBlockade … WaitForCondition (see research output in tools/).

### Condition atoms
`RandomChance`, `Probe` (talent/attribute check), `HasStatusEffect`, `HealthCritical percent="0.25"`, `IsRace`, `HasItem`, `IsInInventory`, `HasTalent`, `IsCombat`, `IsAttackedInMelee`, `TargetInCloseRange`, `CompareCounter`, `HasCharge`, `IsDead`, `IsPartyMember`, … (75 total).

### Status effects usable as debuffs (`SetStatusEffect id=`)
Proven from items: `wound`, `burning`, `poison_weapon`, `overthrown`, `blitzDichFind` (Grolm hammer, an enemy weapon).
Spell states (set by spells — via item **[T]**): `corpofrigo` (cold shock), `plumbarum` (heavy arm), `eisenrost` (iron rust), `horriphobus` (fear), `blitzDichFind` (blinded), `somnigravis` (sleep), `paralys`, `stun`, `sanftmut`, `duplicatus`.
Poisons: `poison_spider`, `poison_spider_smaragd`, `poison_giant_scorpio`, `wurmspeichel` (hard), `drachenspeichel2`, `feuermoos`, `poison_wound_soft/hard`, `angstgift2`.
Buffs (for self-procs): `axxeleratus`, `armatrutz`, `regeneration`, `kampfrausch` (bloodlust), `klingenwand`, `meisterparade`, `counterattack`, `attributoXX`.

### Visual effects
On-hit (`PlayVisualEffect effect=`): `Waffen_Balsam`, `Waffen_Schleifstein`, `Waffen_Diamant`, `Fulminictus_Impact`, `Ignisphaero_Impact`, `Corpofrigo_Impact`, `Kulminatio_Impact`, `Skelettarius_Impact`, `Heal_Impact`, `Balsam_Impact`, `Gift_Impact`, `Lightning`, `Brennen`, `Niederwerfen`, `Elementar_Explode`, `Glitzer01`, `Japhgur_Fernkampf`, `Kraeheneffekt`, `Grolm_Kristalleffekt`.
Persistent glows **[T]**: `Extrofx_Umbracor_Glow_Blue`, `Extrofx_Ardacor_Glow_Red`, `Extrofx_Sonnenstrahlen`.
Character-attached states (`_Template_Statuseffects.State_Effect` + `State_Hardpoint`): `Armatrutz_State`(Damage_Torso), `AttributoXX_State`, `Axxeleratus_State`, `Balsam_State`, `Eiseskaelte_State`, `Falkenauge_State`(Head), `AdleraugeLuchsenohr_State`(Head), `Psychostabilis_State`, `Favilludo_State`, `Kampf_Offensiv1`, `Kampf_Defensiv1`. Giving an item's permanent status effect a `State_Effect` = **aura while equipped [T]**. Vanilla has one permanent effect with a visual, `PeFendral` (`Favilludo_State`, Skeleton_Root), but no item uses it. The `Extrofx_*` glows are `PlayVisualEffect` names from the ending cutscene; `State_Effect` and `PlayVisualEffect` draw from the same pool (`Brennen` is used as both). Monsters also have an `AuraStatuseffect` column.

## 5. Spells and summons
- Spell attribute names: `Za<Name>`, e.g. `ZaTatzeSchwinge` (Helpful Paw — elvish spell, `SkillRequirements CasterRace/elvish;CasterType/fullmage`, `ZaModMax='Level'`).
- Spell rank logic is hard-coded (`ZaClass Game::...`). Per the user: the modifier rank is gated by character level (Paw: up to +11; Armatrutz: one step per 3 levels, max +5 at L15). Items raising `Za*` raise the spell value (success, ZfP*) but not the level gate.
- Paw summons are plain monster templates `summon_wolfsratte_01/02, summon_wolf_03/04, summon_wildschwein_05..07, summon_baer_08..10, summon_tier_11` — their stats can be buffed globally.
- CastSpell ids seen: `FulminictusDonnerkeil`, `IgnifaxiusFlammenstrahl`, `BalsamSalabunde`, `AxxeleratusBlitzgeschwind`, `ForamenForaminor`, `AttributoCH`.

## 6. Party (vanilla start values)
| Id | Who | Notable |
|---|---|---|
| `pc_rhulana` (location01) | Amazon | Sabre 4, Bow 4, Treat Wounds 6, AE 0 |
| `pc_gwendala` (location04) | Elf Zauberweber (spellweaver), L5 | Bow 4, Blitz 4, Fulminictus 3, Armatrutz 3, AE 30 |
| `pc_forgrimm` | Dwarf mercenary | Axes/maces 5, 2H axes 2, KK 16, KO 15 |
| main hero | user's mage | tradition/race to confirm |

## 7. Icons
`IconBrush = 'icons/<name>'` → `export\textures\icons\<name>.dds`, **128×128 DXT3 with 8 mip levels** (header flags 0xA1007, linear size 16384; file = 22000 bytes). Existing icon style: item on a parchment/beige square. Pillow 12 reads these and writes DXT3 but no mips. `build_phase0.py` reuses a vanilla 128-byte header and appends 8 Pillow-encoded DXT3 levels (the 2×2 and 1×1 levels are encoded from a 4×4 image). Loose-file icon from our own mod = Phase 0 T8 **[T]**.

## 8. Locations (English)
location01 Avestrue · location02_* Ferdok (Wagoner's Home, Ducal Citadel, Ugdan Harbor, Praios Square) · dungeon02_diebesgilde Cellar Vault (thieves) · location03 Blood Mountains · location04 Moorbridge Marshes (dungeon04_gruft Moorbridge Crypts) · location05 Above the Silver Falls (dungeon05_burg Castle Vaults) · location08 Tallon (dungeon08_gruft_01 Crypt, dungeon08_bestie Stinking Caves, location08_drachenhort Dragon's Lair) · location09 Murolosh (dwarves) · location10 Deeps of Gruldur · location11 Behind the Fire Falls (Pal'Na'Thar) · location12 Drakensang Mountain · location_zufall_07 Eastern Kosh.

## 9. Runtime results (player-tested) and rules derived from them

Phase 0 (2026-10-28) and 0b (reported 2026-10-28/30). "Proven" = observed in-game by the player.

| Mechanic | Result |
|---|---|
| Cloned weapon/ring templates, vanilla on:Hit and Pe on new items (C1-C3) | **Proven** |
| New script rows, vanilla shape, RandomChance (T1) | **Proven** |
| `SetStatusEffect` corpofrigo, stun (T2a/c) | **Proven** |
| `SetStatusEffect` somnigravis, horriphobus (T2b/d) | **CRASH** ("StatusEffectManager::CreateSEByName ... can't be found"). Spell-only states are not creatable. |
| `CastSpell` from a weapon (T3) | **Failed**: needs the spell known and queues it as the next action. Do not use. |
| Heal / RestoreAsP on wielder (T4a/b) | **Proven** |
| ReduceEndurance on enemies (T4c) | Works but useless (enemies show 1/1 AU) |
| `HasStatusEffect id="burning"` combo (T5) | **Proven** (fire burst) |
| `IsRace` (T6, 0b B6) | No false positive on wolves; 0b weapons reported working. Use only as a bonus layer. |
| Pe with `State_Effect` aura (T7a Armatrutz_State) | **Proven**. `Extrofx_*` cutscene effects as State_Effect: no glow (T7b). |
| Custom loose icon DDS (T8) | **Proven** |
| `If` inside a status-effect Start block WITHOUT Else (T9) | **CRASH**: NEBULA ASSERTION `this->HasElseBlock()` (ifthenelseaction.cc:232). Vanilla never uses Ifs there. |
| Same check WITH Else (0b B11) | **Proven**: HasItem owner="PlayerParty" works on amulet equip (possession, not equipped-set). |
| Armour `ScriptOverride` on:Hit (T10) | **Never fires**. |
| Custom timed debuffs/DoT/self-buffs via SetStatusEffect, weapon Pe + ScriptOverride together (0b B1-B5) | **Proven** (all 0b weapons work) |
| Custom Marked Prey (p1_marked) | Player saw no indication; unverified. Removed in v2. |
| **Custom permanent effects in weapon/armour tooltips** | **SOLVED 2026-10-30** (armour diagnostic A-I): the Id must not contain an underscore. `PeArRv_C` shows "StatusEffect (null) not found"; `PeArRvB`, long Ids, shared text keys, NULL fields, stackability all render with the custom name. All v1 effects were `PeArm_<key>`. |

**Rules (v2 generator enforces them):**
- Every custom status/permanent-effect Id: letters and digits only (dsa.status asserts). Prefer native ids first (vanilla text), then ONE custom effect for the rest; its Name is the green tooltip line.
- Native composition (exact, multi-attribute first: PeMagicHat = AE+10 MR+2, PeMagicRobe = Reg_AE+1, PeKK1-3/PeMU1-3/... per attribute, PeAE10/PeLE10/PeAU10, PeWpPA2 = PA+1, PeAW1/2 = Dodge, talents PeSledge2/PeSledge (Smithing 3/6), PeAlchimie3, PeBowCraftKnife (Bowcraft 3), PeMagiekunde1 (Arcane lore 5), PeEtikette1, PeTaschendieb1 (Pickpocket 2), PeSkinningKnife (Animal lore 3); immunities PeNotBurnable/PeImmuneToKnockdown/PeImmuneToPoison1). Full list: tools/research/out/native_pe.txt.
- Jewelry: custom effects and auras allowed (no effect list in its tooltip).
- Never set somnigravis/horriphobus/other spell states. Creatable: wound, burning, poison_weapon, overthrown, corpofrigo, stun, blitzDichFind + any custom scripted status.
- Status-effect scripts: no If without Else.
- Named enemies' carried storage is probably equipment, not loot (cultists carry a cleaver but drop daggers from `LootTable`). Put boss rewards in the NPC's `loot_unique_*` table.
- Loot tables: `LootTableValue` = number of entries drawn; to guarantee an added entry raise it to (entries incl. ours). **Value 0 does NOT roll every entry** (Marsh Pearl and Crab Shell Plate never dropped, 2 Nov): the builders now always set it to the entry count.
- Native recipes consume Weapon/Armor/Shield ingredients (`Weapon/Langbogen/1`); jewelry ingredients untested.
- Item text: vanilla uses literal `
`; keep descriptions compact (lore + bonuses + procs).
- Icons: vanilla icons are 128x128 DXT3, no mips (export_1.npk textures/icons, extract with tools/npk.py). Pillow's DXT3 encoder hatches gradients; use dsa.encode_dxt3. Judge icons on parchment (tools/preview_icons.py).

## 10. Character creation (Arcane Thief research, 2026-10-30)
- Archetypes: `_Template_PC_CharWizard` (Id `archetype_<RACE>_<PROF>_<M|W>`). Magic = `CasterType` none/halfmage/fullmage + `IsMagicUser` + AE/AEmax + MR.
- Spells: `_Template_Zauber.SkillRequirements` gates learning (`CasterRace/human|elvish`, `CasterType/fullmage` for 10 big spells). `Za*=-500` on an archetype = not known yet (learnable at trainers).
- `Advantages` = mg979 class rules from `_Template_Advantages.AttributeModifier` (`zz_thieves`, `zz_mm_casters`, `z_battlemage` ...: talent/spell/attribute deltas).
- `SetupStorage` = starting pack (`Type/Id[:count]/false/false;`).
- Off-hand slot holds only `_Template_Shield` items. Non-shield meshes (torch, dagger) in a shield template attach at the shield mount and hang **sideways** (Phase 0c, player-tested 2026-10-30). Do not use; off-hands = bucklers/small shields only.
- Pal'Na'Thar (`Zyklop`, location11): CanRob 1 but empty StolenGoodsTable: nothing to steal.

## 11. Story: NPCs, dialogues and quests (research 2026-10-30; builder tools/quests.py)
- **Dialogues** (static): `_Story_Dialogs(DialogId, DialogSpeaker = NPC Name)`, one `_Story_DialogTakes` row per line (StartState / Take = NPC / Response = player), text in `_Locale` under `str(uuid(bytes_le=TakeLocaId))`. Unvoiced lines: TakeSound '', TakeSoundActiv 0, TakeTimeStamp 0. Tree = `_Story_DialogTakeChildMapping` (TakeGUID, TakeChildId, position; **no primary key**: delete exactly your own pairs). StartState children: first whose condition passes. game.db4 needs `_Story_Dialogs(DialogId,0)` and `_Story_DialogTakeStatus(DialogId+TakeId,0)`.
- **Takes never chain to Takes.** Companion interjection = Take -> Response `<Next>` -> Take with `TakeSpeaker` = companion Name (`Rhulana`, `Forgrimm_Sohn_des_Ferolax`, `pc_gwendala`, `Kladdis_Schladromir`, `Dranor_PC`) and condition `IsPartyMember who="..."`.
- **Extending a vanilla dialogue:** add our takes with the vanilla DialogGUID and hang responses under existing takes (position 20+). Rakorium in the Ferdok house (`loc02_rakorium`) has 5 greeting hubs (FirstGreeting, Greeting_nach_03/05/08, one GUID) sharing the same answers: good for whole-game quests.
- **Tasks:** parent quest (TaskParentGuid zero) + child steps; open/close condition blocks (top row OpenCondition / CloseCondition), open/close action rows. game.db4 `_Story_Tasks(TaskId, TaskState)`. `IsDead who="<Name>"` in a close condition works without dialogue (118 vanilla uses).
- **Useful verbs:** `CreateEntity category=.. templateId=.. how="spawnInStorage" entity="Hero" number=n`, `CreateEntity category="NPC" templateId=<_Template_NPC> how="spawnAtEntity" entity=<Name>` (ambushes), `GiveAmount to=<npc> templateId category amount` (take from player), `GiveGold amount=<heller>` (no way to take money), `GiveQuestXp questXp=` (vanilla 5-50, big 100-300), `SetFaction faction="FaFeind" who=<Name>` (turn hostile; 205 vanilla uses), `EquipBestCloseRangeWeapon who=`, `ShowTradeUI trader=`, `StartConversation`, `LockDialog/UnlockDialog`, `PlayCutscene`.
- **Conditions:** TalkedAbout, IsTaskUnLocked/Closed, IsQuestUnLocked/Closed (gate by vanilla chapter, e.g. `IsQuestClosed quest="Burg_Grimmzahn"`), HasAmount, IsInInventory, IsDead, IsGroupDead, IsPartyMember, Probe, HasTalent, IsInLocation, RandomChance, IsGender/IsRace/IsCulture.
- **NPCs:** instance in game.db4 `_Instance_NPC` (`_ID` = `|Level|Objects|NPC|<Id>`, unique per level; `who=` targets the **Name** column) + `_Template_NPC`. Clone an existing look (CharacterSet/AnimSet) and place at any named instance: `_Instance_MarkerPoint` (541), `_Instance_PathWaypoint` (2451), NPCs, chests. `LEmin` 2 = cannot die (story NPCs, Rakorium); -10 = killable. Behaviour `clever_fighter` (20 vanilla, e.g. Red Butchers, Yandrik) / simple / stupid; `SpecialAttackChances` like `MeleeAttack 6.0 0, Finte 3.0 0, Todesstoss 1.0 0`.
- **NPC gear:** items with StorageGUID = NPC Guid; `Lootable` 1 = drops on death (vanilla: Ronkwer's Brabakbengel). Template mirrors: `SetupStorage 'Weapon/<id>/true/false;'` (first flag = lootable) and `SetupEquipment` (applied at runtime: clear it on clones or the source's weapon comes back). Extra drops via `LootTable` (`Type/Id/chance/amount/value/;`, money `Money/Geld/100/<heller>/1/`); the Mactaleanata leader drops her whole armour set this way.
- **Runtime unverified (first in-game test pending):** placed new NPCs appearing (Ulfried, Avestrue), bow-wielding hostile NPC, spawnAtEntity of a custom template inside the Ferdok house.
- **Character creator (playtest 31 Oct):** starting spells are kept only for archetypes in a magic category (`SpecialCategory` Mensch_Mag / Elf / Tul_Mag, `ArchetypeID` Magier/Elf/Elementaristen); others get all Za reset to -500 even with CasterType fullmage. The creator shows 3 classes per category page: a 4th member gets its own page after them. AE/MR are recomputed from attributes + `_Template_profession` bonus (archetype AEmax is ignored). Arcane Thief = Mensch_Mag/Magier + profession Dieb AE +3, MR +1: AE/caster type confirmed, BUT the hero still starts with all Za at -500 (the creator only displays the archetype spells). Fix in use: mods/*/GrantSpells.bat patches the newest save (_Instance_PC Za values where Advantages has z_arcanethief).

## 12. Facts verified on 1 Nov 2026 (crafting rework, saves)

**Drops and loot**
- A monster template's `SetupStorage` (e.g. `Item/loc01_alphaweibchen_fell:1/true/false;`) is ALWAYS on the corpse. A loot table with
  `LootTableValue` 0 did not drop every 100 % entry in play (White Fur's Silver Ruff never appeared): put guaranteed drops in
  SetupStorage, or give the table an explicit pick count = number of entries. Instances carry no SetupStorage; edit the template only.
- Loot tables may hand out plans: `Recipe/<id>/100/1/0/;` (vanilla `rob_unique_alwene`). Dialog can too:
  `CreateEntity category="Recipe" templateId="..." how="spawnInStorage" entity="Hero"`.
- A chest with a `LootTable` has no explicit storage: `m.place(... 'chest' ...)` fails on it; add to its loot table instead.
- (6 Nov, from the save) Pick count = entry count does roll every entry: Greymaw 6/6, Ashpelt, Stormhowl, Oracle 3/3, Ronkwer 2/2
  all delivered every 100 % entry. Value-0 plans drop from an NPC corpse (Da Vanya's Sunward Helm plan learned).
- Vanilla archers (cultists, orcs, goblins, Praiots, zombies) carry NO ammo and shoot anyway; their ammo drop is only in the loot
  table. Faelwen carried 40 unlootable `arm_am_duskfeather` and his 100 % table drop of the same ammo (and his plan) never arrived:
  never give an NPC carried ammo of the id its table drops (inferred, the plan's loss is unexplained).

**Tools**
- `CanDestroy` decides whether a quick-slot tool is used up: Hair pin (1) breaks, Locksmith knife `special_kleinesmesser` (0) is
  reusable. Clone a CanDestroy 0 base (knife, furrier's knife, sickle) for reusable tools.

**Monsters**
- `AuraStatuseffect='blitzDichFind'` (the nature-spirit bears of location03) works as a lightning aura on any monster.
- Placed monsters (`Story.monster`) never respawn. Wolves of Alvina (`Wolf_*_loc03_alwene`) are FaHexen: override `Faction`.

**Moving NPCs in from nowhere (parking)**
- Vanilla parks characters out of sight and moves them later with
  `TransferEntity entity="<Name>" location="<level>" entryPoint="<entry Name>" track="0"`, also across levels.
- `Story.npc(..., park=True)` puts the NPC (and its stock) in level `_graveyard_` and adds an `_Instance_Entry` row
  (`Id='EntryPortalObject'`, never an `EntryPortalParty`) at its real spot; `Story.arrive(nid)` is the action that brings it in.
  Used for the Crimson Circle (they appear when Klingenhand gives the job, after Moorbridge).

**Saves (what has broken a load, and why)**
- A save holds its own copy of every level's instances. New placed content (monsters, NPCs, shop stock) only exists in a NEW game
  unless the save is synced (`tools/maint/sync_save_world.py`). Templates, texts and loot tables come from the installed DB.
- `_PartyReceipes(Id)` lists the plans the party has learned. If a recipe template is removed or renamed, loading crashes with
  "Recipe with Id '...' not found". Keep removed recipe ids, or remap them in saves (`save_doctor.py fix`).
- Characters also carry `KnownRecipes` (TEXT). Story state: `_Story_Tasks(TaskId, TaskState)`, `_Story_Dialogs(DialogId, DialogLocked)`,
  `_Story_DialogTakeStatus(TakeId = dialogId + takeId, TakeStatus)`; none has a unique key, so duplicates are possible: check first.
- Save columns are typed. Never write Python `bytes` into a TEXT column (sqlite stores a BLOB that never equals the text again):
  read with a cp1252 text factory, or cast afterwards. `save_doctor.py check` finds both problems.
- A save is rewritten by the game on every save/autosave: edit only with the game closed, and re-check which save is newest.
- (2 Nov, hypothesis under test) After saves were edited with Python's modern SQLite, the game sometimes failed to load them with
  `Sqlite3Dataset::PerformQuery ... SELECT "TakeId","TakeStatus" FROM _Story_DialogTakeStatus / SQL logic error or missing database`,
  although every row read fine with SQLite 3.6.1 and integrity_check was ok. Remedy applied: rewrite the save with the bundled
  `tools/bin/sqlite3.exe` (`vacuum`); both save tools now end with that. If it recurs, bisect with the `.before_*` backups.
- **Cloned NPCs must not keep the source's `Groups`** (2 Nov): the Dark Eye gang cloned from the sleeping Dark Eyes kept `loc02_schwarzaugen_lagerhaus`, was not in `_DSA_GroupTable`, and the game asserted (`HasTableGuid(groupName, ...)`, groupmanager.cc 409) after closing Cano's shop. `quests.npc()`/`monster()` now clear it.
- **Clones keep `IsSitting` and the saved pose** (3 Nov): Faelwen, cloned from the bench-sitting Ferdok elf trainer, sat in mid-air and could not fight (soft lock). `quests.npc()` clears `IsSitting` and sets `LastBaseAnimation` Idle.
- **Moved NPCs walk back to their old home** (`RoamingBasePosition`, 3 floats): after moving Faelwen from Moorbridge he walked to his old coordinates in the Dark Forest. `sync_save_world.py` resets the home to the entry. Spawned monsters land on their target entity: use `Story.point()` spots, not the boss himself.
- **Quick-slot tokens need the `Game::` class prefix** (3 Nov): the old class mod left `SpellQuickSlot=FlimFlamFunkel=1` on the Elven Fighter (archetype_EL_KA_M/W); creating that character asserted in quickslotproperty.cc 250. build_remastered.py restores the prefix on every PC/CharWizard template.
- **Spells are not talents** (3 Nov): `HasTalent attribute="AttributoKK"` asserts "TalentManager::GetInfo(AttributoKK): talent not found". No vanilla condition reads a spell value (the full condition list has none), so scripts cannot scale with spell skill.
- **Spell hooks found in the exe strings** (3 Nov, read only, untested): `CanActivateTalent talent=` accepts talent, spell OR attack ids (checks the selection leader; asserts if none). `CastSpell` params: `who spellId target zfpUnused modifier fakeOnly track executeAfter`; vanilla's unused `chargeble_attributoch.xml` casts AttributoCH with zfpUnused 2 (cut "charged item" feature: `HasCharge`, `CreateChargedItemQuickslot`). The `Best...Entity` tokens are a fixed list (BestAttrXXEntity, BestTa<talent>Entity incl. BestTaMagiekundeEntity), none for spells. Spell modifier rules (`ZaModMax`): `Level`, `ArmatrutzSpecial`, `TlalucusSpecial`, `0`. The 8 `attributoXX` statuses have no `_Scripts_StatusEffectScripts` row. Modifier strings take fixed numbers only, but spell values are attributes (`ZaAttributoKK +2` works like vanilla `ZaHorriphobus +2`). The game folder's d3d9.dll is DXVK.
- **Attributo lab results** (player-tested 3 Nov, 5 casts each):
  - **ZaP1-3 = 'LEmax'** (probe against Life max): **works**. The dice never eat spell points, so the spell always lands at its best for the spell value, and it grows when the value is raised. This is the reliability fix.
  - **ZaDuration** works (20 min / 1 h observed). **ZaVal3 does nothing**: still +1 base with ZaVal3=2. A fixed-power cast with zfpUnused 9 gave +4 = 9/3+1.
  - **ZaModMax='Level'** on Attributo: the slider appears and its cost/level changes, but the bonus ignores it. The Attributo code does not read the modifier.
  - **ZaTargetType='Area'** on Attributo: **CRASH** when clicking the ground, NEBULA ASSERTION `msg->HasSpellTargetEntity()` (magicproperty.cc 531).
  - **CastSpell from a quick-slot item** (`who/target=ActingEntity zfpUnused=N`): **works**. It casts at once, only for a bearer who knows the spell, and spends that hero's AE.
  - **Clarity status (+20 to the probe attributes) followed by CastSpell or a hand cast**: best result every time. It proves the probe theory.
  - Potion-base items with CanDestroy 0 are **not consumed** on use, so the CreateEntity "give it back" line duplicates them.
  - The `SetStatusEffect` +20 statuses stack.
  - The KK aura talisman (CanActivateTalent gate + permanent SetStatusEffect) did nothing.
  - Several `CastSpell` actions in one script **replace each other**: only the last one runs, like a click without Ctrl. `executeAfter` means "after the dialogue ends", not a queue.
  - `CastSpell` inside a `RunActionScriptInRadius` script did nothing.
  - **Party-wide cast: PROVEN** (3 Nov). The item gives the bearer a short status whose trigger block runs: `CastSpell spellId=.. target="Hero"` (no who) + `WaitAction 4`, then for each companion name `If IsPartyMember who=X` (cast + wait) `Else` (WaitAction 0.1). The bearer casts on each party member in turn: one cast each, real spell value and AE.
  - `who="StatusEffectEntity"` in a status trigger script: **CRASH** (`statusEffectEntity hasn't been set`, tokenmanager.cc 222). Leave `who` out; the action then works on the bearer.
