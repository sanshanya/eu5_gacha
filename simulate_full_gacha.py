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
    # 与游戏内 `gacha_execute_single_roll_silent` 的 LCG RNG 一致：
    # state = (state * 21 + 1) % 10000
    RNG_MODULO = 10000
    RNG_MULTIPLIER = 21
    RNG_INCREMENT = 1

    # 默认 UP 轮换角色（0-7）
    BASE_ROSTER = [
        "Xinhai",  # 0
        "Fischl",  # 1
        "Keqing",  # 2
        "Raiden",  # 3
        "Furina",  # 4
        "HuTao",  # 5
        "Klee",  # 6
        "Nahida",  # 7
    ]

    # 解锁“璃月池”后追加（0-8）
    LIYUE_EXTRA_ROSTER = [
        "Ningguang",  # 8
    ]

    @classmethod
    def build_roster(cls, liyue_unlocked):
        roster = list(cls.BASE_ROSTER)
        if liyue_unlocked:
            roster.extend(cls.LIYUE_EXTRA_ROSTER)
        return roster

    def __init__(self, debug=False, use_fix=True, rng=None, current_up_idx=0, liyue_unlocked=False):
        # --- Persistent State (Country scope) ---
        self.var_gacha_total_rolls_count = 0
        self.var_gacha_pity_5star_count = 0
        self.var_gacha_pity_4star_count = 0
        self.var_gacha_is_guaranteed_bool = 0
        self.var_gacha_block_pity_met_bool = 0

        self.var_gacha_std5_result_count = 0
        self.var_gacha_4star_result_count = 0

        # --- Global-like state used by this simulator instance ---
        self.roster = self.build_roster(liyue_unlocked)
        self.roster_size = len(self.roster)
        self.var_gacha_current_up_idx = current_up_idx % self.roster_size

        # --- Params ---
        self.debug = debug
        self.use_fix = use_fix
        self.rng = rng or random.Random()

        # RNG State：按游戏逻辑初始化
        if use_fix:
            self.var_gacha_entropy_gold_amt = self.rng.randrange(self.RNG_MODULO)
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
        if self.use_fix:
            return abs(self.var_gacha_entropy_gold_amt) % 10000
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
        if not self.use_fix:
            val += self.var_gacha_total_rolls_count * 13
        return (val * 31) % 10000

    def sv_gacha_calc_standard_5_idx(self):
        val = (self.var_gacha_std5_result_count * 17) + abs(self.var_gacha_entropy_gold_amt)
        # 与游戏内常驻池（不含UP）一致：0-(roster_size-2)
        return val % (self.roster_size - 1)

    # --- Effects (mirror `in_game/common/scripted_effects/gacha_logic_effects.txt`) ---

    def rotate_pool(self):
        old_up = self.roster[self.var_gacha_current_up_idx]
        self.var_gacha_current_up_idx = (self.var_gacha_current_up_idx + 1) % self.roster_size
        new_up = self.roster[self.var_gacha_current_up_idx]
        if self.debug:
            print(f"--- ROTATION: {old_up} -> {new_up} ---")

    def _step_rng_state(self):
        self.var_gacha_entropy_gold_amt = (
            (self.var_gacha_entropy_gold_amt * self.RNG_MULTIPLIER) + self.RNG_INCREMENT
        ) % self.RNG_MODULO

    def execute_single_roll(self):
        # Step 1: 状态步进
        self.var_gacha_total_rolls_count += 1
        if self.use_fix:
            self._step_rng_state()
        else:
            self.var_gacha_entropy_gold_amt -= 16

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
        if self.use_fix:
            self._step_rng_state()
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
            return self.roster[self.var_gacha_current_up_idx], True

        # 歪常驻（Sliding Window）
        self.stats["lose_up"] += 1
        self.var_gacha_std5_result_count += 1
        if self.use_fix:
            self._step_rng_state()

        raw_idx = self.sv_gacha_calc_standard_5_idx()  # 0-(roster_size-2)
        final_idx = raw_idx + 1 if raw_idx >= self.var_gacha_current_up_idx else raw_idx
        return self.roster[final_idx], False

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


def run_distribution_test(trials, pulls_per_trial, seed=None, use_fix=True, up_idx=0, liyue_unlocked=False):
    rng = random.Random(seed)
    roster = EU5GachaSimulation.build_roster(liyue_unlocked)
    counts_5 = []
    max_streak_5 = 0
    total_5 = 0
    total_up = 0
    trials_with_up = 0
    char_counts = Counter()

    for _ in range(trials):
        sim = EU5GachaSimulation(rng=rng, use_fix=use_fix, current_up_idx=up_idx, liyue_unlocked=liyue_unlocked)
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
        total_5 += sim.stats["total_5star"]
        total_up += sim.stats["win_up"]
        if sim.stats["win_up"] > 0:
            trials_with_up += 1
        char_counts.update(sim.stats["distribution"])

    counts_5_sorted = sorted(counts_5)
    counter = Counter(counts_5_sorted)

    print("=== 5★ DISTRIBUTION (per trial) ===")
    print(
        f"trials={trials} pulls_per_trial={pulls_per_trial} "
        f"use_fix={use_fix} seed={seed} roster_size={len(roster)} liyue_unlocked={liyue_unlocked}"
    )
    total_pulls = trials * pulls_per_trial
    up_rate_given_5 = (total_up / total_5) if total_5 else 0.0
    print(
        "rates: "
        f"5★/pull={total_5/total_pulls:.5f} "
        f"UP|5★={up_rate_given_5:.4f} "
        f"UP/pull={total_up/total_pulls:.5f}"
    )
    print(f"P(UP>=1 in {pulls_per_trial})={trials_with_up/trials:.4f}")
    print(
        "5★: "
        f"mean={sum(counts_5)/len(counts_5):.3f} "
        f"max={max(counts_5)} "
        f"p95={_nearest_rank_percentile(counts_5_sorted, 95)} "
        f"p99={_nearest_rank_percentile(counts_5_sorted, 99)} "
        f"max_consecutive_5★={max_streak_5}"
    )
    if total_5:
        featured = roster[up_idx % len(roster)]
        print(
            "expected 5★ chars/trial: "
            + ", ".join(
                f"{name}={char_counts.get(name, 0)/trials:.3f}"
                for name in roster
            )
        )
        print(f"featured={featured} expected_featured/trial={char_counts.get(featured, 0)/trials:.3f}")
    print("histogram(5★count -> trials):")
    for k in sorted(counter.keys()):
        print(f"  {k:>2} -> {counter[k]}")


def run_rotation_test(cycles, pulls_per_cycle, seed=None, use_fix=True, up_idx=0, liyue_unlocked=False):
    rng = random.Random(seed)
    sim = EU5GachaSimulation(rng=rng, use_fix=use_fix, current_up_idx=up_idx, liyue_unlocked=liyue_unlocked)

    print("=== ROTATION SIMULATION ===")
    print(
        f"cycles={cycles} pulls_per_cycle={pulls_per_cycle} "
        f"use_fix={use_fix} seed={seed} roster_size={sim.roster_size} liyue_unlocked={liyue_unlocked}"
    )

    last_dist = Counter()
    last_total_5 = 0

    for i in range(cycles):
        up_name = sim.roster[sim.var_gacha_current_up_idx]
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


def run_unique_test(countries, pulls_each, seed=None, use_fix=True, up_idx=0, liyue_unlocked=False):
    rng = random.Random(seed)
    sims = [
        EU5GachaSimulation(rng=rng, use_fix=use_fix, current_up_idx=up_idx, liyue_unlocked=liyue_unlocked)
        for _ in range(countries)
    ]

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
    print(
        f"countries={countries} pulls_each={pulls_each} use_fix={use_fix} seed={seed} "
        f"roster_size={sims[0].roster_size} liyue_unlocked={liyue_unlocked}"
    )
    print("owners(char -> country): " + ", ".join(f"{k}={v}" for k, v in sorted(owners.items())))
    for cid in range(countries):
        print(f"country[{cid}]: acquired={acquired[cid]} dup_own={dup_own[cid]} dup_other={dup_other[cid]}")


def run_stream_blocks_test(blocks, block_size, seed=None, use_fix=True, up_idx=0, liyue_unlocked=False):
    rng = random.Random(seed)
    sim = EU5GachaSimulation(rng=rng, use_fix=use_fix, current_up_idx=up_idx, liyue_unlocked=liyue_unlocked)

    counts_5 = []
    counts_up = []
    blocks_with_up = 0
    max_streak_5 = 0
    streak = 0

    for _ in range(blocks):
        c5 = 0
        c_up = 0
        for _ in range(block_size):
            tier, _, is_up = sim.execute_single_roll()
            if tier == 2:
                c5 += 1
                if is_up:
                    c_up += 1
                streak += 1
                max_streak_5 = max(max_streak_5, streak)
            else:
                streak = 0
        counts_5.append(c5)
        counts_up.append(c_up)
        if c_up > 0:
            blocks_with_up += 1

    counts_5_sorted = sorted(counts_5)
    counter = Counter(counts_5_sorted)

    print("=== 5★ STREAM (continuous blocks) ===")
    featured = sim.roster[up_idx % sim.roster_size]
    print(f"blocks={blocks} block_size={block_size} use_fix={use_fix} seed={seed} featured={featured}")
    total_pulls = blocks * block_size
    total_5 = sim.stats["total_5star"]
    total_up = sim.stats["win_up"]
    up_rate_given_5 = (total_up / total_5) if total_5 else 0.0
    print(
        "rates: "
        f"5★/pull={total_5/total_pulls:.5f} "
        f"UP|5★={up_rate_given_5:.4f} "
        f"UP/pull={total_up/total_pulls:.5f}"
    )
    print(f"P(UP>=1 in {block_size})={blocks_with_up/blocks:.4f}")
    print(
        "5★ per block: "
        f"mean={sum(counts_5)/len(counts_5):.3f} "
        f"min={min(counts_5)} "
        f"max={max(counts_5)} "
        f"p95={_nearest_rank_percentile(counts_5_sorted, 95)} "
        f"p99={_nearest_rank_percentile(counts_5_sorted, 99)} "
        f"max_consecutive_5★={max_streak_5}"
    )
    if total_5:
        print(
            "expected 5★ chars/block: "
            + ", ".join(
                f"{name}={sim.stats['distribution'].get(name, 0)/blocks:.3f}"
                for name in sim.roster
            )
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
    parser.add_argument("--up-idx", type=int, default=0, help="当前UP角色索引（默认 0；未解锁璃月池为 0-7，解锁后为 0-8）")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--no-fix", action="store_true", help="使用旧版确定性熵算法（用于对照）")
    parser.add_argument("--liyue-unlocked", action="store_true", help="模拟：璃月池已解锁（追加凝光，UP 轮换扩展到 0-8）")
    args = parser.parse_args()

    use_fix = not args.no_fix
    roster = EU5GachaSimulation.build_roster(args.liyue_unlocked)
    if args.up_idx < 0 or args.up_idx >= len(roster):
        parser.error(f"--up-idx must be in [0, {len(roster)-1}] for the current roster (liyue_unlocked={args.liyue_unlocked}).")

    if args.mode == "rotation":
        run_rotation_test(
            args.cycles,
            args.pulls_per_cycle,
            seed=args.seed,
            use_fix=use_fix,
            up_idx=args.up_idx,
            liyue_unlocked=args.liyue_unlocked,
        )
        return
    if args.mode == "unique":
        run_unique_test(
            args.countries,
            args.pulls_each,
            seed=args.seed,
            use_fix=use_fix,
            up_idx=args.up_idx,
            liyue_unlocked=args.liyue_unlocked,
        )
        return
    if args.mode == "stream":
        run_stream_blocks_test(
            args.blocks,
            args.block_size,
            seed=args.seed,
            use_fix=use_fix,
            up_idx=args.up_idx,
            liyue_unlocked=args.liyue_unlocked,
        )
        return
    run_distribution_test(
        args.trials,
        args.pulls,
        seed=args.seed,
        use_fix=use_fix,
        up_idx=args.up_idx,
        liyue_unlocked=args.liyue_unlocked,
    )


if __name__ == "__main__":
    main()
