import os
import re
import csv
import glob

# ==============================================================================
# 1. ⚙️ 路径配置 (只读模式)
# ==============================================================================
# 请确保此路径正确
BASE_PATH = r"E:\app\steam\steamapps\common\Europa Universalis V\game\mod\eu5_gacha"

# 输入路径 (自动拼接)
PATH_LOC = os.path.join(BASE_PATH, "main_menu", "localization", "simp_chinese", "eu_gacha_l_simp_chinese.yml")
PATH_TRAITS = os.path.join(BASE_PATH, "in_game", "common", "traits")
PATH_STATIC_MODS = os.path.join(BASE_PATH, "main_menu", "common", "static_modifiers")
PATH_MOD_TYPES = os.path.join(BASE_PATH, "main_menu", "common", "modifier_type_definitions")
PATH_ICONS_FILE = os.path.join(BASE_PATH, "main_menu", "common", "modifier_icons", "gacha_modifier_icons.txt")

# 输出文件 (仅在当前目录生成 CSV)
OUT_CHAR_CSV = "gacha_characters_data.csv"
OUT_SYS_CSV = "gacha_system_config.csv"

# ==============================================================================
# 2. 解析逻辑
# ==============================================================================

def extract_brace_content(text, start_index):
    """提取 {} 内部内容"""
    balance = 0
    content = []
    started = False
    for i in range(start_index, len(text)):
        char = text[i]
        if char == '{':
            if not started:
                started = True
                balance = 1
                continue
            else:
                balance += 1
        elif char == '}':
            balance -= 1
            if balance == 0 and started:
                return "".join(content).strip()
        if started:
            content.append(char)
    return ""

def clean_code(code_str):
    """清理代码格式，保留换行"""
    if not code_str: return ""
    return code_str.strip()

def main():
    print("🚀 开始安全提取...")
    
    # 数据容器
    characters = {}
    systems = {} 

    # ------------------------------------------------------------------
    # A. 读取 Localisation (构建骨架)
    # ------------------------------------------------------------------
    if os.path.exists(PATH_LOC):
        print(f"📖 读取本地化文件...")
        with open(PATH_LOC, 'r', encoding='utf-8-sig') as f:
            loc_content = f.read()

        # 正则列表
        loc_patterns = [
            # 身份
            (r'gacha_first_name_(\w+):\s*"(.*)"', "first_name"),
            (r'gacha_last_name_(\w+):\s*"(.*)"', "last_name"),
            # 特质
            (r'gacha_(\w+)_origin_trait:\s*"(.*)"', "loc_trait_origin_name"),
            (r'desc_gacha_(\w+)_origin_trait:\s*"(.*)"', "loc_trait_origin_desc"),
            (r'gacha_(\w+)_awakened_trait:\s*"(.*)"', "loc_trait_awakened_name"),
            (r'desc_gacha_(\w+)_awakened_trait:\s*"(.*)"', "loc_trait_awakened_desc"),
            (r'gacha_(\w+)_transcended_trait:\s*"(.*)"', "loc_trait_transcended_name"),
            (r'desc_gacha_(\w+)_transcended_trait:\s*"(.*)"', "loc_trait_transcended_desc"),
            # 修正
            (r'STATIC_MODIFIER_NAME_gacha_(\w+)_modifier:\s*"(.*)"', "loc_modifier_name"),
            (r'STATIC_MODIFIER_DESC_gacha_(\w+)_modifier:\s*"(.*)"', "loc_modifier_desc"),
            (r'gacha_(\w+)_modifier:\s*"(.*)"', "loc_modifier_name"), # 兼容旧格式
            (r'gacha_(\w+)_modifier_desc:\s*"(.*)"', "loc_modifier_desc"),
            # 命座修正名称 (关键修正：捕获 c0-c6)
            (r'STATIC_MODIFIER_NAME_gacha_(\w+)_(c[0-6])_modifier:\s*"(.*)"', "constellation"),
            # 事件
            (r'gacha_(\w+)_events\.1\.title:\s*"(.*)"', "evt_meet_title"),
            (r'gacha_(\w+)_events\.1\.desc:\s*"(.*)"', "evt_meet_desc"),
            (r'gacha_(\w+)_events\.1\.a:\s*"(.*)"', "evt_meet_opt"),
            (r'gacha_(\w+)_events\.2\.title:\s*"(.*)"', "evt_up_title"),
            (r'gacha_(\w+)_events\.2\.desc:\s*"(.*)"', "evt_up_desc"),
            (r'gacha_(\w+)_events\.2\.a:\s*"(.*)"', "evt_up_opt"),
            (r'gacha_(\w+)_events\.4\.title:\s*"(.*)"', "evt_max_title"),
            (r'gacha_(\w+)_events\.4\.desc:\s*"(.*)"', "evt_max_desc"),
            (r'gacha_(\w+)_events\.4\.a:\s*"(.*)"', "evt_max_opt"),
            (r'gacha_(\w+)_events\.11\.title:\s*"(.*)"', "evt_awk_title"),
            (r'gacha_(\w+)_events\.11\.desc:\s*"(.*)"', "evt_awk_desc"),
            (r'gacha_(\w+)_events\.11\.a:\s*"(.*)"', "evt_awk_opt"),
            (r'gacha_(\w+)_events\.12\.title:\s*"(.*)"', "evt_tra_title"),
            (r'gacha_(\w+)_events\.12\.desc:\s*"(.*)"', "evt_tra_desc"),
            (r'gacha_(\w+)_events\.12\.a:\s*"(.*)"', "evt_tra_opt"),
            # 系统级
            (r'MODIFIER_TYPE_NAME_(gacha_\w+):\s*"(.*)"', "system_loc_name"),
            (r'MODIFIER_TYPE_DESC_(gacha_\w+):\s*"(.*)"', "system_loc_desc"),
            (r'STATIC_MODIFIER_NAME_(gacha_\w+):\s*"(.*)"', "system_loc_name"),
            (r'STATIC_MODIFIER_DESC_(gacha_\w+):\s*"(.*)"', "system_loc_desc"),
        ]

        for pattern, col_type in loc_patterns:
            matches = re.findall(pattern, loc_content)
            for match in matches:
                # 处理命座: Group1=ID, Group2=Level, Group3=Text
                if col_type == "constellation":
                    cid, c_lvl, text = match
                    # 过滤掉以 _cX 结尾的错误 ID (防止递归错误)
                    if re.search(r'_c[0-6]$', cid): continue
                    
                    if cid not in characters: characters[cid] = {"char_id": cid}
                    characters[cid][f"{c_lvl}_name"] = text.replace('\\n', '\n')
                
                # 处理系统
                elif col_type.startswith("system"):
                    sid, text = match
                    if sid not in systems: systems[sys_id] = {"sys_id": sid}
                    key = "loc_name" if "name" in col_type else "loc_desc"
                    systems[sid][key] = text.replace('\\n', '\n')
                
                # 处理常规角色数据
                else:
                    cid, text = match
                    # 严格过滤：如果是 core, starlight 或 命座衍生ID，跳过
                    if cid in ['core', 'starlight'] or re.search(r'_c[0-6]$', cid): 
                        continue
                    
                    if cid not in characters: characters[cid] = {"char_id": cid}
                    characters[cid][col_type] = text.replace('\\n', '\n')

    # ------------------------------------------------------------------
    # B. 读取 Static Modifiers (修正 & 命座逻辑)
    # ------------------------------------------------------------------
    if os.path.exists(PATH_STATIC_MODS):
        print(f"🔍 解析 Static Modifiers...")
        files = glob.glob(os.path.join(PATH_STATIC_MODS, "*.txt"))
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 匹配 gacha_xxx = { ... }
            matches = re.finditer(r'(gacha_\w+)\s*=\s*', content)
            for m in matches:
                full_name = m.group(1)
                code = extract_brace_content(content, m.end())
                code = clean_code(code)

                # 1. 命座修正 gacha_hutao_c1_modifier
                c_match = re.match(r'gacha_(\w+)_(c[0-6])_modifier', full_name)
                if c_match:
                    cid, c_lvl = c_match.groups()
                    if cid in characters:
                        characters[cid][f"code_{c_lvl}"] = code
                    continue

                # 2. 基础修正 gacha_hutao_modifier
                m_match = re.match(r'gacha_(\w+)_modifier', full_name)
                if m_match:
                    cid = m_match.group(1)
                    if cid == "core": # 系统级
                        if "gacha_core_modifier" not in systems: systems["gacha_core_modifier"] = {"sys_id": "gacha_core_modifier"}
                        systems["gacha_core_modifier"]["code_logic"] = code
                        continue
                    if cid in characters:
                        characters[cid]["code_modifier"] = code
                    continue
                
                # 3. 其他归为系统
                if full_name not in systems: systems[full_name] = {"sys_id": full_name}
                systems[full_name]["code_logic"] = code

    # ------------------------------------------------------------------
    # C. 读取 Traits (特质逻辑)
    # ------------------------------------------------------------------
    if os.path.exists(PATH_TRAITS):
        print(f"🔍 解析 Traits...")
        files = glob.glob(os.path.join(PATH_TRAITS, "*.txt"))
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            matches = re.finditer(r'gacha_(\w+)_(origin|awakened|transcended)_trait\s*=\s*', content)
            for m in matches:
                cid = m.group(1)
                type_ = m.group(2)
                
                # 排除 _c0 这种垃圾 ID
                if re.search(r'_c[0-6]$', cid): continue

                if cid in characters:
                    # 提取 modifier = { ... }
                    body = extract_brace_content(content, m.end() - 1 if content[m.end()-1] == '{' else m.end())
                    mod_match = re.search(r'modifier\s*=\s*', body)
                    if mod_match:
                        code = extract_brace_content(body, mod_match.end())
                        characters[cid][f"code_trait_{type_}"] = clean_code(code)

    # ------------------------------------------------------------------
    # D. 输出 CSV
    # ------------------------------------------------------------------
    char_headers = [
        "char_id", "pool_type", "rarity", "element", "gender", "age", "culture", "religion",
        "adm_min", "adm_max", "dip_min", "dip_max", "mil_min", "mil_max",
        "first_name", "last_name", 
        "loc_trait_origin_name", "loc_trait_origin_desc", "code_trait_origin",
        "loc_trait_awakened_name", "loc_trait_awakened_desc", "code_trait_awakened",
        "loc_trait_transcended_name", "loc_trait_transcended_desc", "code_trait_transcended",
        "loc_modifier_name", "loc_modifier_desc", "code_modifier",
        "c0_name", "code_c0", "c1_name", "code_c1", "c2_name", "code_c2", 
        "c3_name", "code_c3", "c4_name", "code_c4", "c5_name", "code_c5", "c6_name", "code_c6",
        "evt_meet_title", "evt_meet_desc", "evt_meet_opt",
        "evt_up_title", "evt_up_desc", "evt_up_opt",
        "evt_max_title", "evt_max_desc", "evt_max_opt",
        "evt_awk_title", "evt_awk_desc", "evt_awk_opt",
        "evt_tra_title", "evt_tra_desc", "evt_tra_opt",
        "asset_portrait_path", "asset_icon_origin", "asset_icon_awakened", "asset_icon_transcended"
    ]
    
    sys_headers = ["sys_id", "type", "loc_name", "loc_desc", "code_logic", "icon_path"]

    print(f"💾 写入 {OUT_CHAR_CSV} ...")
    with open(OUT_CHAR_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=char_headers)
        writer.writeheader()
        for cid, data in characters.items():
            # 补全默认值
            for h in char_headers:
                if h not in data: data[h] = ""
            writer.writerow(data)

    print(f"💾 写入 {OUT_SYS_CSV} ...")
    with open(OUT_SYS_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=sys_headers)
        writer.writeheader()
        for sid, data in systems.items():
            for h in sys_headers:
                if h not in data: data[h] = ""
            writer.writerow(data)

    print("✅ 安全提取完成。")

if __name__ == "__main__":
    main()