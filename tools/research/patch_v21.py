"""One-off patch: v2.1 changes to tools/armory_data.py (moves off Drakensang Mountain, auras, spells, v21 include)."""
p = 'tools/armory_data.py'
t = open(p, encoding='utf-8').read()
def rep(a, b):
    global t
    assert t.count(a) == 1, a
    t = t.replace(a, b)
rep("(L, 'loot_loc12_chest_hammerhoehle', 'all'), mods='KK +2 TaSchmieden +3'", "(L, 'loot_loc09_kiste_aldessia2', 'all'), mods='KK +2 TaSchmieden +3'")
rep("(L, 'loot_loc12_chest_durchgang', 'all'), mods='MU +1 KL +1", "(L, 'loot_loc10_amuletttruhe', 'all'), mods='MU +1 KL +1")
rep("(L, 'loot_loc12_chest_hammerhoehle', 'all'), hit=[('p', 10, [('st', 'overthrown')])", "(C, 'loc11_chest_05', 'location11'), hit=[('p', 10, [('st', 'overthrown')])")
rep("'A dragonslayer hammer left in the Hammer Cave by the last of its oath-bound wielders.'", "'A dragonslayer hammer carried through the Fire Falls by the last of its oath-bound wielders.'")
rep("\"The good dragon's heart, made whole in the dark below Drakensang.\"", "\"The good dragon's heart, made whole and sealed in the dwarves' amulet vault.\"")
for key, aura in (("l_fang_lioness", "('AttributoMU_State', 'Skeleton_Root')"), ("l_angrosch_hammer", "('Favilludo_State', 'Skeleton_Root')"),
                  ("l_sala_mandra", "('Falkenauge_State', 'Head')"), ("l_eye_hesinde", "('AttributoKL_State', 'Skeleton_Root')"),
                  ("l_phex_laugh", "('Seidenzunge_State', 'Damage_Torso')"), ("l_wyrmbane", "('Kampf_Offensiv1', 'Head')"),
                  ("l_kurkum_aegis", "('Armatrutz_State', 'Damage_Torso')"), ("l_forgefather_plate", "('AttributoKO_State', 'Skeleton_Root')"),
                  ("l_seven_gazes", "('Psychostabilis_State', 'Damage_Torso')")):
    i = t.index(f"'{key}'"); j = t.index("tint=", i)
    t = t[:j] + f"aura={aura}, " + t[j:]
rep("mods='AEmax +10 MR +2 KL +1 IN +1', WpW6plus=6, WpPAmod=2", "mods='AEmax +10 MR +2 KL +1 IN +1 ZaFulminictus +2 ZaIgnifaxius +2 ZaArmatrutz +1', WpW6plus=6, WpPAmod=2")
rep("mods='AEmax +10 MR +2', WpW6plus=4, WpPAmod=1", "mods='AEmax +10 MR +2 ZaFulminictus +2 ZaIgnifaxius +2', WpW6plus=4, WpPAmod=1")
i = t.index("# ---------------- crafting material ----------------")
t = t[:i] + ("# v2.1 additions live in armory_data_v21.py (executed here so they share this namespace)\n"
             "import os as _os\nexec(open(_os.path.join(_os.path.dirname(__file__), 'armory_data_v21.py'), encoding='utf-8').read())\n"
             "ITEMS += ITEMS_V21\n\n") + t[i:]
open(p, 'w', encoding='utf-8').write(t)
v = 'tools/armory_data_v21.py'; s = open(v, encoding='utf-8').read()
s = s.replace("from armory_data_core import *   # noqa: F401,F403  (S, W, A, J, R, D, constants)\n", "")
open(v, 'w', encoding='utf-8').write(s)
print('patched')
