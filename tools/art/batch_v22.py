"""Codex icon batch v2.2: writes prompt files + run list; `post` mode turns finished PNGs into DDS for every mapped item key.
Usage: python -I tools/art/batch_v22.py prompts   ->  assets/armory_icons_v2/prompts/b22_*.txt + batch_v22_list.txt
       python -I tools/art/batch_v22.py post      ->  assets/armory_icons_v2/arm_<key>.dds for every finished image
Images use the native style sheet as reference and paint their own tier glow (native magic-icon look)."""
import sys, os
HERE = os.path.dirname(__file__); ROOT = os.path.join(HERE, '..', '..'); A = os.path.join(ROOT, 'assets', 'armory_icons_v2')
GLOW = {'none': 'No glow; same soft dark drop shadow as the sheet.',
        'blue': 'It is a magic item: add the same thin soft blue glow hugging the outline that the magic icons on the sheet have.',
        'violet': 'It is a rare magic item: add a thin soft violet glow hugging the outline, as thin as the blue glow of the magic icons on the sheet.',
        'gold': 'It is a legendary item: add a thin soft golden glow hugging the outline, as thin as the blue glow of the magic icons on the sheet.',
        'red': 'It is a cursed or mythical item: add a thin soft deep red glow hugging the outline, as thin as the blue glow of the magic icons on the sheet.'}
DIAG = 'held diagonally from lower left to upper right, filling the square'
JOBS = [  # image key, glow, description, item keys using it
    ('n_hood', 'blue', 'a deep hood of dark charcoal leather with fine silver-blue rune stitching along the edge, shown from the front like the helmets on the sheet', ['n_hood']),
    ('n_gloves', 'blue', 'a pair of dark leather gloves with open fingertips and silver-blue rune stitching on the backs, shown side by side', ['n_gloves']),
    ('n_breeches', 'blue', 'a pair of soft dark charcoal breeches with hidden pockets and fine silver-blue stitching, shown upright from the front', ['n_breeches']),
    ('n_treads', 'blue', 'a pair of soft Iryan leather boots in dark charcoal with turned-down cuffs and silver-blue stitching, side by side, toes pointing down to the left', ['n_treads']),
    ('n_signet', 'violet', 'a heavy gold signet ring with a black stone showing a tiny silver fox, shown at an angle', ['n_signet', 'j_shadowmaster']),
    ('s_nightfang', 'violet', f'a slim black elven long knife with a curved blade and a silver leaf guard, {DIAG}', ['s_nightfang']),
    ('d_twinfang', 'blue', f'a dirk with a split forked tip, one prong stained green with venom, dark grip, {DIAG}', ['d_twinfang']),
    ('d_misericorde', 'blue', f'a narrow triangular mercy dagger with a round steel guard and a simple pommel, {DIAG}', ['d_misericorde']),
    ('d_moonsilver', 'violet', f'a thin stiletto of bright pale moonsilver with a crescent-moon guard, {DIAG}', ['d_moonsilver']),
    ('d_kris', 'violet', f'a wavy Tulamide kris dagger with a dark carved wooden hilt and a faint green sheen on the blade, {DIAG}', ['d_kris']),
    ('d_athame', 'violet', f'a ritual athame with a black double-edged blade inlaid with tiny silver stars and a crystal pommel, {DIAG}', ['d_athame']),
    ('d_black_widow', 'violet', f'a heavy black dagger with a red hourglass mark on the guard and a dark red grip, {DIAG}', ['d_black_widow']),
    ('a_starfall', 'blue', 'three steel throwing stars with points shaped like starbursts, one overlapping the others', ['a_starfall']),
    ('s_witchfire', 'violet', 'three balanced throwing daggers with hollow glass channels in the blades holding glowing orange oil, fanned out', ['s_witchfire']),
    ('r_spellguard', 'blue', 'a small round wooden buckler with an iron rim and a single blue warding rune painted on it, slightly turned', ['r_spellguard']),
    ('s_mirror_buckler', 'violet', 'a small round buckler of polished mirror-bright steel with a gold rim, reflecting light, slightly turned', ['s_mirror_buckler']),
    ('w_stormcaller', 'violet', f'a partisan polearm with a broad winged steel head etched with lightning runes, {DIAG}', ['w_stormcaller']),
    ('w_hearthguard', 'violet', f'a heavy two-handed dwarven greataxe with a broad crescent blade, iron-banded haft and a red hearth emblem, {DIAG}', ['w_hearthguard']),
    ('w_moonshadow', 'blue', f'a curved saber with a dark blued blade and a silver basket guard, {DIAG}', ['w_moonshadow']),
    ('w_whisperwind', 'blue', f'a short recurve hunting bow of pale wood wrapped with grey feathers, {DIAG}', ['w_whisperwind']),
    ('ring_mix', 'blue', 'a simple silver ring with a small blue stone, shown at an angle', ['j_duelist', 'j_quickhand', 'j_patient_guard', 'j_marksman', 'j_spellblade']),
    ('ring_bulwark', 'blue', 'a thick plain iron ring with dwarven rune bands, shown at an angle', ['j_bulwark']),
    ('ring_late', 'violet', 'a gold ring set with a deep violet stone, shown at an angle', ['j_fencer', 'j_mirror_mind', 'j_wellspring', 'j_marathon']),
    ('ring_troll', 'violet', 'a crude dark iron ring holding a drop-shaped blood-red stone, shown at an angle', ['j_trollblood']),
    ('ring_red_rage', 'red', 'a gold ring shaped like a snarling beast biting a red gem, shown at an angle', ['j_red_rage']),
    ('ring_gambler', 'violet', 'a silver ring set with a tiny ivory die instead of a stone, shown at an angle', ['j_gambler']),
    ('ring_mountain_king', 'gold', 'a massive dwarven gold signet ring with a mountain and crown engraved on a dark stone, shown at an angle', ['j_mountain_king']),
    ('ring_amazon_queen', 'gold', 'a gold ring with a small lion head and two crossed sabers on the band, shown at an angle', ['j_amazon_queen']),
    ('am_serpent', 'blue', 'a silver amulet of a coiled snake biting its own tail, on a thin chain', ['j_serpent']),
    ('am_owl', 'blue', 'an amulet shaped like an owl face with two round amber eyes, on a leather cord', ['j_owl']),
    ('am_ember', 'blue', 'a red-gold pendant holding a glowing coal-like stone, on a chain', ['j_emberheart']),
    ('am_ironwill', 'violet', 'a heavy black iron torc with knotwork ends, open at the front', ['j_ironwill']),
    ('am_burning_mind', 'red', 'a pendant with a cracked crystal full of swirling fire, on a dark chain', ['j_burning_mind']),
    ('am_ardakor', 'red', 'a black cult amulet shaped like a single dragon eye with a red slit pupil, on a dark chain', ['j_ardakor_eye']),
    ('am_elfsong', 'violet', 'a delicate silver leaf pendant with fine veins, on a thin silver chain', ['j_elfsong']),
]
if __name__ == '__main__':
    os.makedirs(os.path.join(A, 'prompts'), exist_ok=True)
    if sys.argv[1] == 'prompts':
        with open(os.path.join(A, 'prompts', 'batch_v22_list.txt'), 'w', newline='') as lst:
            for key, glow, desc, _ in JOBS:
                with open(os.path.join(A, 'prompts', f'b22_{key}.txt'), 'w', encoding='utf-8') as f:
                    f.write(f'One inventory icon in exactly the same painted style as the attached sheet of Drakensang inventory icons: {desc}. '
                            f'Same lighting, colour saturation and painted texture as the sheet. {GLOW[glow]} Transparent background, no text.\n')
                lst.write(f'b22_{key}\n')
        print(len(JOBS), 'prompts')
    else:
        sys.path.insert(0, os.path.join(HERE, '..'))
        from PIL import Image
        from dsa import VANILLA_ICON_HEADER, encode_dxt3
        done = 0
        for key, _, _, items in JOBS:
            src = os.path.join(A, 'src', f'b22_{key}.png')
            if not os.path.exists(src): print('missing', key); continue
            im = Image.open(src).convert('RGBA')
            bb = im.split()[3].point(lambda v: 255 if v > 20 else 0).getbbox(); im = im.crop(bb); w, h = im.size; s = int(max(w, h) * 1.06)
            sq = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sq.paste(im, ((s - w) // 2, (s - h) // 2)); out = sq.resize((128, 128), Image.LANCZOS)
            out.save(os.path.join(A, f'b22_{key}_128.png'))
            for it in items:
                open(os.path.join(A, f'arm_{it}.dds'), 'wb').write(VANILLA_ICON_HEADER + encode_dxt3(out)); done += 1
        print('icons written', done)
