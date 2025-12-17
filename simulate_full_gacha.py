import argparse
import math
import random
from collections import Counter


def _nearest_rank_percentile(sorted_values, percentile):
    if not sorted_values:
        return None
    n = len(sorted_values)
    k = max(0, math.ceil((percentile / 100.0) * n) - 1)
    return sorted_values[k]


class EU5GachaSimulation:
    # 与游戏内 `gacha_ensure_state_initialized` 的 7 个种子一致（负数用于打断确定性序列）
    ENTROPY_INIT_VALUES = [-1428, -2857, -4286, -5716, -7144, -8573, -9995]

    # 与游戏内 `gacha_execute_single_roll_silent` 的 per-roll random_list 扰动一致
    ENTROPY_PERTURB_VALUES = [0, 7, -7, 31, -31, 97, -97, 257, -257, 997, -997]
    ENTROPY_PERTURB_WEIGHTS = [10, 10, 10, 10, 10, 10, 10, 5, 5, 2, 2]

    # 0-7
    CHAR_MAP = [
        "Xinhai",  # 0
        "Fischl",  # 1
        "Keqing",  # 2
        "Raiden",  # 3
        "Furina",  # 4
        "HuTao",  # 5
        "Klee",  # 6
        "Nahida",  # 7
    ]

    def __init__(self, debug=False, use_fix=True, rng=None, current_up_idx=0):
        # --- Persistent State (Country scope) ---
        self.var_gacha_total_rolls_count = 0
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_is_guaranteed_bool = 0
        self.var_gacha_block_pity_met_bool = 0

        self.var_gacha_std5_result_count = 0
        self.var_gacha_4star_result_count = 0

        # --- Global-like state used by this simulator instance ---
        self.var_gacha_current_up_idx = current_up_idx

        # --- Params ---
        self.debug = debug
        self.use_fix = use_fix
        self.rng = rng or random.Random()

        # 熵资源：按游戏逻辑初始化
        if use_fix:
            self.var_gacha_entropy_gold_amt = self.rng.choice(self.ENTROPY_INIT_VALUES)
        else:
            self.var_gacha_entropy_gold_amt = 10000

        # --- Statistics ---
        self.stats = {
            "total_5star": 0,
            "total_4star": 0,
            "total_3star": 0,
            "win_up": 0,
            "lose_up": 0,
            "max_pity_5star": 0,
            "distribution": {},
        }

    # --- Script Values (mirror `in_game/common/script_values/gacha_eu_values.txt`) ---

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
        return min(val, 10001)

    def sv_gacha_calc_block_idx(self):
        return self.var_gacha_total_rolls_count % 10

    def sv_gacha_calc_entropy2(self):
        val = self.sv_gacha_calc_entropy()
        val += self.var_gacha_total_rolls_count * 13
        return (val * 31) % 10000

    def sv_gacha_calc_standard_5_idx(self):
        val = (self.var_gacha_std5_result_count * 17) + abs(self.var_gacha_entropy_gold_amt)
        return val % 7

    # --- Effects (mirror `in_game/common/scripted_effects/gacha_logic_effects.txt`) ---

    def rotate_pool(self):
        old_up = self.CHAR_MAP[self.var_gacha_current_up_idx]
        self.var_gacha_current_up_idx = (self.var_gacha_current_up_idx + 1) % 8
        new_up = self.CHAR_MAP[self.var_gacha_current_up_idx]
        if self.debug:
            print(f"--- ROTATION: {old_up} -> {new_up} ---")

    def _apply_entropy_perturbation(self):
        if not self.use_fix:
            return
        delta = self.rng.choices(self.ENTROPY_PERTURB_VALUES, weights=self.ENTROPY_PERTURB_WEIGHTS, k=1)[0]
        self.var_gacha_entropy_gold_amt += delta
        if self.var_gacha_entropy_gold_amt > 0:
            self.var_gacha_entropy_gold_amt *= -1

    def execute_single_roll(self):
        # Step 1: 状态步进
        self.var_gacha_total_rolls_count += 1
        self.var_gacha_entropy_gold_amt -= 16
        self._apply_entropy_perturbation()

        # Step 2: block 重置（block_idx == 1）
        block_idx = self.sv_gacha_calc_block_idx()
        if block_idx == 1:
            self.var_gacha_block_pity_met_bool = 0

        # Step 3: 星级判定
        entropy = self.sv_gacha_calc_entropy()
        prob_5 = self.sv_gacha_calc_5star_prob()
        prob_4 = self.sv_gacha_calc_4star_prob()

        tier_idx = 0
        if entropy < prob_5:
            tier_idx = 2
        elif entropy < prob_4 or (block_idx == 0 and self.var_gacha_block_pity_met_bool == 0):
            tier_idx = 1

        # Step 4: Resolve
        if tier_idx == 2:
            return self._resolve_5star()
        if tier_idx == 1:
            return self._resolve_4star()
        return self._resolve_3star()

    def execute_n_rolls(self, n):
        for _ in range(n):
            self.execute_single_roll()

    def _resolve_5star(self):
        self.stats["total_5star"] += 1
        self.stats["max_pity_5star"] = max(self.stats["max_pity_5star"], self.var_gacha_pity_5star_count)

        # 更新保底（与游戏一致）
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_block_pity_met_bool = 1
        self.var_gacha_pity_4star_count += 1

        char_name, is_up = self._resolve_5star_character()
        self.stats["distribution"][char_name] = self.stats["distribution"].get(char_name, 0) + 1
        return 2, char_name, is_up

    def _resolve_5star_character(self):
        entropy2 = self.sv_gacha_calc_entropy2()

        if self.var_gacha_is_guaranteed_bool == 1:
            is_up = True
            self.var_gacha_is_guaranteed_bool = 0
        else:
            if entropy2 < 5000:
                is_up = True
            else:
                is_up = False
                self.var_gacha_is_guaranteed_bool = 1

        if is_up:
            self.stats["win_up"] += 1
            return self.CHAR_MAP[self.var_gacha_current_up_idx], True

        # 歪常驻（Sliding Window）
        self.stats["lose_up"] += 1
        self.var_gacha_std5_result_count += 1

        raw_idx = self.sv_gacha_calc_standard_5_idx()  # 0-6
        final_idx = raw_idx + 1 if raw_idx >= self.var_gacha_current_up_idx else raw_idx
        return self.CHAR_MAP[final_idx], False

    def _resolve_4star(self):
        self.stats["total_4star"] += 1

        # 更新保底（与游戏一致）
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_block_pity_met_bool = 1
        self.var_gacha_pity_5star_count += 1
        self.var_gacha_4star_result_count += 1
        return 1, None, None

    def _resolve_3star(self):
        self.stats["total_3star"] += 1
        self.var_gacha_pity_5star_count += 1
        self.var_gacha_pity_4star_count += 1
        return 0, None, None


def run_distribution_test(trials, pulls_per_trial, seed=None, use_fix=True):
    rng = random.Random(seed)
    counts_5 = []
    max_streak_5 = 0

    for _ in range(trials):
        sim = EU5GachaSimulation(rng=rng, use_fix=use_fix)
        streak = 0
        best = 0
        for _ in range(pulls_per_trial):
            tier, _, _ = sim.execute_single_roll()
            if tier == 2:
                streak += 1
                best = max(best, streak)
            else:
                streak = 0
        max_streak_5 = max(max_streak_5, best)
        counts_5.append(sim.stats["total_5star"])

    counts_5_sorted = sorted(counts_5)
    counter = Counter(counts_5_sorted)

    print("=== 5★ DISTRIBUTION (per trial) ===")
    print(f"trials={trials} pulls_per_trial={pulls_per_trial} use_fix={use_fix} seed={seed}")
    print(
        "5★: "
        f"mean={sum(counts_5)/len(counts_5):.3f} "
        f"max={max(counts_5)} "
        f"p95={_nearest_rank_percentile(counts_5_sorted, 95)} "
        f"p99={_nearest_rank_percentile(counts_5_sorted, 99)} "
        f"max_consecutive_5★={max_streak_5}"
    )
    print("histogram(5★count -> trials):")
    for k in sorted(counter.keys()):
        print(f"  {k:>2} -> {counter[k]}")


def run_rotation_test(cycles, pulls_per_cycle, seed=None, use_fix=True):
    rng = random.Random(seed)
    sim = EU5GachaSimulation(rng=rng, use_fix=use_fix)

    print("=== ROTATION SIMULATION ===")
    print(f"cycles={cycles} pulls_per_cycle={pulls_per_cycle} use_fix={use_fix} seed={seed}")

    last_dist = Counter()
    last_total_5 = 0

    for i in range(cycles):
        up_name = sim.CHAR_MAP[sim.var_gacha_current_up_idx]
        for _ in range(pulls_per_cycle):
            sim.execute_single_roll()

        current_dist = Counter(sim.stats["distribution"])
        delta_dist = current_dist - last_dist
        delta_total_5 = sim.stats["total_5star"] - last_total_5

        print(f"\n--- CYCLE {i+1}: UP={up_name} ---")
        print(f"5★ this cycle: {delta_total_5}")
        if delta_total_5 > 0:
            top = delta_dist.most_common(3)
            print("top 5★ (this cycle): " + ", ".join(f"{name}={count}" for name, count in top))

        last_dist = current_dist
        last_total_5 = sim.stats["total_5star"]
        sim.rotate_pool()


def run_unique_test(countries, pulls_each, seed=None, use_fix=True):
    rng = random.Random(seed)
    sims = [EU5GachaSimulation(rng=rng, use_fix=use_fix) for _ in range(countries)]

    owners = {}  # char_name -> country_idx
    acquired = [0 for _ in range(countries)]
    dup_own = [0 for _ in range(countries)]
    dup_other = [0 for _ in range(countries)]

    for _ in range(pulls_each):
        for cid, sim in enumerate(sims):
            tier, char, _ = sim.execute_single_roll()
            if tier != 2:
                continue

            if char not in owners:
                owners[char] = cid
                acquired[cid] += 1
            elif owners[char] == cid:
                dup_own[cid] += 1
            else:
                dup_other[cid] += 1

    print("=== WORLD UNIQUE SANITY ===")
    print(f"countries={countries} pulls_each={pulls_each} use_fix={use_fix} seed={seed}")
    print("owners(char -> country): " + ", ".join(f"{k}={v}" for k, v in sorted(owners.items())))
    for cid in range(countries):
        print(f"country[{cid}]: acquired={acquired[cid]} dup_own={dup_own[cid]} dup_other={dup_other[cid]}")


def run_stream_blocks_test(blocks, block_size, seed=None, use_fix=True):
    rng = random.Random(seed)
    sim = EU5GachaSimulation(rng=rng, use_fix=use_fix)

    counts_5 = []
    max_streak_5 = 0
    streak = 0

    for _ in range(blocks):
        c5 = 0
        for _ in range(block_size):
            tier, _, _ = sim.execute_single_roll()
            if tier == 2:
                c5 += 1
                streak += 1
                max_streak_5 = max(max_streak_5, streak)
            else:
                streak = 0
        counts_5.append(c5)

    counts_5_sorted = sorted(counts_5)
    counter = Counter(counts_5_sorted)

    print("=== 5★ STREAM (continuous blocks) ===")
    print(f"blocks={blocks} block_size={block_size} use_fix={use_fix} seed={seed}")
    print(
        "5★ per block: "
        f"mean={sum(counts_5)/len(counts_5):.3f} "
        f"min={min(counts_5)} "
        f"max={max(counts_5)} "
        f"p95={_nearest_rank_percentile(counts_5_sorted, 95)} "
        f"p99={_nearest_rank_percentile(counts_5_sorted, 99)} "
        f"max_consecutive_5★={max_streak_5}"
    )
    print("histogram(5★count -> blocks):")
    for k in sorted(counter.keys()):
        print(f"  {k:>2} -> {counter[k]}")


def main():
    parser = argparse.ArgumentParser(description="EU5 gacha simulator (keeps in sync with in-game V3 logic).")
    parser.add_argument("--mode", choices=["distribution", "rotation", "unique", "stream"], default="distribution")
    parser.add_argument("--trials", type=int, default=5000, help="distribution 模式的试验次数")
    parser.add_argument("--pulls", type=int, default=100, help="distribution 模式每次试验的抽数")
    parser.add_argument("--cycles", type=int, default=8, help="rotation 模式的轮换次数")
    parser.add_argument("--pulls-per-cycle", type=int, default=50000, help="rotation 模式每轮抽数")
    parser.add_argument("--countries", type=int, default=2, help="unique 模式国家数量")
    parser.add_argument("--pulls-each", type=int, default=1000, help="unique 模式每国抽数")
    parser.add_argument("--blocks", type=int, default=2000, help="stream 模式的块数量")
    parser.add_argument("--block-size", type=int, default=100, help="stream 模式每块抽数")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-fix", action="store_true", help="关闭随机扰动/负值约束（用于对照旧逻辑）")
    args = parser.parse_args()

    use_fix = not args.no_fix

    if args.mode == "rotation":
        run_rotation_test(args.cycles, args.pulls_per_cycle, seed=args.seed, use_fix=use_fix)
        return
    if args.mode == "unique":
        run_unique_test(args.countries, args.pulls_each, seed=args.seed, use_fix=use_fix)
        return
    if args.mode == "stream":
        run_stream_blocks_test(args.blocks, args.block_size, seed=args.seed, use_fix=use_fix)
        return
    run_distribution_test(args.trials, args.pulls, seed=args.seed, use_fix=use_fix)


if __name__ == "__main__":
    main()
