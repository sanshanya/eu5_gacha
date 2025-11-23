import csv
import os
import shutil
from pathlib import Path

# ==============================================================================
# ⚙️ 配置区域 (只写 output)
# ==============================================================================
INPUT_CSV = "gacha_characters_data.csv"
OUTPUT_DIR = "output/eu5_gacha" # 所有文件生成在这里，绝对不碰源文件

# ==============================================================================
# 🛠️ 构建逻辑
# ==============================================================================

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_file(path, content):
    ensure_dir(path)
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write(content)

def wrap_code(code, indent=4):
    if not code or str(code).strip() == "": return ""
    lines = str(code).split('\n')
    return '\n'.join([' ' * indent + line.strip() for line in lines if line.strip()])

class ModBuilder:
    def __init__(self):
        self.chars = []
        
    def load_data(self):
        if not os.path.exists(INPUT_CSV):
            print(f"❌ 找不到 {INPUT_CSV}")
            return False
        with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['char_id'].strip(): self.chars.append(row)
        print(f"📊 加载了 {len(self.chars)} 名角色")
        return True

    def clean_output(self):
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        print(f"🧹 已清理输出目录: {OUTPUT_DIR}")

    # --- 1. 构建 Traits (合并 origin, awakened, transcended) ---
    def build_traits(self):
        for char in self.chars:
            cid = char['char_id']
            content = f"""# Traits for {cid}
gacha_{cid}_origin_trait = {{
    category = ruler
    allow = {{ always = no }}
    modifier = {{
{wrap_code(char['code_trait_origin'], 8)}
    }}
}}

gacha_{cid}_awakened_trait = {{
    category = ruler
    allow = {{ always = no }}
    modifier = {{
{wrap_code(char['code_trait_awakened'], 8)}
    }}
}}

gacha_{cid}_transcended_trait = {{
    category = general
    allow = {{ always = no }}
    modifier = {{
{wrap_code(char['code_trait_transcended'], 8)}
    }}
}}
"""
            write_file(f"{OUTPUT_DIR}/in_game/common/traits/gacha_{cid}_traits.txt", content)

    # --- 2. 构建 Modifiers (合并 Modifier + C0~C6) ---
    def build_modifiers(self):
        for char in self.chars:
            cid = char['char_id']
            # 基础修正
            content = f"""# Modifiers for {cid}
gacha_{cid}_modifier = {{
{wrap_code(char['code_modifier'], 4)}
}}

"""
            # 命座修正循环写入
            for i in range(7):
                code = char.get(f"code_c{i}", "")
                # 默认逻辑补全
                if not code.strip():
                    code = f"game_data = {{ category = character decaying = no }}\n    gacha_constellation_level = {i}"
                
                content += f"""gacha_{cid}_c{i}_modifier = {{
{wrap_code(code, 4)}
}}

"""
            write_file(f"{OUTPUT_DIR}/main_menu/common/static_modifiers/gacha_{cid}_modifiers.txt", content)

    # --- 3. 构建 Events (合并所有事件到单文件) ---
    def build_events(self):
        for char in self.chars:
            cid = char['char_id']
            content = f"""namespace = gacha_{cid}_events

# 1. 初见
gacha_{cid}_events.1 = {{
    type = country_event
    title = gacha_{cid}_events.1.title
    desc = gacha_{cid}_events.1.desc
    is_triggered_only = yes
    immediate = {{ event_illustration_estate_effect = {{ foreground = estate_type:nobles_estate background = estate_type:nobles_estate }} }}
    option = {{ name = gacha_{cid}_events.1.a historical_option = yes }}
}}

# 2. 提升
gacha_{cid}_events.2 = {{
    type = country_event
    title = gacha_{cid}_events.2.title
    desc = gacha_{cid}_events.2.desc
    is_triggered_only = yes
    immediate = {{ event_illustration_estate_effect = {{ foreground = estate_type:clergy_estate background = estate_type:clergy_estate }} }}
    option = {{ name = gacha_{cid}_events.2.a add_prestige = 10 }}
}}

# 4. 满命
gacha_{cid}_events.4 = {{
    type = country_event
    title = gacha_{cid}_events.4.title
    desc = gacha_{cid}_events.4.desc
    is_triggered_only = yes
    immediate = {{ event_illustration_estate_effect = {{ foreground = estate_type:nobles_estate background = estate_type:nobles_estate }} }}
    option = {{ name = gacha_{cid}_events.4.a add_prestige = 50 add_legitimacy = 20 }}
}}

# 11. 觉醒 (C2)
gacha_{cid}_events.11 = {{
    type = country_event
    title = gacha_{cid}_events.11.title
    desc = gacha_{cid}_events.11.desc
    is_triggered_only = yes
    option = {{ name = gacha_{cid}_events.11.a add_stability = 0.25 scope:existing_char = {{ add_trait = gacha_{cid}_awakened_trait }} }}
}}

# 12. 超越 (C4)
gacha_{cid}_events.12 = {{
    type = country_event
    title = gacha_{cid}_events.12.title
    desc = gacha_{cid}_events.12.desc
    is_triggered_only = yes
    option = {{ name = gacha_{cid}_events.12.a add_legitimacy = 5 scope:existing_char = {{ add_trait = gacha_{cid}_transcended_trait }} }}
}}
"""
            write_file(f"{OUTPUT_DIR}/in_game/events/gacha_{cid}_events.txt", content)

    # --- 4. 构建 Scripted Effects (Wrapper) ---
    def build_effects(self):
        for char in self.chars:
            cid = char['char_id']
            # 标准 Wrapper 逻辑
            content = f"""gacha_create_{cid}_effect = {{
    if = {{
        limit = {{ has_global_variable = gacha_{cid}_is_summoned }}
        random_in_global_list = {{
            variable = gacha_obtained_characters
            limit = {{ has_trait = gacha_{cid}_origin_trait }}
            save_scope_as = existing_char
        }}
        if = {{
            limit = {{ scope:existing_char = {{ employer = root }} }}
            scope:existing_char = {{
                if = {{
                    limit = {{ NOT = {{ var:gacha_constellation_lvl >= 6 }} }}
                    change_variable = {{ name = gacha_constellation_lvl add = 1 }}
                    gacha_apply_constellation_stats_effect = {{ who = {cid} }}
                }}
            }}
            if = {{
                limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl >= 6 }} }}
                scope:existing_char = {{ root = {{ trigger_event_non_silently = {{ id = gacha_{cid}_events.4 }} }} }}
            }}
            else_if = {{
                limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl = 4 }} }}
                scope:existing_char = {{ root = {{ trigger_event_non_silently = {{ id = gacha_{cid}_events.12 }} }} }}
            }}
            else_if = {{
                limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl = 2 }} }}
                scope:existing_char = {{ root = {{ trigger_event_non_silently = {{ id = gacha_{cid}_events.11 }} }} }}
            }}
            else = {{
                scope:existing_char = {{ root = {{ trigger_event_non_silently = {{ id = gacha_{cid}_events.2 }} }} }}
            }}
            clear_saved_scope = existing_char
        }}
        else = {{
            if = {{
                limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl >= 6 }} }}
                root = {{
                    change_variable = {{ name = gacha_starlight add = 1 }}
                    trigger_event_non_silently = {{ id = gacha_events.30 }}
                }}
            }}
            else = {{
                add_gold = 100
                add_prestige = 50
            }}
            clear_saved_scope = existing_char
        }}
    }}
    else = {{
        create_character = {{
            first_name = gacha_first_name_{cid}
            last_name = gacha_last_name_{cid}
            female = yes
            age = {char.get('age', 18)}
            culture = culture:{char.get('culture', 'tougokud')}
            religion = religion:{char.get('religion', 'shinto')}
            adm = {{ {char.get('adm_min', 80)} {char.get('adm_max', 100)} }}
            dip = {{ {char.get('dip_min', 80)} {char.get('dip_max', 100)} }}
            mil = {{ {char.get('mil_min', 80)} {char.get('mil_max', 100)} }}
            create_in_limbo = yes
            save_scope_as = new_char
        }}
        scope:new_char = {{
            gacha_register_new_character = {{ who = {cid} }}
        }}
        set_global_variable = {{ name = gacha_{cid}_is_summoned value = 1 }}
        scope:new_char = {{ root = {{ trigger_event_non_silently = {{ id = gacha_{cid}_events.1 }} }} }}
        clear_saved_scope = new_char
    }}
}}
"""
            write_file(f"{OUTPUT_DIR}/in_game/common/scripted_effects/gacha_{cid}_effects.txt", content)

    # --- 5. 构建 Localization ---
    def build_localization(self):
        content = "l_simp_chinese:\n"
        for char in self.chars:
            cid = char['char_id']
            content += f"\n  # === {char['first_name']} ({cid}) ===\n"
            content += f'  gacha_first_name_{cid}: "{char["first_name"]}"\n'
            content += f'  gacha_last_name_{cid}: "{char["last_name"]}"\n'
            # Traits
            content += f'  gacha_{cid}_origin_trait: "{char["loc_trait_origin_name"]}"\n'
            content += f'  desc_gacha_{cid}_origin_trait: "{char["loc_trait_origin_desc"]}"\n'
            content += f'  gacha_{cid}_awakened_trait: "{char["loc_trait_awakened_name"]}"\n'
            content += f'  desc_gacha_{cid}_awakened_trait: "{char["loc_trait_awakened_desc"]}"\n'
            content += f'  gacha_{cid}_transcended_trait: "{char["loc_trait_transcended_name"]}"\n'
            content += f'  desc_gacha_{cid}_transcended_trait: "{char["loc_trait_transcended_desc"]}"\n'
            # Modifiers
            content += f'  STATIC_MODIFIER_NAME_gacha_{cid}_modifier: "{char["loc_modifier_name"]}"\n'
            content += f'  STATIC_MODIFIER_DESC_gacha_{cid}_modifier: "{char["loc_modifier_desc"]}"\n'
            content += f'  gacha_{cid}_modifier: "{char["loc_modifier_name"]}"\n'
            content += f'  gacha_{cid}_modifier_desc: "{char["loc_modifier_desc"]}"\n'
            # Constellation Names
            for i in range(7):
                content += f'  STATIC_MODIFIER_NAME_gacha_{cid}_c{i}_modifier: "{char.get(f"c{i}_name", "")}"\n'
            # Events
            content += f'  gacha_{cid}_events.1.title: "{char["evt_meet_title"]}"\n'
            content += f'  gacha_{cid}_events.1.desc: "{char["evt_meet_desc"]}"\n'
            content += f'  gacha_{cid}_events.1.a: "{char["evt_meet_opt"]}"\n'
            content += f'  gacha_{cid}_events.2.title: "{char["evt_up_title"]}"\n'
            content += f'  gacha_{cid}_events.2.desc: "{char["evt_up_desc"]}"\n'
            content += f'  gacha_{cid}_events.2.a: "{char["evt_up_opt"]}"\n'
            content += f'  gacha_{cid}_events.4.title: "{char["evt_max_title"]}"\n'
            content += f'  gacha_{cid}_events.4.desc: "{char["evt_max_desc"]}"\n'
            content += f'  gacha_{cid}_events.4.a: "{char["evt_max_opt"]}"\n'
            content += f'  gacha_{cid}_events.11.title: "{char["evt_awk_title"]}"\n'
            content += f'  gacha_{cid}_events.11.desc: "{char["evt_awk_desc"]}"\n'
            content += f'  gacha_{cid}_events.11.a: "{char["evt_awk_opt"]}"\n'
            content += f'  gacha_{cid}_events.12.title: "{char["evt_tra_title"]}"\n'
            content += f'  gacha_{cid}_events.12.desc: "{char["evt_tra_desc"]}"\n'
            content += f'  gacha_{cid}_events.12.a: "{char["evt_tra_opt"]}"\n'

        write_file(f"{OUTPUT_DIR}/main_menu/localization/simp_chinese/gacha_characters_auto_l_simp_chinese.yml", content)

    # --- 6. 构建 Genes & Props (Asset Mapping) ---
    def build_assets(self):
        for char in self.chars:
            cid = char['char_id']
            # Props
            write_file(f"{OUTPUT_DIR}/in_game/gfx/portraits/accessories/gacha_{cid}_props.txt", 
                       f'gacha_{cid}_01 = {{ entity = {{ required_tags = "" shared_pose_entity = head entity = "gacha_{cid}_01_entity" }} }}')
            # Genes
            write_file(f"{OUTPUT_DIR}/in_game/common/genes/gacha_{cid}_genes.txt", 
                       f'accessory_genes = {{ gacha_{cid}_props_1 = {{ gene_{cid}_blank_1 = {{ index = 0 }} gacha_{cid}_01 = {{ index = 1 male = {{ 1 = gacha_{cid}_01 }} female = male boy = male girl = male adolescent_boy = male adolescent_girl = male infant = male }} }} }}')
            # Portrait Modifiers
            write_file(f"{OUTPUT_DIR}/in_game/gfx/portraits/portrait_modifiers/gacha_{cid}_portrait.txt", 
                       f'gacha_{cid}_portrait = {{ usage = game priority = 100 gacha_{cid}_01 = {{ dna_modifiers = {{ accessory = {{ mode = replace gene = gacha_{cid}_props_1 template = gacha_{cid}_01 value = 0.5 }} }} weight = {{ base = 0 modifier = {{ add = 255 has_trait = gacha_{cid}_origin_trait }} }} }} }}')
            # Asset file (仅文本定义)
            tex_name = os.path.basename(char['asset_portrait_path']) if char['asset_portrait_path'] else f"gacha_{cid}_1024_0.dds"
            write_file(f"{OUTPUT_DIR}/in_game/gfx/models/props/gacha_{cid}/gacha_{cid}_01.asset", 
                       f'pdxmesh = {{ name = "gacha_{cid}_01_mesh" file = "gacha_hm_prophet.mesh" scale = 1 meshsettings = {{ name = "prophet_shieldShape" index = 0 texture_diffuse = "{tex_name}" texture_specular = "{tex_name}" shader = "portrait_attachment_alpha_to_coverage" shader_file = "gfx/hmportrait.shader" }} }} entity = {{ name = "gacha_{cid}_01_entity" pdxmesh = "gacha_{cid}_01_mesh" }}')

    def run(self):
        self.clean_output()
        if self.load_data():
            print("🚀 开始构建 (安全模式)...")
            self.build_traits()
            self.build_modifiers()
            self.build_events()
            self.build_effects()
            self.build_localization()
            self.build_assets()
            print(f"✅ 构建完成！所有文件已生成在: {os.path.abspath(OUTPUT_DIR)}")
            print("👉 请手动检查 output 文件夹，确认无误后，再手动复制到你的 MOD 目录。")

if __name__ == "__main__":
    builder = ModBuilder()
    builder.run()