# ======================= v2.3: secret-quest gear (Crimson Circle duelists, Rakorium's codex) =======================
# Executed inside armory_data.py (shares its namespace). place=None: the secret_quests module puts these in the duelists'
# hands (they wield them and drop them) or hands them out as quest rewards. Native-only effects on weapons/armour/shields.

ITEMS_V23 = [
    # ---------- the seven duelists' weapons (each drops from its wielder) ----------
    W('s_riposte', 'superrare', 'Rapier', 'Harbour Riposte', "Jorgo Fairwind's rapier. He never attacks first; he never needs to.",
      None, hit=[('p', 20, [('st', 'ArmSundered')]), ('if', 'ArmSundered', [('dmg', 0, 1, 'physical', '')]), ('p', 8, [('buff', 'ArmQuickstep')])],
      mods='GE +1', WpW6plus=6, WpATmod=1, WpPAmod=2, tint=SHADOW),
    W('s_ashblade', 'superrare', 'Khunchomer', 'Ashblade', "Ilsabe's Khunchom saber, tempered in a burning chapel. It still remembers the fire.",
      None, hit=[('p', 15, [FIRE()]), ('if', 'burning', [('dmg', 0, 1, 'fire', 'Ignisphaero_Impact')]), ('p', 8, [('buff', 'ArmTrance')])],
      mods='MU +1', imm='fire', WpW6plus=7, WpATmod=1, tint=EMBER),
    W('l_duskarrow', 'legendary', 'Elfenbogen', 'Duskarrow', 'The bow of Faelwen, the elf who hunts elves. Gwendala knows its song, and hates it.',
      None, hit=[('p', 100, [('dmg', 1, 0, 'physical', '')]), ('p', 15, [('st', 'ArmDazed')]), ('p', 10, [('st', 'corpofrigo')]), ('p', 8, [('buff', 'ArmQuickstep')])],
      mods='FF +1 IN +1', WpW6=2, WpW6plus=4, aura=('Falkenauge_State', 'Head'), tint=LEAF),
    W('l_oathbreaker', 'legendary', 'Bastartschwert', 'Oathbreaker', 'Sir Wolfhart swore on this blade to defend Grimmzahn, then sold the gate to the orcs.',
      None, hit=[('p', 15, [('st', 'ArmShaken')]), ('p', 12, [('st', 'ArmBleeding')]), ('if', 'ArmShaken', [('dmg', 0, 1, 'physical', '')])],
      mods='KK +1 MU +1', WpW6plus=8, WpATmod=1, WpPAmod=1, tint=BLOOD),
    S('s_oath_pavise', 'superrare', 'Eisenschild_01', 'Pavise of the Broken Oath', "Wolfhart's kite shield. The Grimmzahn crest has been scraped off.",
      None, mods='KO +1', imm='overthrown', WpPAmod=3, tint=BLOOD),
    W('l_lionsbane', 'legendary', 'Amazonensaebel', 'Lionsbane', 'Sabeth was cast out of Kurkum for killing a sister in a duel. Rhulana will want this saber back.',
      None, hit=[('p', 15, [('st', 'ArmSundered')]), ('p', 12, [('st', 'wound')]), ('if', 'wound', [('dmg', 0, 1, 'physical', '')]), ('p', 10, [('buff', 'ArmLionroar')])],
      mods='GE +1 MU +1 TaSaebel +2', WpW6plus=9, WpATmod=2, WpPAmod=1, aura=('AttributoMU_State', 'Skeleton_Root'), tint=HOLY),
    W('l_exile_cleaver', 'legendary', 'Felsspalter', "Exile's Cleaver", 'Grimbart Ironbeard was banished from Murolosh with this axe. Forgrimm has heard the story; the dwarves do not tell it twice.',
      None, hit=[('p', 15, [('st', 'overthrown')]), ('p', 15, [('st', 'ArmFrailty')]), ('if', 'overthrown', [('dmg', 2, 1, 'physical', 'Kulminatio_Impact')]), ('p', 8, [('buff', 'ArmIronskin')])],
      mods='KK +2 KO +1', WpW6plus=8, WpPAmod=0, tint=EARTH),
    W('m_crimson_vow', 'mythic', 'Langdolch', 'Crimson Vow', 'The Crimson Master\'s dirk. Every member of the Circle swore their oath on it, in blood.',
      None, hit=[('p', 20, [('st', 'ArmBleeding')]), ('p', 15, [('st', 'ArmStarburn')]), ('if', 'ArmBleeding', [('dmg', 2, 1, 'physical', '')]),
                 ('p', 100, [('asp', 1)]), ('p', 10, [('buff', 'ArmShadowstep')])],
      mods='GE +2 FF +1 AEmax +10', WpW6plus=8, WpATmod=2, WpINI=2, aura=('Seidenzunge_State', 'Damage_Torso'), tint=BLOOD),
    # ---------- Crimson Circle rewards (Master Klingenhand) ----------
    A('a_klingenhand_gloves', 'superrare', 'handschuhe_streuner', "Klingenhand's Fencing Gloves", 'Thin kid gloves, darned at the knuckles. They have won forty duels.',
      None, mods='AT +1 PA +1 FF +1', tint=SHADOW),
    J('j_crimson_circle', 'mythic', 'Goldring', 'Ring of the Crimson Circle', 'Seven blades engraved around a red stone. Its last owner was the best duelist in the Middenrealm; now it is you.',
      None, mods='AT +2 PA +2 GE +1 MU +1', aura=('Kampf_Offensiv1', 'Head'), tint=BLOOD),
    # ---------- Rakorium's codex rewards ----------
    J('j_rk_spectacles', 'superrare', 'Silberkette', "Rakorium's Spare Spectacles", 'Worn on a chain. Through them, magic looks like handwriting, and handwriting looks like magic.',
      None, mods='KL +2 IN +1 MR +1 TaMagiekunde +3', tint=ASTRAL),
    W('m_rk_staff', 'mythic', 'Magierstab', "Rakorium's Grand Theory", 'A staff carved with the complete proof that dragons dream. It hums when nobody is listening.',
      None, hit=[('p', 100, [('asp', 2)]), ('p', 20, [('st', 'ArmStarburn')]), ('p', 15, [('st', 'ArmHexed')]), ('p', 10, [('buff', 'ArmAstralsurge')])],
      mods='AEmax +15 KL +2 IN +1 MR +2 ZaIgnifaxius +2 ZaFulminictus +2 ZaBlitz +2', WpW6plus=7, WpPAmod=2, aura=('AttributoKL_State', 'Skeleton_Root'), tint=ASTRAL),
    A('a_rk_best_hat', 'legendary', 'hut_magierhut', "Rakorium's Best Hat", 'Not the second-best hat. THE hat. Slightly singed, and it knows things.',
      None, mods='AEmax +10 KL +1 IN +1 MR +2', tint=ASTRAL),
]
