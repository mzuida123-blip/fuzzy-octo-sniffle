#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
import random
import argparse
import numpy as np

ROOT = os.path.dirname(__file__)
PACKAGE_PATH = os.path.join(ROOT, "omni_brain_simulator")
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)

from core.engine import WYTransformerEngine, TopologicalWire, WYResistorMesh
from core.visualizer import OmniVisualizer
from control.regime import RegimeController
from control.totalitarian import TotalitarianController


def normalize_matrix(mat: list) -> np.ndarray:
    arr = np.array(mat)
    mi, ma = arr.min(), arr.max()
    if ma - mi == 0:
        return np.zeros_like(arr)
    return (arr - mi) / (ma - mi)


def run_system(iterations: int = 100, viz_headless: bool = False, save_dir: str | None = None) -> None:
    wire = TopologicalWire(jump_points_count=8, seed=42)
    mesh = WYResistorMesh(seed=42)
    viz = OmniVisualizer(headless=viz_headless, save_dir=save_dir)
    controller = RegimeController(mesh, wire, target_resistance=25.0, tolerance=4.0)

    print("🚀 超脑系统启动：W-Y 维度对冲开启...")

    try:
        for i in range(iterations):
            strength = random.uniform(0.1, 2.5)
            mesh.apply_impulse([strength] * mesh.grid_size)
            gov = controller.governance_step()
            w = normalize_matrix(mesh.snapshot())
            y = np.flipud(w) * (1.0 + np.random.normal(0, 0.02, w.shape))
            viz.update(w, y)
            if i % 10 == 0:
                print(f"Iter {i}: avg_res={gov['avg_resistance']:.4f}, resonance={gov['resonance_frequency']:.4f}, action={gov['action']}")
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n⚠️ 系统紧急断开连接。")
    finally:
        out = os.path.join(ROOT, "final_snapshot.png")
        try:
            viz.save_snapshot(out)
            print(f"Saved final snapshot to {out}")
        except Exception:
            pass


def run_system_with_regime(iterations: int = 200, viz_headless: bool = False, save_dir: str | None = None):
    engine = WYTransformerEngine(size=64)
    viz = OmniVisualizer(headless=viz_headless, save_dir=save_dir)
    total_ctrl = TotalitarianController(entropy_threshold=1.2)

    print("🚀 超脑系统已进入[集权统治模式]...")

    for i in range(iterations):
        engine.inject_w_signal(np.random.randint(0, 64), np.random.randint(0, 64), 2.0)
        engine.compute_mobius_resonance()
        w, y = engine.forward_propagate()
        y_governed = total_ctrl.check_and_govern(y)
        viz.update(w, y_governed)
        if i % 10 == 0:
            print(f"Iter {i}: resonance={engine.resonance_frequency:.4f}, regime_active={total_ctrl.regime_active}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Omni Brain Simulator runner')
    parser.add_argument('--mode', choices=['system', 'regime'], default='system', help='Which demo mode to run')
    parser.add_argument('--iterations', type=int, default=100, help='Number of iterations')
    parser.add_argument('--save', action='store_true', help='Run headless and save frames instead of interactive display')
    parser.add_argument('--save-dir', type=str, default=None, help='Directory to save frames when running headless')
    args = parser.parse_args()

    viz_headless = args.save
    save_dir = args.save_dir

    if args.mode == 'system':
        run_system(iterations=args.iterations, viz_headless=viz_headless, save_dir=save_dir)
    else:
        run_system_with_regime(iterations=200, viz_headless=viz_headless, save_dir=save_dir)
