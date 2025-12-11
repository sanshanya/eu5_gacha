import random

class EU5GachaSimulation:
    def __init__(self, pool_size_std=7, debug=False, use_fix=True):
        # --- Persistent State (Saved Variables) ---
        self.var_gacha_total_rolls_count = 0
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_is_guaranteed_bool = 0
        self.var_gacha_block_pity_met_bool = 0 # 0 or 1
        
        self.var_gacha_std5_result_count = 0
        self.var_gacha_4star_result_count = 0
        
        # --- Simulation Params ---
        self.debug = debug
        self.pool_size_std = pool_size_std # Optimized: Should be 7
        self.use_fix = use_fix
        
        # Optimized: Randomize Initial Entropy
        if use_fix:
             # Simulates 'random_list' initialization (0-9999)
            self.var_gacha_entropy_gold_amt = random.randint(0, 9999)
        else:
            # Legacy Bug: Static initialization
            self.var_gacha_entropy_gold_amt = 10000
        
        # --- Statistics ---
        self.stats = {
            "total_5star": 0,
            "total_4star": 0,
            "up_5star": 0,
            "std_5star": 0,
            "max_pity_5star": 0,
            "distribution": {},
            "pity_history_5star": []
        }

    # ===================================================
    # SCRIPT VALUES (Data Layer)
    # Replicating `gacha_eu_values.txt`
    # ===================================================

    def sv_gacha_calc_entropy(self):
        # value = 937
        val = 937
        
        # add = { value = var:gacha_total_rolls_count multiply = 17 }
        val += self.var_gacha_total_rolls_count * 17
        
        # add = { value = var:gacha_pity_5star_count multiply = 13 }
        val += self.var_gacha_pity_5star_count * 13
        
        # add = { value = var:gacha_entropy_gold_amt abs = yes }
        val += abs(self.var_gacha_entropy_gold_amt)
        
        # modulo = 10000
        return val % 10000

    def sv_gacha_calc_5star_prob(self):
        # value = 60
        val = 60
        
        # if pity >= 73
        if self.var_gacha_pity_5star_count >= 73:
            # add = { value = pity subtract = 73 multiply = 600 }
            val += (self.var_gacha_pity_5star_count - 73) * 600
            
        # Hard Pity Safety: if pity >= 89, value = 10001
        if self.var_gacha_pity_5star_count >= 89:
            val = 10001
            
        return val

    def sv_gacha_calc_4star_prob(self):
        # value = 510
        val = 510
        
        # if pity >= 8
        if self.var_gacha_pity_4star_count >= 8:
            # add = { value = pity subtract = 8 multiply = 5000 }
            val += (self.var_gacha_pity_4star_count - 8) * 5000
            
        # max = 10001 (Logic implies capping, though code structure typically adds)
        # In code: "max = 10001" usually means "clamp max to", 
        # but here let's assume it ensures 100% at some point.
        # Actually standard Paradox math: `max` clamps the result. 
        # But if the formula exceeds 10000, it guarantees drop.
        if val > 10000:
            val = 10001
        return val

    def sv_gacha_calc_block_idx(self):
        # value = 0 + total % 10
        return self.var_gacha_total_rolls_count % 10

    def sv_gacha_calc_entropy2(self):
        # value = gacha_calc_entropy_sv
        val = self.sv_gacha_calc_entropy()
        
        # add = { value = total * 13 }
        val += self.var_gacha_total_rolls_count * 13
        
        # multiply = 31, modulo = 10000
        val = (val * 31) % 10000
        return val

    def sv_gacha_calc_standard_5_idx(self):
        # (std_count * 17) % pool_size
        val = self.var_gacha_std5_result_count * 17
        
        # Optimized: Add Entropy
        if self.use_fix:
            val += abs(self.var_gacha_entropy_gold_amt)
            
        return val % self.pool_size_std

    # ===================================================
    # EFFECTS (Logic Layer)
    # Replicating `gacha_logic_effects.txt`
    # ===================================================

    def execute_single_roll(self):
        # self.var_gacha_entropy_gold_amt = random.randint(0, 500) # Simulate changing gold
        # Actually gacha logic decrements gold by 16. Let's simulate that behavior.
        # Although in the real game gold is an input, here we just need it to vary to provide entropy.
        # Let's say user has infinite gold but it changes.
        self.var_gacha_entropy_gold_amt = (self.var_gacha_entropy_gold_amt - 16) 
        
        # Step 1: State Step
        self.var_gacha_total_rolls_count += 1
        
        # Step 2: Snapshots
        val_entropy = self.sv_gacha_calc_entropy()
        val_prob_5 = self.sv_gacha_calc_5star_prob()
        val_prob_4 = self.sv_gacha_calc_4star_prob()
        val_block_idx = self.sv_gacha_calc_block_idx()
        
        if self.debug:
            print(f"Roll #{self.var_gacha_total_rolls_count} | Entropy: {val_entropy} | Pity5: {self.var_gacha_pity_5star_count} (Prob: {val_prob_5}) | Pity4: {self.var_gacha_pity_4star_count}")

        # Block Reset Logic
        if val_block_idx == 1:
            self.var_gacha_block_pity_met_bool = 0
            
        # Step 3: Tier Decision
        tier_idx = 0
        
        # 5 Star Check
        if val_entropy < val_prob_5:
            tier_idx = 2
        
        # 4 Star Check (Else If)
        # Logic: OR( entropy < prob4, AND( block_idx == 0, block_met == 0 ) )
        else:
            is_block_guarantee = (val_block_idx == 0 and self.var_gacha_block_pity_met_bool == 0)
            if (val_entropy < val_prob_4) or is_block_guarantee:
                tier_idx = 1
                
        # Step 4: Resolve
        if tier_idx == 2:
            self._resolve_5star()
        elif tier_idx == 1:
            self._resolve_4star()
        else:
            self._resolve_3star()
            
    def execute_newbie_pull(self):
        """
        Replicates 'gacha_free_first_roll' outcome.
        - Direct call to gacha_resolve_5star_and_save_scope
        - BYPASSES Pity Reset (Logic 5.1)
        - DOES consume/set Guarantee (Logic 6.1)
        """
        if self.debug: print(f"*** NEWBIE FREE PULL (Guaranteed 5*) ***")
        self._logic_6_1_resolve_character()

    def _resolve_5star(self):
        # Logic 5.1 (Standard path): Reset Pity THEN Resolve Character
        if self.debug: print(f"*** 5 STAR! ***")
        self.stats["total_5star"] += 1
        self.stats["pity_history_5star"].append(self.var_gacha_pity_5star_count)
        self.stats["max_pity_5star"] = max(self.stats["max_pity_5star"], self.var_gacha_pity_5star_count)
        
        # Update Pity (The 5.1 part)
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_block_pity_met_bool = 1
        self.var_gacha_pity_4star_count += 1
        
        # Resolve Character (The 6.1 part)
        self._logic_6_1_resolve_character()

    def _logic_6_1_resolve_character(self):
        # Replicates 'gacha_resolve_5star_and_save_scope'
        
        # 1. Calc Entropy2
        val_entropy2 = self.sv_gacha_calc_entropy2()
        is_up = 0
        
        # 2. Logic (50/50 & Guarantee)
        if self.var_gacha_is_guaranteed_bool == 1:
            is_up = 1
            self.var_gacha_is_guaranteed_bool = 0
        else:
            if val_entropy2 < 5000:
                is_up = 1
            else:
                is_up = 0
                self.var_gacha_is_guaranteed_bool = 1
                
        # 3. Grant
        if is_up == 1:
            self._grant_character("Kokomi (UP)")
            self.stats["up_5star"] += 1
        else:
            self.stats["std_5star"] += 1
            self.var_gacha_std5_result_count += 1
            idx = self.sv_gacha_calc_standard_5_idx()
            
            # OPTIMIZED MAPPING (Pool Size 7)
            # This simulates the "List-based" approach where index 0-6 maps 1:1
            standard_pool = [
                "Keqing",
                "Raiden",
                "Furina",
                "Hu Tao",
                "Klee",
                "Nahida",
                "Fischl"
            ]
            
            if 0 <= idx < len(standard_pool):
                 char = standard_pool[idx]
            else:
                 # Should not happen with correct Modulo
                 char = "ERROR_INDEX_OUT_OF_BOUNDS"
                 
            self._grant_character(char)

    def _resolve_4star(self):
        if self.debug: print(f"--- 4 Star ---")
        self.stats["total_4star"] += 1
        
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_block_pity_met_bool = 1
        self.var_gacha_pity_5star_count += 1
        
        self.var_gacha_4star_result_count += 1
        
    def _resolve_3star(self):
        self.var_gacha_pity_5star_count += 1
        self.var_gacha_pity_4star_count += 1

    def _grant_character(self, name):
        self.stats["distribution"][name] = self.stats["distribution"].get(name, 0) + 1


def run_test(pulls=100000, simulation_runs=1, pool_size=8):
    print(f"Running Full Gacha System Simulation ({pulls} pulls)...")
    print(f"Config: Standard Pool Size = {pool_size}")
    
    
    sim = EU5GachaSimulation(pool_size_std=pool_size)
    
    # Run Newbie Pull (One-time, guaranteed)
    sim.execute_newbie_pull()

    # Run
    for _ in range(pulls):
        sim.execute_single_roll()
        
    # Report
    s = sim.stats
    print("\n=== SIMULATION REPORT ===")
    print(f"Total Pulls: {pulls}")
    print(f"Total 5-Stars: {s['total_5star']} ({s['total_5star']/pulls*100:.3f}%)")
    print(f"Total 4-Stars: {s['total_4star']} ({s['total_4star']/pulls*100:.3f}%)")
    
    # 5-Star Details
    print("\n--- 5-Star Details ---")
    print(f"UP (Kokomi): {s['up_5star']} ({s['up_5star']/s['total_5star']*100 if s['total_5star'] else 0:.1f}%)")
    print(f"Standard:    {s['std_5star']} ({s['std_5star']/s['total_5star']*100 if s['total_5star'] else 0:.1f}%)")
    print(f"Max Pity Reached: {s['max_pity_5star']}")
    if s['pity_history_5star']:
        avg_pity = sum(s['pity_history_5star']) / len(s['pity_history_5star'])
        print(f"Avg Pity: {avg_pity:.2f}")
        
    # Standard Distribution
    print("\n--- Standard Character Distribution (The Bug Check) ---")
    stds = {k:v for k,v in s['distribution'].items() if "UP" not in k}
    total_std_pulls = sum(stds.values())
    
    print(f"{'Character':<15} | {'Count':<8} | {'% of Std':<10}")
    print("-" * 40)
    for char, count in sorted(stds.items(), key=lambda x: x[1], reverse=True):
        p = (count / total_std_pulls * 100) if total_std_pulls else 0
        print(f"{char:<15} | {count:<8} | {p:.2f}%")
        
    # Bias Check
    if "Fischl" in stds:
        fischl = stds["Fischl"]
        others = [v for k,v in stds.items() if k != "Fischl"]
        if others:
            avg_others = sum(others) / len(others)
            ratio = fischl / avg_others
            print(f"\nBias Factor (Fischl / Avg Others): {ratio:.2f}x")
            
def check_newbie_distribution(runs=10000):
    print(f"\n=== NEWBIE PULL DISTRIBUTION CHECK ({runs} runs) ===")
    counts = {}
    
    for i in range(runs):
        sim = EU5GachaSimulation(pool_size_std=7, use_fix=True)
        # Reset debug to suppress logs
        sim.debug = False
        sim.execute_newbie_pull()
        
        pulled = [k for k,v in sim.stats["distribution"].items() if v > 0][0]
        counts[pulled] = counts.get(pulled, 0) + 1
        
    print(f"Distribution: {counts}")
    
    # Check Standard Bias specifically
    stds = {k:v for k,v in counts.items() if "UP" not in k}
    total_std = sum(stds.values())
    if total_std > 0:
        print("\nStandard Character Rates (Newbie Pull):")
        for k,v in sorted(stds.items(), key=lambda x:x[1], reverse=True):
            print(f"{k}: {v} ({v/total_std*100:.2f}%)")
    else:
        print("No standard characters pulled (Extremely lucky?)")

def check_determinism(runs=10):
    print(f"\n=== NEWBIE PULL DETERMINISM CHECK (Optimized: {runs} fresh saves) ===")
    outcomes = []
    
    for i in range(runs):
        # FRESH START with FIX ENABLED
        sim = EU5GachaSimulation(pool_size_std=7, use_fix=True)
        
        # Capture the first pull
        sim.debug = False
        sim.execute_newbie_pull()
        
        # Find who was pulled
        pulled = [k for k,v in sim.stats["distribution"].items() if v > 0][0]
        outcomes.append(pulled)
        print(f"Run #{i+1}: {pulled}")
        
    if len(set(outcomes)) == 1:
        print(f"CONCLUSION: DETERMINISTIC (FAIL). Always pulls '{outcomes[0]}'.")
    else:
        print(f"CONCLUSION: RANDOM (PASS). Outcomes varied: {set(outcomes)}")

def run_test(pulls=100000, simulation_runs=1, pool_size=7):
    print(f"Running Full Gacha System Simulation ({pulls} pulls)...")
    print(f"Config: Standard Pool Size = {pool_size} (Optimized)")
    
    sim = EU5GachaSimulation(pool_size_std=pool_size, use_fix=True)
    
    # Run Newbie Pull (One-time, guaranteed)
    sim.execute_newbie_pull()

    # Run
    for _ in range(pulls):
        sim.execute_single_roll()
        
    # Report
    s = sim.stats
    print("\n=== SIMULATION REPORT ===")
    print(f"Total Pulls: {pulls}")
    print(f"Total 5-Stars: {s['total_5star']} ({s['total_5star']/pulls*100:.3f}%)")
    print(f"Total 4-Stars: {s['total_4star']} ({s['total_4star']/pulls*100:.3f}%)")
    
    # 5-Star Details
    print("\n--- 5-Star Details ---")
    print(f"UP (Kokomi): {s['up_5star']} ({s['up_5star']/s['total_5star']*100 if s['total_5star'] else 0:.1f}%)")
    print(f"Standard:    {s['std_5star']} ({s['std_5star']/s['total_5star']*100 if s['total_5star'] else 0:.1f}%)")
    print(f"Max Pity Reached: {s['max_pity_5star']}")
    if s['pity_history_5star']:
        avg_pity = sum(s['pity_history_5star']) / len(s['pity_history_5star'])
        print(f"Avg Pity: {avg_pity:.2f}")
        
    # Standard Distribution
    print("\n--- Standard Character Distribution (The Bug Check) ---")
    stds = {k:v for k,v in s['distribution'].items() if "UP" not in k}
    total_std_pulls = sum(stds.values())
    
    print(f"{'Character':<15} | {'Count':<8} | {'% of Std':<10}")
    print("-" * 40)
    for char, count in sorted(stds.items(), key=lambda x: x[1], reverse=True):
        p = (count / total_std_pulls * 100) if total_std_pulls else 0
        print(f"{char:<15} | {count:<8} | {p:.2f}%")
        
    # Bias Check
    if "Fischl" in stds:
        fischl = stds["Fischl"]
        others = [v for k,v in stds.items() if k != "Fischl"]
        if others:
            avg_others = sum(others) / len(others)
            ratio = fischl / avg_others
            print(f"\nBias Factor (Fischl / Avg Others): {ratio:.2f}x")

if __name__ == "__main__":
    check_determinism()
    check_newbie_distribution()
    # run_test()
