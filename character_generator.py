#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EU5 Gacha Character Generator
自动生成新角色所需的所有文件
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

# 配置文件模板
CONFIG_TEMPLATE = {
    "character_id": "keqing",  # 角色ID（英文小写）
    "first_name": "刻晴",
    "last_name": "璃月",
    "display_name": "刻晴",  # 显示名称
    "title": "玉衡星",  # 称号
    "element": "electro",  # 元素类型: electro, hydro, pyro, etc.
    "rarity": 5,  # 星级
    "gender": "female",  # female/male
    "age": 22,
    "culture": "tougokud",
    "religion": "shintō",
    
    # 属性范围 (min, max)
    "stats": {
        "adm": [75, 90],
        "dip": [70, 85],
        "mil": [85, 100]
    },
    
    # 特质定位
    "trait_focus": "military",  # military, admin, diplomatic, naval
    
    # 命座名称
    "constellations": {
        "c0": "紫薇座",
        "c1": "雷厉",
        "c2": "苛征",
        "c3": "璇玑",
        "c4": "调停",
        "c5": "贯彻",
        "c6": "廉贞"
    },
    
    # 特质名称
    "traits": {
        "origin": "玉衡星",
        "awakened": "斫断愚昧",
        "transcended": "天街巡游"
    },
    
    # 事件文本
    "events": {
        "first_meeting": {
            "title": "雷光闪耀",
            "desc": "随着雷光闪过，一位身着紫色服饰的女性出现在大殿中...",
            "option": "此乃吾国之幸！"
        },
        "constellation_up": {
            "title": "紫电流转",
            "desc": "刻晴的力量得到了进一步的提升...",
            "option": "继续前进！"
        },
        "max_constellation": {
            "title": "璇玑无双",
            "desc": "刻晴已经达到了力量的巅峰...",
            "option": "天下无敌！"
        },
        "c2_awakening": {
            "title": "命之座·觉醒",
            "desc": "随着命星的闪耀，刻晴领悟了「斫断愚昧」的真意...",
            "option": "所向披靡！"
        },
        "c4_transcendence": {
            "title": "命之座·超越",
            "desc": "刻晴展现出了「天街巡游」的姿态...",
            "option": "快如闪电！"
        }
    },
    
    # 素材文件路径（可选）
    "assets": {
        "portrait_texture": "",  # 角色立绘 1024x1024 .dds 文件路径
        "origin_trait_icon": "",  # 基础特质图标
        "awakened_trait_icon": "",  # C2特质图标
        "transcended_trait_icon": ""  # C4特质图标
    }
}


class CharacterGenerator:
    """角色文件生成器"""
    
    def __init__(self, config: Dict[str, Any], mod_path: str):
        self.config = config
        self.mod_path = Path(mod_path)
        self.char_id = config['character_id']
        
    def generate_all(self):
        """生成所有文件"""
        print(f"🎮 开始生成角色: {self.config['display_name']} ({self.char_id})")
        
        self.generate_traits()
        self.generate_effects()
        self.generate_events()
        self.generate_modifiers()
        self.generate_asset_files()
        self.update_gacha_pool()
        self.update_localization()
        self.update_triggers()
        
        print(f"✅ 角色 {self.config['display_name']} 生成完成！")
        
        # 处理素材文件
        self.handle_assets()
        
        print("\n⚠️  请记得准备以下图片文件:")
        print(f"   1. main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_origin_trait.dds")
        print(f"   2. main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_awakened_trait.dds")
        print(f"   3. main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_transcended_trait.dds")
        print(f"   4. in_game/gfx/models/props/gacha_{self.char_id}/gacha_{self.char_id}_1024_0.dds")
    
    def generate_traits(self):
        """生成特质文件
        
        CRITICAL: 使用不同的category避免特质冲突！
        - origin & awakened: category = ruler (可以共存)
        - transcended: category = general (不同category)
        如果全部使用相同category，游戏会自动移除旧特质！
        """
        content = f"""gacha_{self.char_id}_origin_trait = {{
  category = ruler  # 注意：origin和awakened使用同一category，可以共存
  allow = {{
    always = no
  }}

  modifier = {{
    land_morale_modifier        = 0.15
    discipline                  = 0.05
    general_effectiveness       = 0.25
    land_forcelimit_modifier    = 0.10
  }}
}}

gacha_{self.char_id}_awakened_trait = {{
  category = ruler  # 与origin相同，不会冲突
  allow = {{
    always = no
  }}

  modifier = {{
    manpower_recovery_speed     = 0.20
    global_regiment_recruit_speed = -0.25
    infantry_power              = 0.10
  }}
}}

gacha_{self.char_id}_transcended_trait = {{
  category = general  # ⚠️ 必须不同！否则会移除origin trait
  allow = {{
    always = no
  }}

  modifier = {{
    shock_damage                = 0.15
    movement_speed              = 0.15
    siege_ability               = 0.20
  }}
}}
"""
        path = self.mod_path / "in_game/common/traits" / f"gacha_{self.char_id}_traits.txt"
        self._write_file(path, content)
        print(f"✓ 生成: {path.name}")
    
    def generate_effects(self):
        """生成脚本效果文件"""
        content = f"""gacha_create_{self.char_id}_effect = {{
  # ==========================================
  # 分支 A：已拥有 -> 命之座升级 (Duplicate)
  # ==========================================
  if = {{
    limit = {{ has_global_variable = gacha_{self.char_id}_is_summoned }}

    random_in_global_list = {{
      variable = gacha_obtained_characters
      limit = {{ has_trait = gacha_{self.char_id}_origin_trait }}
      save_scope_as = existing_char
    }}

    if = {{
      limit = {{ scope:existing_char = {{ employer = root }} }}

      # --- 先处理角色数值变化 ---
      scope:existing_char = {{
        if = {{
          limit = {{ NOT = {{ var:gacha_constellation_lvl >= 6 }} }}
          change_variable = {{ name = gacha_constellation_lvl add = 1 }}
          gacha_apply_constellation_stats_effect = {{ who = {self.char_id} }}
        }}
      }}

      # --- 然后在root作用域下，根据【新的】命座等级触发对应的事件 ---
      if = {{
        limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl >= 6 }} }}
        scope:existing_char = {{
          root = {{
            trigger_event_non_silently = {{ id = gacha_{self.char_id}_events.4 }}
          }}
        }}
      }}
      else_if = {{
        limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl = 4 }} }}
        scope:existing_char = {{
          root = {{
            trigger_event_non_silently = {{ id = gacha_{self.char_id}_events.12 }}
          }}
        }}
      }}
      else_if = {{
        limit = {{ scope:existing_char = {{ var:gacha_constellation_lvl = 2 }} }}
        scope:existing_char = {{
          root = {{
            trigger_event_non_silently = {{ id = gacha_{self.char_id}_events.11 }}
          }}
        }}
      }}
      else = {{
        scope:existing_char = {{
          root = {{
            trigger_event_non_silently = {{ id = gacha_{self.char_id}_events.2 }}
          }}
        }}
      }}
      
      clear_saved_scope = existing_char
    }}
    else = {{
      add_gold = 100
      add_prestige = 50
      clear_saved_scope = existing_char
    }}
  }}

  # ==========================================
  # 分支 B：未拥有 -> 首次创建 (New)
  # ==========================================
  else = {{
    create_character = {{
      first_name = gacha_first_name_{self.char_id}
      last_name  = gacha_last_name_{self.char_id}
      {'female' if self.config['gender'] == 'female' else 'male'}     = yes
      age        = {self.config['age']}
      culture  = culture:{self.config['culture']}
      religion = religion:{self.config['religion']}
      adm = {{ {self.config['stats']['adm'][0]} {self.config['stats']['adm'][1]} }}
      dip = {{ {self.config['stats']['dip'][0]} {self.config['stats']['dip'][1]} }}
      mil = {{ {self.config['stats']['mil'][0]} {self.config['stats']['mil'][1]} }}
      create_in_limbo = yes
      save_scope_as = gacha_{self.char_id}_new_char
    }}
    scope:gacha_{self.char_id}_new_char = {{
      gacha_register_new_character = {{ who = {self.char_id} }}
    }}
    set_global_variable = {{ name = gacha_{self.char_id}_is_summoned value = 1 }}

    scope:gacha_{self.char_id}_new_char = {{
      root = {{
        trigger_event_non_silently = {{ id = gacha_{self.char_id}_events.1 }}
      }}
    }}
    
    clear_saved_scope = gacha_{self.char_id}_new_char
  }}
}}
"""
        path = self.mod_path / "in_game/common/scripted_effects" / f"gacha_{self.char_id}_effects.txt"
        self._write_file(path, content)
        print(f"✓ 生成: {path.name}")
    
    def generate_events(self):
        """生成事件文件"""
        events = self.config['events']
        content = f"""namespace = gacha_{self.char_id}_events

# ==========================================
# 事件 1：初次见面 (First Meeting)
# ==========================================
gacha_{self.char_id}_events.1 = {{
    type = country_event
    title = gacha_{self.char_id}_events.1.title
    desc  = gacha_{self.char_id}_events.1.desc
    is_triggered_only = yes

    immediate = {{
        event_illustration_estate_effect = {{
            foreground = estate_type:nobles_estate
            background = estate_type:nobles_estate
        }}
    }}

    option = {{
        name = gacha_{self.char_id}_events.1.a
        historical_option = yes
    }}
}}

# ==========================================
# 事件 2：通用命座提升 (Constellation Up)
# ==========================================
gacha_{self.char_id}_events.2 = {{
    type = country_event
    title = gacha_{self.char_id}_events.2.title
    desc  = gacha_{self.char_id}_events.2.desc
    is_triggered_only = yes

    immediate = {{
        event_illustration_estate_effect = {{
            foreground = estate_type:clergy_estate
            background = estate_type:clergy_estate
        }}
    }}

    option = {{
        name = gacha_{self.char_id}_events.2.a
        add_prestige = 10
    }}
}}

# ==========================================
# 事件 4：满命 (Max Constellation)
# ==========================================
gacha_{self.char_id}_events.4 = {{
    type = country_event
    title = gacha_{self.char_id}_events.4.title
    desc  = gacha_{self.char_id}_events.4.desc
    is_triggered_only = yes

    immediate = {{
        event_illustration_estate_effect = {{
            foreground = estate_type:nobles_estate
            background = estate_type:nobles_estate
        }}
    }}

    option = {{
        name = gacha_{self.char_id}_events.4.a
        add_prestige = 50
        add_legitimacy = 20
    }}
}}

# ==========================================
# 事件 11：命之座·觉醒 (C2)
# ==========================================
gacha_{self.char_id}_events.11 = {{
    type = country_event
    title = "gacha_{self.char_id}_events.11.title"
    desc  = "gacha_{self.char_id}_events.11.desc"
    is_triggered_only = yes

    option = {{
        name = "gacha_{self.char_id}_events.11.a"
        add_stability = 0.25
    }}
}}

# ==========================================
# 事件 12：命之座·超越 (C4)
# ==========================================
gacha_{self.char_id}_events.12 = {{
    type = country_event
    title = "gacha_{self.char_id}_events.12.title"
    desc  = "gacha_{self.char_id}_events.12.desc"
    is_triggered_only = yes

    option = {{
        name = "gacha_{self.char_id}_events.12.a"
        add_legitimacy = 5
    }}
}}
"""
        path = self.mod_path / "in_game/events" / f"gacha_{self.char_id}_events.txt"
        self._write_file(path, content)
        print(f"✓ 生成: {path.name}")
    
    def generate_modifiers(self):
        """生成修正文件"""
        element = self.config['element']
        content = f"""gacha_{self.char_id}_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_core = yes
  gacha_{element}_godeye = yes
}}

gacha_{self.char_id}_c0_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 0
}}
gacha_{self.char_id}_c1_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 1
}}
gacha_{self.char_id}_c2_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 2
}}
gacha_{self.char_id}_c3_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 3
}}
gacha_{self.char_id}_c4_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 4
}}
gacha_{self.char_id}_c5_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 5
}}
gacha_{self.char_id}_c6_modifier = {{
  game_data = {{ category = character decaying = no }}
  gacha_constellation_level = 6
}}
"""
        path = self.mod_path / "main_menu/common/static_modifiers" / f"gacha_{self.char_id}_modifiers.txt"
        self._write_file(path, content)
        print(f"✓ 生成: {path.name}")
    
    def generate_asset_files(self):
        """生成立绘资产文件"""
        # 1. Asset definition
        asset_content = f"""
pdxmesh = {{
	name = "gacha_{self.char_id}_01_mesh"
	file = "gacha_hm_prophet.mesh"
	scale = 1
	meshsettings = {{
		name = "prophet_shieldShape"
		index = 0
		texture_diffuse = "gacha_{self.char_id}_1024_0.dds"
		texture_specular = "gacha_{self.char_id}_1024_0.dds"
		shader = "portrait_attachment_alpha_to_coverage"
		shader_file = "gfx/hmportrait.shader"
	}}
}}
entity = {{
	name = "gacha_{self.char_id}_01_entity"
	pdxmesh = "gacha_{self.char_id}_01_mesh"
}}
"""
        asset_path = self.mod_path / f"in_game/gfx/models/props/gacha_{self.char_id}/gacha_{self.char_id}_01.asset"
        self._write_file(asset_path, asset_content)
        print(f"✓ 生成: gacha_{self.char_id}_01.asset")
        
        # 2. Props
        props_content = f"""gacha_{self.char_id}_01 = {{
  entity = {{
    required_tags     = ""
    shared_pose_entity = head
    entity            = "gacha_{self.char_id}_01_entity"
  }}
}}
"""
        props_path = self.mod_path / f"in_game/gfx/portraits/accessories/gacha_{self.char_id}_props.txt"
        self._write_file(props_path, props_content)
        print(f"✓ 生成: gacha_{self.char_id}_props.txt")
        
        # 3. Genes
        genes_content = f"""accessory_genes = {{
  gacha_{self.char_id}_props_1 = {{
    gene_{self.char_id}_blank_1 = {{ index = 0 }}

    gacha_{self.char_id}_01 = {{
      index = 1
      male   = {{ 1 = gacha_{self.char_id}_01 }}
      female = male
      boy    = male
      girl   = male
      adolescent_boy  = male
      adolescent_girl = male
      infant = male
    }}
  }}
}}
"""
        genes_path = self.mod_path / f"in_game/common/genes/gacha_{self.char_id}_genes_special_accessories_misc.txt"
        self._write_file(genes_path, genes_content)
        print(f"✓ 生成: gacha_{self.char_id}_genes_special_accessories_misc.txt")
        
        # 4. Portrait modifiers
        portrait_content = f"""gacha_{self.char_id}_portrait = {{
  usage    = game
  priority = 100

  gacha_{self.char_id}_01 = {{
    dna_modifiers = {{
      accessory = {{
        mode     = replace
        gene     = gacha_{self.char_id}_props_1
        template = gacha_{self.char_id}_01
        value    = 0.5
      }}
    }}
    weight = {{
      base = 0
      modifier = {{
        add = 255
        has_trait = gacha_{self.char_id}_origin_trait
      }}
    }}
  }}
}}
"""
        portrait_path = self.mod_path / f"in_game/gfx/portraits/portrait_modifiers/gacha_{self.char_id}_portrait.txt"
        self._write_file(portrait_path, portrait_content)
        print(f"✓ 生成: gacha_{self.char_id}_portrait.txt")
    
    def update_gacha_pool(self):
        """更新抽卡池（需要手动检查）"""
        print(f"⚠️  请手动更新 gacha_pools.txt，将 gacha_create_{self.char_id}_effect 添加到对应的池子中")
    
    def update_localization(self):
        """生成本地化文本（需要手动添加）"""
        loc_path = self.mod_path / "localization_template.yml"
        
        consts = self.config['constellations']
        traits = self.config['traits']
        events = self.config['events']
        
        content = f"""
# ============================================================
# Character - {self.config['display_name']} ({self.char_id})
# ============================================================

# === 姓名 ===
gacha_first_name_{self.char_id}: "{self.config['first_name']}"
gacha_last_name_{self.char_id}: "{self.config['last_name']}"

# === 特质 (Traits) ===
gacha_{self.char_id}_origin_trait: "{traits['origin']}"
desc_gacha_{self.char_id}_origin_trait: "TODO: 添加描述"

gacha_{self.char_id}_awakened_trait: "{traits['awakened']}"
desc_gacha_{self.char_id}_awakened_trait: "TODO: 添加描述"

gacha_{self.char_id}_transcended_trait: "{traits['transcended']}"
desc_gacha_{self.char_id}_transcended_trait: "TODO: 添加描述"

# === 修正 (Modifiers) ===
STATIC_MODIFIER_NAME_gacha_{self.char_id}_modifier: "TODO: 添加修正名称"
STATIC_MODIFIER_DESC_gacha_{self.char_id}_modifier: "TODO: 添加修正描述"
gacha_{self.char_id}_modifier: "TODO"
gacha_{self.char_id}_modifier_desc: "TODO"

# === 命之座 (Constellations) ===
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c0_modifier: "{consts['c0']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c1_modifier: "{consts['c1']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c2_modifier: "{consts['c2']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c3_modifier: "{consts['c3']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c4_modifier: "{consts['c4']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c5_modifier: "{consts['c5']}"
STATIC_MODIFIER_NAME_gacha_{self.char_id}_c6_modifier: "{consts['c6']}"

# === 事件 (Events) ===
gacha_{self.char_id}_events.1.title: "{events['first_meeting']['title']}"
gacha_{self.char_id}_events.1.desc: "{events['first_meeting']['desc']}"
gacha_{self.char_id}_events.1.a: "{events['first_meeting']['option']}"

gacha_{self.char_id}_events.2.title: "{events['constellation_up']['title']}"
gacha_{self.char_id}_events.2.desc: "{events['constellation_up']['desc']}"
gacha_{self.char_id}_events.2.a: "{events['constellation_up']['option']}"

gacha_{self.char_id}_events.4.title: "{events['max_constellation']['title']}"
gacha_{self.char_id}_events.4.desc: "{events['max_constellation']['desc']}"
gacha_{self.char_id}_events.4.a: "{events['max_constellation']['option']}"

gacha_{self.char_id}_events.11.title: "{events['c2_awakening']['title']}"
gacha_{self.char_id}_events.11.desc: "{events['c2_awakening']['desc']}"
gacha_{self.char_id}_events.11.a: "{events['c2_awakening']['option']}"

gacha_{self.char_id}_events.12.title: "{events['c4_transcendence']['title']}"
gacha_{self.char_id}_events.12.desc: "{events['c4_transcendence']['desc']}"
gacha_{self.char_id}_events.12.a: "{events['c4_transcendence']['option']}"
"""
        self._write_file(loc_path, content)
        print(f"✓ 生成: localization_template.yml (请手动复制到 eu_gacha_l_simp_chinese.yml)")
    
    def update_triggers(self):
        """更新触发器（提示需要手动添加）"""
        print(f"⚠️  请手动更新 gacha_trigger.txt，添加: has_trait = gacha_{self.char_id}_origin_trait")
    
    def handle_assets(self):
        """处理素材文件（复制或提示）"""
        import shutil
        
        if 'assets' not in self.config:
            return
        
        assets = self.config['assets']
        copied_count = 0
        
        # 定义目标路径映射
        asset_mapping = {
            'portrait_texture': self.mod_path / f"in_game/gfx/models/props/gacha_{self.char_id}/gacha_{self.char_id}_1024_0.dds",
            'origin_trait_icon': self.mod_path / f"main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_origin_trait.dds",
            'awakened_trait_icon': self.mod_path / f"main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_awakened_trait.dds",
            'transcended_trait_icon': self.mod_path / f"main_menu/gfx/interface/icons/traits/gacha_{self.char_id}_transcended_trait.dds"
        }
        
        print("\n📁 处理素材文件...")
        
        for asset_key, target_path in asset_mapping.items():
            source_path = assets.get(asset_key, "")
            
            if source_path and source_path.strip():
                source = Path(source_path)
                
                if source.exists():
                    # 确保目标目录存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(source, target_path)
                    print(f"✓ 已复制: {source.name} → {target_path.name}")
                    copied_count += 1
                else:
                    print(f"⚠️  文件不存在: {source_path}")
        
        if copied_count > 0:
            print(f"\n✅ 成功复制 {copied_count} 个素材文件！")
        else:
            print("💡 未提供素材文件路径，请稍后手动添加图片文件。")
    
    def _write_file(self, path: Path, content: str):
        """写入文件"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """主函数"""
    import sys
    
    # 检查是否提供了配置文件
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print("📝 使用默认配置（刻晴）")
        config = CONFIG_TEMPLATE
    
    # 获取MOD路径（当前脚本所在目录）
    mod_path = Path(__file__).parent
    
    # 生成角色文件
    generator = CharacterGenerator(config, str(mod_path))
    generator.generate_all()
    
    print("\n📖 使用说明:")
    print("1. 创建一个JSON配置文件（参考 CONFIG_TEMPLATE）")
    print("2. 运行: python character_generator.py your_config.json")
    print("3. 生成后手动完成:")
    print("   - 更新 gacha_pools.txt 添加角色到卡池")
    print("   - 更新 gacha_trigger.txt 添加立绘触发器")
    print("   - 将 localization_template.yml 的内容复制到主本地化文件")
    print("   - 准备4个 .dds 图片文件")


if __name__ == "__main__":
    main()
