# Snow Project Reference Analysis

## Overview
The "Snow Project" is a character-focused mod that emphasizes "Waifu" collection, management, and powerful cheat-like mechanics. Unlike our Gacha mod, which focuses on the *acquisition* process (RNG, Pity), the Snow Project focuses on the *management* and *interaction* with these characters after they are acquired.

## Key Features & Learnings

### 1. Customizable Estate Localization
**Feature**: The `ls_snow_Heimdall_estate` changes its name dynamically based on the country's culture, religion, or language (e.g., "Noumin" for Japanese, "Krestyanstvo" for Russian).
**Application**: We can use this for our "Gacha Guild" or "Adventurer's Guild" estate to make it feel native to every culture (e.g., "Adventurer's Guild" in English, "Maoxian Zhe" in Chinese).

### 2. Character Interactions
**Feature**: The mod uses `character_interactions` extensively.
*   `ls_snow_waifu_interaction`: A specific interaction menu for Waifu characters.
*   `ls_snow_master_interaction`: A self-interaction for the player ruler to open a management menu.
**Application**: We should implement a "Gacha Character Interaction" system.
*   **Gift**: Give items to increase loyalty/stats.
*   **Commission**: Send them on specific missions (events).
*   **Talk**: Trigger flavor events.

### 3. Enforced Relationships (On-Actions)
**Feature**: The mod strictly enforces relationships using `on_actions`.
*   `on_character_marriage`: Prevents Waifus from marrying anyone but the Master. If they do, they are forcibly divorced and the spouse is killed.
*   `on_character_death`: If the Master dies, all Waifus become "Widows" and move to the heir's court.
**Application**: We can use this to ensure Gacha characters remain loyal or handle "inheritance" of the Gacha roster if the ruler dies (though in our design, they belong to the *country/player*, not necessarily the ruler personally).

### 4. Custom Subject Types
**Feature**: A custom subject type (`ls_snow_common_vassal`) that requires the subject's ruler to *not* be a Waifu, or else the relationship breaks.
**Application**: Less relevant for us immediately, but useful if we add "Gacha Nations" or "Character Fiefdoms" later.

### 5. Debug & Sandbox Tools
**Feature**: `ls_snow_events.1` acts as a "Cheat Menu" to:
*   Spawn all characters at once.
*   Toggle immortality.
*   Force marriage with everyone.
**Application**: We should add a "Debug Menu" event for testers to instantly add specific characters or reset pity.

## Technical Implementation Details

### Dynamic Localization
```yaml
ls_snow_Heimdall_estate:
    text:
        localization_key: ls_snow_Heimdall_estate_noumin
        trigger: { culture.language = language:japanese_language }
```

### Character Spawning Wrapper
The mod uses a `ls_snow_create_common_effect` to standardize character creation, which we have already adopted with `gacha_register_new_character`.

### Trait-Based Logic
The mod relies heavily on checking `has_trait = ls_snow_WAIFU_trait`. We should ensure all our logic checks for a `gacha_character_trait` to distinguish our characters from vanilla ones.

## Recommendation
We should prioritize implementing **Character Interactions** and **Customizable Estate Localization** to enhance the "post-pull" experience. The "Get All" debug option is also a quick win for development.
