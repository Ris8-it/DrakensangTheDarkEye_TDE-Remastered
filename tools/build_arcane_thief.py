"""Arcane Thief: turns the Thief archetype (archetype_MI_TA_M/_W) into a dagger/throwing hybrid caster.

Usage: python -I tools/build_arcane_thief.py "<game>/export/db/armory_backup" mods/arcane_thief
Character creation only: affects heroes created after install. Independent of the Armory.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from dsa import Mod, insert, lit

db, out = sys.argv[1], sys.argv[2]
m = Mod(db, 'arcanethief')
ADV = 'z_arcanethief'
# Removes the thief's Arcane lore penalty, favours trickster spells, taxes the heavy mage spells, slower AE regeneration.
ADV_MOD = ('TaMagiekunde:+8;TaAlchimie:+8;Reg_AE_freq:+1;ZaAxxeleratus:+1;ZaDuplicatus:+1;ZaBlitz:+1;ZaAttributoGE:+1;ZaAttributoFF:+1;'
           'ZaFulminictus:+1;ZaIgnisphaero:-3;ZaGardianum:-2;ZaBalsam:-3;ZaSkelettarius:-5;ZaDschinenruf:-5;'
           'ZaElementarerDiener:-5;ZaOdem:-5;ZaEscliptifactusSchattenkraft:-5;ZaAeroFugumVakuum:-3;')
base = dict(m.s.execute("select * from _Template_Advantages where Id='z_charlatan'").fetchone())
base.update(Id=ADV, Name=f'{ADV}_N', Description=f'{ADV}_D', AttributeModifier=ADV_MOD)
m.static += [f"DELETE FROM _Template_Advantages WHERE Id={lit(ADV)};", insert('_Template_Advantages', base)]
m.undo_static.append(f"DELETE FROM _Template_Advantages WHERE Id={lit(ADV)};")
m.text(f'{ADV}_N', 'Arcane Thief')
m.text(f'{ADV}_D', 'Trained in the shadows and in the arcane: Arcane lore and Alchemy without the thief penalty (scrolls and potions), a knack for haste, blinding and illusion spells, '
                   'but weaker with fire, summoning and battlefield magic, and slower to regain astral energy.')
BG = ("A thief from Grangor who stole a magister's grimoire and, to everyone's surprise, understood it. Quick with dagger and throwing knife, "
      "light on her feet, and able to learn almost any spell a battle mage can, though her astral reserves are smaller and slower to return.")
for aid, info in (('archetype_MI_TA_M', 'MI_TA_M_Info'), ('archetype_MI_TA_W', 'MI_TA_W_Info')):
    cur = dict(m.s.execute('select * from _Template_PC_CharWizard where Id=?', (aid,)).fetchone())
    # the character creator keeps starting spells only for magic categories (playtest 31 Oct: the Thief got none).
    # Same setup as the vanilla Charlatan. The mage page holds 3 classes, so the Thief appears on its own page after them (confirmed working).
    m.edit_vanilla('PC_CharWizard', aid, CasterType='fullmage', IsMagicUser=1, AEmax=22, AE=22, MR=cur['MR'] + 2,
                   SpecialCategory='Mensch_Mag', ArchetypeID='Magier',
                   ZaAxxeleratus=3, ZaBlitz=3, ZaDuplicatus=2, ZaFulminictus=2,
                   Advantages=cur['Advantages'].replace('zz_thieves;', f'zz_thieves;{ADV};'),
                   SetupStorage=cur['SetupStorage'])   # review 31 Oct: no starting shield (metal shields block spellcasting anyway)
    m.vanilla_text(info, BG.replace('her ', 'his ').replace('she ', 'he ') if aid.endswith('_M') else BG)
# AE and MR are computed by the creator from attributes + profession bonus (Battle Mage +18 AE +2 MR, Charlatan +6/+1)
m.edit_vanilla('profession', 'Dieb', AEmax=3, MR=1)
m.write(out)
os.makedirs(os.path.join(out, 'icons'), exist_ok=True)
open(os.path.join(out, 'icons', 'files.txt'), 'w').write('')
open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write(
    '# Arcane Thief\n\nCharacter creation: the **Thief** archetype becomes an arcane thief (new heroes only).\n\n'
    '- Caster type full mage: can learn every human spell at trainers (like a battle mage).\n'
    '- AE 22 (battle mage 32), MR +2, starting spells Axxeleratus 3, Blitz 3, Duplicatus 2, Fulminictus 2.\n'
    '- Keeps all thief talents, dagger aptitude and Dodge; no starting shield (metal shields block spellcasting; caster bucklers are wood).\n'
    f'- Advantage "Arcane Thief": `{ADV_MOD}`\n\nInstall/Uninstall with the bat files (game closed). Independent of the Armory.\n')
print('ok', len(m.static), 'static rows,', len(m.vanilla_edits), 'archetype edits')
