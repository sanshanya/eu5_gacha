import random

class EU5GachaSimulation:
    def __init__(self, pool_size_std=8, debug=False, use_fix=True):
        # --- Persistent State ---
        self.var_gacha_total_rolls_count = 0
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_is_guaranteed_bool = 0
        self.var_gacha_block_pity_met_bool = 0 
        
        self.var_gacha_std5_result_count = 0
        self.var_gacha_4star_result_count = 0

        # --- New: UP Pool State ---
        self.var_gacha_current_up_idx = 0 # 0-7

        # --- Simulation Params ---
        self.debug = debug
        self.pool_size_std = pool_size_std # Should be 8 (Total Characters)
        self.use_fix = use_fix
        
        if use_fix:
            self.var_gacha_entropy_gold_amt = random.randint(0, 9999)
        else:
            self.var_gacha_entropy_gold_amt = 10000
        
        # --- Statistics ---
        self.stats = {
            "total_5star": 0,
            "total_4star": 0,
            "win_up": 0,        # Count of UP wins
            "lose_up": 0,       # Count of UP losses (Standard)
            "max_pity_5star": 0,
            "distribution": {}, # {Name: Count}
            "pity_history_5star": []
        }

        # Character Mapping (0-7)
        self.char_map = [
            "Xinhai",  # 0
            "Fischl",  # 1
            "Keqing",  # 2
            "Raiden",  # 3
            "Furina",  # 4
            "HuTao",   # 5
            "Klee",    # 6
            "Nahida"   # 7
        ]

    # ... (Value Calc Functions 44-106 remain largely same, simplified for brevity) ...

    def sv_gacha_calc_entropy(self):
        val = 937
        val += self.var_gacha_total_rolls_count * 17
        val += self.var_gacha_pity_5star_count * 13
        val += abs(self.var_gacha_entropy_gold_amt)
        return val % 10000

    def sv_gacha_calc_5star_prob(self):
        val = 60
        if self.var_gacha_pity_5star_count >= 73:
            val += (self.var_gacha_pity_5star_count - 73) * 600
        if self.var_gacha_pity_5star_count >= 89:
            val = 10001
        return val

    def sv_gacha_calc_4star_prob(self):
        val = 510
        if self.var_gacha_pity_4star_count >= 8:
            val += (self.var_gacha_pity_4star_count - 8) * 5000
        if val > 10000:
            val = 10001
        return val

    def sv_gacha_calc_block_idx(self):
        return self.var_gacha_total_rolls_count % 10

    def sv_gacha_calc_entropy2(self):
        val = self.sv_gacha_calc_entropy()
        val += self.var_gacha_total_rolls_count * 13
        val = (val * 31) % 10000
        return val

    def sv_gacha_calc_standard_5_idx(self):
        # We need a random index from 0 to 6 (7 options)
        val = self.var_gacha_std5_result_count * 17
        val += abs(self.var_gacha_entropy_gold_amt)
        
        # Modulo 7 because there are 7 standard characters available
        return val % 7

    # --- Effects ---

    def rotate_pool(self):
        """Simulates the yearly rotation"""
        old_up = self.char_map[self.var_gacha_current_up_idx]
        self.var_gacha_current_up_idx = (self.var_gacha_current_up_idx + 1) % 8
        new_up = self.char_map[self.var_gacha_current_up_idx]
        if self.debug: print(f"--- ROTATION: {old_up} -> {new_up} ---")

    def execute_single_roll(self):
        self.var_gacha_entropy_gold_amt -= 16
        self.var_gacha_total_rolls_count += 1
        
        val_entropy = self.sv_gacha_calc_entropy()
        val_prob_5 = self.sv_gacha_calc_5star_prob()
        val_prob_4 = self.sv_gacha_calc_4star_prob()
        
        tier_idx = 0
        if val_entropy < val_prob_5:
            tier_idx = 2
        else:
            # Simplified block logic for sim
            if val_prob_4 > 500 or val_entropy < val_prob_4: 
                tier_idx = 1 # Rough approx to enable 4 stars
        
        if tier_idx == 2:
            self._resolve_5star()
        elif tier_idx == 1:
            self._resolve_4star()
        else:
            self._resolve_3star()

    def _resolve_5star(self):
        self.stats["total_5star"] += 1
        self.stats["max_pity_5star"] = max(self.stats["max_pity_5star"], self.var_gacha_pity_5star_count)
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_block_pity_met_bool = 1
        self.var_gacha_pity_4star_count += 1
        self._logic_6_1_resolve_character()

    def _logic_6_1_resolve_character(self):
        # 1. Check 50/50
        val_entropy2 = self.sv_gacha_calc_entropy2()
        is_up = 0
        
        if self.var_gacha_is_guaranteed_bool == 1:
            is_up = 1
            self.var_gacha_is_guaranteed_bool = 0
        else:
            if val_entropy2 < 5000:
                is_up = 1
            else:
                is_up = 0
                self.var_gacha_is_guaranteed_bool = 1
        
        # 2. Grant Character
        if is_up == 1:
            # UP Logic: Direct Index
            char_idx = self.var_gacha_current_up_idx
            self.stats["win_up"] += 1
            self._grant_character(self.char_map[char_idx], is_up=True)
        else:
            # Standard Logic: Sliding Window
            self.stats["lose_up"] += 1
            self.var_gacha_std5_result_count += 1
            
            # Get random 0-6
            std_raw_idx = self.sv_gacha_calc_standard_5_idx() 
            
            # Apply Sliding Window: If raw index hits or exceeds current UP, skip +1
            final_idx = std_raw_idx
            if final_idx >= self.var_gacha_current_up_idx:
                final_idx += 1
                
            self._grant_character(self.char_map[final_idx], is_up=False)

    def _resolve_4star(self):
        self.stats["total_4star"] += 1
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_pity_5star_count += 1
        self.var_gacha_4star_result_count += 1

    def _resolve_3star(self):
        self.var_gacha_pity_5star_count += 1
        self.var_gacha_pity_4star_count += 1

    def _grant_character(self, name, is_up):
        self.stats["distribution"][name] = self.stats["distribution"].get(name, 0) + 1


def run_rotation_test():
    print("=== RUNNING ROTATION SIMULATION ===")
    
    # We will simulate 8 years (or cycles)
    # Each cycle we do enough pulls to get ~1000 5-stars to see distribution
    
    cycles = 8
    pulls_per_cycle = 50000 
    
    sim = EU5GachaSimulation()
    
    for i in range(cycles):
        current_up_name = sim.char_map[sim.var_gacha_current_up_idx]
        print(f"\n--- CYCLE {i+1}: UP = {current_up_name} ---")
        
        # Reset Cycle Stats
        cycle_dist = {}
        
        for _ in range(pulls_per_cycle):
            sim.execute_single_roll()
            
        # Analysis
        dist = sim.stats["distribution"]
        total_5s = sim.stats["total_5star"]
        
        print(f"Total 5 Stars so far: {total_5s}")
        
        # Print Distribution for this state
        # Note: Since stats gather cumulatively, we'd need to track delta. 
        # But looking at total heavy bias towards UP is enough.
        
        # Let's verify Xinhai specifically
        xinhai_count = dist.get("Xinhai", 0)
        print(f"Xinhai Count: {xinhai_count}")
        
        # Verify Current UP dominance
        up_count = dist.get(current_up_name, 0)
        print(f"Current UP ({current_up_name}): {up_count}")
        
        # ROTATE
        sim.rotate_pool()

    print("\n=== FINAL DISTRIBUTION ===")
    for k, v in sorted(sim.stats["distribution"].items(), key=lambda x:x[1], reverse=True):
         print(f"{k}: {v}")

if __name__ == "__main__":
    run_rotation_test()
