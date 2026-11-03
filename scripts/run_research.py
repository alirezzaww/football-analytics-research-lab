"""Run the tournament research in dependency order on Windows, macOS or Linux."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGES = [
    "11_tournament_passes_per_game.py",
    "13_minutes_and_shot_quality.py",
    "14_threshold_sensitivity.py",
    "15_kirby_passing_profile.py",
    "16_match_variation.py",
    "17_passing_volume_adjustment.py",
    "18_first_xg_model.py",
    "19_time_window_sensitivity.py",
    "20_pass_location_context.py",
    "21_match_bootstrap_uncertainty.py",
    "22_score_state_context.py",
    "23_within_match_score_comparison.py",
    "24_passes_shots_and_possessions.py",
    "25_shot_angle_model.py",
    "26_probability_calibration.py",
    "28_training_distance_support.py",
    "29_match_xg_summary.py",
    "30_cumulative_xg_timeline.py",
    "31_shot_location_maps.py",
    "32_shot_volume_quality.py",
    "33_shot_body_part_context.py",
    "34_header_assisting_passes.py",
    "35_corner_delivery_rates.py",
    "36_corner_phase_analysis.py",
    "37_corner_window_sensitivity.py",
    "38_france_tournament_corners.py",
    "39_corner_delivery_profiles.py",
    "scripts/check_evidence.py",
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true", help="Save plots without opening windows")
    parser.add_argument("--extended-evaluation", action="store_true",
                        help="Also rerun the frozen-model check on 45 other fixtures (downloads once)")
    args = parser.parse_args()
    env = os.environ.copy()
    if args.headless:
        env["MPLBACKEND"] = "Agg"
    stages = list(STAGES)
    if args.extended_evaluation:
        stages.insert(stages.index("28_training_distance_support.py"), "27_frozen_model_evaluation.py")
    for stage in stages:
        print(f"Running {stage}", flush=True)
        subprocess.run([sys.executable, str(ROOT / stage)], cwd=ROOT, env=env, check=True)
    print("Research pipeline and evidence checks completed.")

if __name__ == "__main__":
    main()
