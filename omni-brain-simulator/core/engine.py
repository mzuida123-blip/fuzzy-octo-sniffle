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
        # 使用一个稳定的伪随机分布以便测试可重复
        return round(random.uniform(0.80, 0.99), 4)


class WYResistorMesh:
    """W-Y 芯片：4x4 非线性电阻网格模拟器。

    特点：
    - 每个格点包含一个阻抗值（欧姆标度），随输入脉冲发生微分变化
    - 支持多步脉冲应用、复位与统计输出
    """

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
        """将电压脉冲应用到网格的行向通道。

        - voltage_vector: 以行索引为主的脉冲强度列表（若短于行数将重复或以最后一项代替）
        - collapse_rate: 阻抗随单位脉冲坍缩比例基准

        返回网格的平均阻抗值作为特征��。
        """
        for i in range(self.grid_size):
            v = voltage_vector[i] if i < len(voltage_vector) else (voltage_vector[-1] if voltage_vector else 1.0)
            # 非线性因子：与行平均当前阻抗有关（高阻抗时更容易崩坍）
            row_avg = sum(self.matrix[i]) / self.grid_size
            nonlinear = 1.0 + math.tanh((row_avg - sum(self.init_range) / 2.0) / 25.0)
            for j in range(self.grid_size):
                factor = v * collapse_rate * nonlinear
                # 限制最小阻抗阈值，防止数值下溢
                self.matrix[i][j] = max(0.1, self.matrix[i][j] * (1.0 - factor))
        return round(self.average_resistance(), 4)

    def reset(self, seed: int | None = None) -> None:
        """重置网格到随机初始状态（可传 seed 以复现）。"""
        if seed is not None:
            random.seed(seed)
        self.matrix = [
            [random.uniform(*self.init_range) for _ in range(self.grid_size)]
            for _ in range(self.grid_size)
        ]

    def snapshot(self) -> List[List[float]]:
        """返回阻抗矩阵的深拷贝视图（方便测试/可视化）。"""
        return [row.copy() for row in self.matrix]


# ------------------------------------------------------------------
# WYTransformerEngine: a lightweight transform engine intended to work
# with higher-resolution W/Y domains (numpy arrays) for visualization
# ------------------------------------------------------------------
import numpy as np

class WYTransformerEngine:
    """A simple transformer engine that exposes an API used by the
    visualization and control loops in the demo.

    - size: width/height of the square W/Y domains (e.g. 64)
    - internal_state: numpy array representing the W-domain impedances
    - resonance_frequency: heuristic scalar updated by compute_mobius_resonance
    """

    def __init__(self, size: int = 64, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.size = int(size)
        # initialize W-domain as random impedance-like values
        self.internal_state = np.random.uniform(5.0, 50.0, size=(self.size, self.size))
        self.resonance_frequency = 0.0

    def inject_w_signal(self, x: int, y: int, val: float = 1.0) -> None:
        """Inject a point signal into the W-domain with bounds checks."""
        xi = max(0, min(self.size - 1, int(x)))
        yi = max(0, min(self.size - 1, int(y)))
        self.internal_state[xi, yi] += float(val)

    def compute_mobius_resonance(self) -> None:
        """Update resonance_frequency as an inverse function of average impedance."""
        avg = float(np.mean(self.internal_state))
        # heuristic: lower impedance => higher frequency
        self.resonance_frequency = max(0.0, 100.0 / (1.0 + avg))

    def forward_propagate(self) -> Tuple[np.ndarray, np.ndarray]:
        """Produce W and Y numpy arrays for visualization.

        - W is a normalized version of the internal_state
        - Y is a mirrored/transformed projection with phase-like modulation
        """
        w = np.copy(self.internal_state)
        # normalize to 0..1 for visualization
        w_min, w_max = w.min(), w.max()
        if w_max - w_min == 0:
            w_norm = np.zeros_like(w)
        else:
            w_norm = (w - w_min) / (w_max - w_min)

        # create Y as a flipped and slightly phase-shifted version
        y = np.flipud(w_norm) * (1.0 + np.random.normal(0, 0.02, w_norm.shape))
        return w_norm, y


# simple demo using the transformer engine
def demo_transformer(seed: int | None = None) -> None:
    eng = WYTransformerEngine(size=16, seed=seed)
    print("WYTransformerEngine demo: avg", float(np.mean(eng.internal_state)))
    eng.inject_w_signal(2, 3, 5.0)
    eng.compute_mobius_resonance()
    print("resonance_frequency", eng.resonance_frequency)
