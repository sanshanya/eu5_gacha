# Character Creation Wrapper Comparison

## 1. Overview
We compared the reference mod's `ls_snow_create_common_effect` with our `gacha_register_new_character` + `gacha_create_xinhai_effect` architecture.

| Feature | Reference Mod (`ls_snow`) | Our Mod (`gacha`) |
| :--- | :--- | :--- |
| **Philosophy** | **"All-in-One" Factory** | **"Manager + Kernel" Split** |
| **Creation** | Inside the common effect | Inside the specific wrapper |
| **Duplicates** | Ignored (or kills old versions) | **Constellation Upgrade** (Logic handled in wrapper) |
| **Parameters** | Heavily templated (`$who$`) | Hardcoded in wrapper (Safer) |
| **Flexibility** | High for identical heroes | High for unique mechanics per char |

## 2. Detailed Analysis

### Reference Mod: `ls_snow_create_common_effect`
The reference mod uses a single "Factory" effect that takes `$who$` and `$age$` as arguments.
*   **Pros**: Extremely concise. Adding a new character just requires one line: `ls_snow_create_common_effect = { who = lifu age = 19 }`.
*   **Cons**:
    *   **Rigid Duplicate Logic**: It simply checks if the character exists and skips creation if so. It cannot handle "Constellation Upgrades" or "Refunds" easily without making the common effect extremely complex.
    *   **Template Risk**: Passing `$who$` into `first_name = ls_snow_$who$_first_name` relies on the engine correctly parsing nested variables in `create_character`, which can be unstable.

### Our Mod: `gacha_create_xinhai_effect` + `gacha_register_new_character`
We use a "Wrapper + Kernel" approach.
1.  **Wrapper (`gacha_create_xinhai_effect`)**: Handles the *logic* of acquisition.
    *   Checks if player owns the character -> **Upgrade Constellation**.
    *   Checks if another player owns it -> **Refund**.
    *   If new -> **Create Character** (Hardcoded parameters for safety).
2.  **Kernel (`gacha_register_new_character`)**: Handles the *chores* after creation.
    *   Adds common traits/modifiers.
    *   Registers to global lists.
    *   Moves to correct estate.

## 3. Conclusion
**Our implementation is better suited for a Gacha System.**

The reference mod's approach is excellent for a **"Unique Hero"** system where you either have the hero or you don't. However, for a **Gacha** system where "Duplicates" are a core mechanic (Constellations/Pity), we *need* the logic to be exposed in the wrapper layer, not hidden inside a common factory.

**Recommendation**:
*   **Keep our current structure.** It provides the necessary flexibility for the Gacha loop.
*   **Adopt their "List Registration"**: We already do this (`add_to_global_variable_list`), which is good.
*   **Adopt their "Estate Assignment"**: We should ensure we assign them to our custom "Gacha Guild" estate (once created) rather than just the Crown Estate, similar to their `ls_snow_Heimdall_estate`.
