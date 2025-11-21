<div align=center> <img src="https://sansme.oss-cn-beijing.aliyuncs.com/thumbnail.png" width="360" height="360"></div>

# EU5 Gacha Mod

> **Current Version**: Phase 1 (MVP)
> **Engine**: Jomini (Project Caesar)

This mod introduces a "Gacha" (Wish) system into EU5, allowing players to summon powerful characters from other worlds (starting with **Sangonomiya Kokomi** from Genshin Impact) to serve as advisors and generals.

## 📚 Documentation

We have reorganized the documentation into the `docs/` folder:

| Document | Description |
| :--- | :--- |
| [**1. Project Overview**](docs/1_project_overview.md) | Vision, core loop, and development roadmap. |
| [**2. Gacha System Design**](docs/2_design_gacha_system.md) | The math behind the "Soft Pity + 50/50" logic and the Pool architecture. |
| [**3. Story System Design**](docs/3_design_story_system.md) | How characters react dynamically to War, Plague, and Conquest. |
| [**4. Workflow: Add Character**](docs/4_workflow_add_character.md) | Step-by-step guide to adding new characters (e.g., Raiden Shogun). |
| [**5. Technical Reference**](docs/5_reference_technical.md) | Localization syntax, troubleshooting, and lessons learned. |

## 🚀 Features

*   **True Gacha Probability**: Implements a robust PRNG with Soft Pity (74+) and Hard Pity (90).
*   **Dynamic Rewards**: 50/50 mechanic for UP characters vs Standard characters.
*   **Immersive Events**: High-quality flavor text and "Toast" notifications.
*   **Multiplayer Safe**: Prevents duplicate unique characters in multiplayer sessions.

## 🛠️ Installation

1.  Place the mod folder in your EU5 `mod/` directory.
2.  Enable the mod in the launcher.
3.  In-game, look for the "Gacha" decision or button to start wishing.

---
*Design by [User Name] & Antigravity*
