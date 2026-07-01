"""Core engine for omni_brain_simulator

Contains WYResistorMesh, TopologicalWire and WYTransformerEngine used by
visualizer and control loops.
"""
from __future__ import annotations

import math
import random
from typing import List, Tuple


class TopologicalWire:
    """双层嵌套拓扑线缆。

    - outer_layer: 外层用于二次导向/耦合
    - inner_layer: 内层用于原始输入/输出
    - terminal_junction: 端点名称

    可选 seed 用于可复现性测试。
    """

    def __init__(self, jump_points_count: int = 8, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
        self.points_count = int(jump_points_count)
        self.outer_layer = [f"Outer_Node_Jump_{i+1}" for i in range(self.points_count)]
        self.inner_layer = [f"Inner_Node_Flow_{i+1}" for i in range(self.points_count)]
        self.terminal_junction = "TERMINAL_JUNCTION_PAD"

    def get_resonance_gap(self) -> float:
        """返回 0..1 之间的共振匹配度（越接近 1 同频匹配越好）。"""
        return round(random.uniform(0.80, 0.99), 4)


class WYResistorMesh:
    """W-Y 芯片：4x4 非线性电阻网格模拟器（低分辨率）。"""

    def __init__(self, grid_size: int = 4, init_range: Tuple[float, float] = (10.0, 50.0), seed: int | None = None):
        if seed is not None:
            random.seed(seed)
        self.grid_size = int(grid_size)
        self.init_range = init_range
        self.matrix: List[List[float]] = [
            [random.uniform(*init_range) for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]

    def average_resistance(self) -> float:
        total = sum(sum(row) for row in self.matrix)
        return total / (self.grid_size * self.grid_size)

    def apply_impulse(self, voltage_vector: List[float], collapse_rate: float = 0.05) -> float:
        for i in range(self.grid_size):
            v = voltage_vector[i] if i < len(voltage_vector) else (voltage_vector[-1] if voltage_vector else 1.0)
            row_avg = sum(self.matrix[i]) / self.grid_size
            nonlinear = 1.0 + math.tanh((row_avg - sum(self.init_range) / 2.0) / 25.0)
            for j in range(self.grid_size):
                factor = v * collapse_rate * nonlinear
                self.matrix[i][j] = max(0.1, self.matrix[i][j] * (1.0 - factor))
        return round(self.average_resistance(), 4)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            random.seed(seed)
        self.matrix = [
            [random.uniform(*self.init_range) for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]

    def snapshot(self) -> List[List[float]]:
        return [row.copy() for row in self.matrix]


# WYTransformerEngine: higher-resolution transformer for visualization
import numpy as np
from typing import Tuple

class WYTransformerEngine:
    def __init__(self, size: int = 64, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.size = int(size)
        self.internal_state = np.random.uniform(5.0, 50.0, size=(self.size, self.size))
        self.resonance_frequency = 0.0

    def inject_w_signal(self, x: int, y: int, val: float = 1.0) -> None:
        xi = max(0, min(self.size - 1, int(x)))
        yi = max(0, min(self.size - 1, int(y)))
        self.internal_state[xi, yi] += float(val)

    def compute_mobius_resonance(self) -> None:
        avg = float(np.mean(self.internal_state))
        self.resonance_frequency = max(0.0, 100.0 / (1.0 + avg))

    def forward_propagate(self) -> Tuple[np.ndarray, np.ndarray]:
        w = np.copy(self.internal_state)
        w_min, w_max = w.min(), w.max()
        if w_max - w_min == 0:
            w_norm = np.zeros_like(w)
        else:
            w_norm = (w - w_min) / (w_max - w_min)
        y = np.flipud(w_norm) * (1.0 + np.random.normal(0, 0.02, w_norm.shape))
        return w_norm, y

    def demo_transformer(self, seed: int | None = None) -> None:
        print("WYTransformerEngine demo: avg", float(np.mean(self.internal_state)))
