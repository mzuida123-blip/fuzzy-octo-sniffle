"""omni-brain-simulator.core.engine

W-Y 跨维格点与非线性电阻网络引擎（本文件为本批次提交）
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

        - voltage_vector: 以行索引为主的脉冲强度列表（��短于行数将重复或以 1.0 代替）
        - collapse_rate: 阻抗随单位脉冲坍缩比例基准

        返回网格的平均阻抗值作为特征量。
        """
        for i in range(self.grid_size):
            v = voltage_vector[i] if i < len(voltage_vector) else voltage_vector[-1] if voltage_vector else 1.0
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


# 简单演示与自检
def demo_run(seed: int | None = None) -> None:
    print("-- omni-brain-simulator.core.engine demo --")
    wire = TopologicalWire(jump_points_count=8, seed=seed)
    mesh = WYResistorMesh(seed=seed)

    print(f"Terminal resonance gap: {wire.get_resonance_gap()}")
    print(f"Initial avg resistance: {mesh.average_resistance():.4f} ohm")

    pulses = [1.0, 2.0, 0.5, 1.5]
    for t, p in enumerate(pulses, start=1):
        avg = mesh.apply_impulse([p] * mesh.grid_size)
        print(f" After pulse {t} (strength {p}): avg_resistance={avg:.4f}")

    print("Snapshot:")
    for row in mesh.snapshot():
        print(" ", [round(x, 3) for x in row])


if __name__ == "__main__":
    demo_run(seed=42)
