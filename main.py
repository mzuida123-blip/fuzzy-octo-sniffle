#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
import random
import numpy as np

# Ensure the internal package path (omni-brain-simulator) is importable as a plain module source root
ROOT = os.path.dirname(__file__)
PACKAGE_PATH = os.path.join(ROOT, "omni-brain-simulator")
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


def run_system(iterations: int = 100, interactive: bool = True) -> None:
    wire = TopologicalWire(jump_points_count=8, seed=42)
    mesh = WYResistorMesh(seed=42)
    viz = OmniVisualizer()
    controller = RegimeController(mesh, wire, target_resistance=25.0, tolerance=4.0)

    print("🚀 超脑系统启动：W-Y 维度对冲开启...")

    try:
        for i in range(iterations):
            # 注入随机环境波动作为干扰（行向脉冲）
            strength = random.uniform(0.1, 2.5)
            mesh.apply_impulse([strength] * mesh.grid_size)

            # 控制器评估并应用治理/纠偏
            gov = controller.governance_step()

            # 生成可视化矩阵
            w = normalize_matrix(mesh.snapshot())
            # Y 域为 W 的镜像 + 少量噪声，表示镜像反馈
            y = np.flipud(w) * (1.0 + np.random.normal(0, 0.02, w.shape))

            # 渲染
            viz.update(w, y)

            if i % 10 == 0:
                print(f"Iter {i}: avg_res={gov['avg_resistance']:.4f}, resonance={gov['resonance_frequency']:.4f}, action={gov['action']}")

            # 小睡以控制刷新率
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


# New: run_system_with_regime using WYTransformerEngine + TotalitarianController

def run_system_with_regime():
    # use transformer engine for higher-res domains
    engine = WYTransformerEngine(size=64)
    viz = OmniVisualizer()
    total_ctrl = TotalitarianController(entropy_threshold=1.2)

    print("🚀 超脑系统已进入[集权统治模式]...")

    for i in range(200):
        # 1. 注入
        engine.inject_w_signal(np.random.randint(0, 64), np.random.randint(0, 64), 2.0)

        # 2. 映射
        engine.compute_mobius_resonance()
        w, y = engine.forward_propagate()

        # 3. 统治逻辑 (核心步骤)
        y_governed = total_ctrl.check_and_govern(y)

        # 4. 渲染
        viz.update(w, y_governed)

    # note: call run_system_with_regime() explicitly to run

if __name__ == "__main__":
    run_system()
