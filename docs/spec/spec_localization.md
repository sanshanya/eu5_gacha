# Localization Standards & Architecture

- **Version**: 1.0
- **Last Updated**: 2025-12-04
- **Official Reference**: [EU5 Wiki - Localization](https://eu5.paradoxwikis.com/Localization)

> [!IMPORTANT]
> **Golden Rule**: All player-facing text MUST use localization keys. No hardcoded text in scripts.
> **Encoding**: All `.yml` files MUST be **UTF-8 with BOM** (matches EU5 wiki).
> **Scope Case**: Use uppercase scopes in data functions (e.g., `ROOT.ScriptValue('foo')`, `ROOT.GetVariable('bar')`) to match engine expectations from the official wiki.

---

## 1. File Structure (Modularization)

We abandon the monolithic file approach. Localization files are split by domain and character.

**Root Directory**: `in_game/localization` (Moving from `main_menu` to keep with code)

| File Pattern | Purpose | Example |
|:---|:---|:---|
| `gacha_core_l_<lang>.yml` | System UI, menus, common interactions | `gacha_core_l_simp_chinese.yml` |
| `gacha_modifiers_l_<lang>.yml` | Static modifiers, modifier types | `gacha_modifiers_l_english.yml` |
| `gacha_char_<name>_l_<lang>.yml` | Specific character text (events, traits) | `gacha_char_kokomi_l_simp_chinese.yml` |
| `gacha_concepts_l_<lang>.yml` | Game concepts (tooltips) | `gacha_concepts_l_english.yml` |

---

## 2. Key Naming Conventions

Keys should be hierarchical and descriptive.

| Category | Pattern | Example |
|:---|:---|:---|
| **Events** | `gacha_<char>_event.<id>.<part>` | `gacha_kokomi_event.1.t` (Title), `gacha_kokomi_event.1.desc` |
| **Modifiers** | `<modifier_name>` | `gacha_kokomi_modifier` |
| **Traits** | `<trait_name>` | `gacha_kokomi_origin_trait` |
| **Interactions** | `<interaction_name>` | `gacha_wish_interaction` |
| **UI/Menu** | `gacha_ui_<feature>_<element>` | `gacha_ui_wish_button_confirm` |

---

## 3. Data Functions & Dynamic Text

Use Bracket Notation `[...]` for dynamic data.

### 3.1 Variable Display (Crucial)

#### A. Numerical Variables
To display a number stored in a variable:
- **Syntax**: `[SCOPE.GetVariable('var_name')|format]` or `[SCOPE.Var('var_name').GetValue|format]`
- **Example**: `[ROOT.GetVariable('gacha_starlight')|0]`

#### B. Flag Variables (Localization Keys)
To display a localization key stored in a variable (e.g., `set_variable = { name = title value = flag:king_title }`):
- **Syntax**: `[SCOPE.Var('var_name').GetFlagName]`
- **Example**: `[ROOT.Var('title').GetFlagName]` -> Displays "King"
- **Note**: This is used for dynamic text replacement (e.g., changing titles based on gender/culture).

### 3.2 Script Value Display (Calculated Values)
To display a calculated `script_value` (defined in `common/script_values`):
- **Syntax**: `[SCOPE.ScriptValue('value_name')|format]`
- **Example**: `[ROOT.ScriptValue('gacha_pity_calculation')|0]`
- **Description**: `[SCOPE.GetScriptValueDesc('value_name')]` (Displays the localized description of the value)

### 3.3 Common Data Functions
- **Names**: `[Root.GetName]`, `[Scope.GetCharacter.GetFirstName]`

### 3.4 Advanced Formatting

#### A. Custom Colors & Formatting (via .gui)
- **Syntax**: `#<key> Text#!` (e.g., `#R Text#!` for red, if 'R' is defined)
- **Definition**: Colors and other text formatting are defined in `.gui` files using `textformatting` blocks (e.g., `main_menu/gui/textformatting.gui`).
- **Nesting**: `#R #Y Text#! #!`
- **Joining**: `#R;Y Text#!`

#### B. Text Icons & Concepts
- **Concepts**: `£concept_name£` (Provides tooltips, defined in localization files)
- **Icons**: `@icon_name!` (e.g., `@trigger_yes!`, `@adm!`, likely defined in `.gfx` or `.gui`)

#### C. Standard Colors (Legacy/Common)
Prefer `#color_*` / `#bold` formatting from the official EU5 wiki. Legacy `§` codes are still accepted but avoid introducing new ones.
- Examples: `#color_yellow Text#!`, `#bold Bolded#!`, `#bold;color_yellow Text#!`.
- Legacy (avoid new): `§Y` (Yellow), `§R` (Red), `§G` (Green), `§B` (Blue), `§!` (End).

---

## 4. Concepts (Game Concepts)

Use Game Concepts to provide nested tooltips for complex terms.

**Syntax**:
- In Text: `This character is a £concept_gacha_traveler£.`
- Key Definition: `concept_gacha_traveler: "Traveler"`
- Tooltip Definition: `concept_gacha_traveler_desc: "A hero from another world..."`

**Common Concepts**:
- `concept_gacha_wish` (祈愿)
- `concept_gacha_starlight` (星辉)
- `concept_gacha_constellation` (命之座)

---

## 5. Workflow

1.  **Create/Edit Script**: Add keys to script files (e.g., `title = gacha_event.1.t`).
2.  **Update Localization**: Open the relevant `.yml` file (e.g., `gacha_char_kokomi_l_english.yml`).
3.  **Add Key**: Add the key and text.
4.  **Verify**: Check in-game. Use `reload localization` (if available) or restart.

---

## 6. Migration Plan (Current Task)

1.  **Move**: Move localization from `main_menu` to `in_game/localization`.
2.  **Split**: Break `eu_gacha_l_*.yml` into the modular files defined above.
3.  **Refactor**: Rename keys to match the new convention (if necessary, but prioritize splitting first).
4.  **Verify**: Ensure no missing keys.

---

## 7. Base File Patch Log (源文件修改登记)

> [!IMPORTANT]
> 仅在引擎**不支持注入/追加**时允许覆盖原文件，且必须在此登记原因与范围。

- 2025-12-22：**已撤销** base 修改，改为在 mod 内覆盖文件：
  - `in_game/common/customizable_localization/country_history.txt`
  - 说明：以同名文件覆盖 `country_history` 列表（完整复制原版 + GS1 规则）。
