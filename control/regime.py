from __future__ import annotations

from typing import Any, Dict

# Lightweight governance / regime controller for the WY mesh
class RegimeController:
    """RegimeController 对 WYResistorMesh 提供统治与纠偏策略。

    目标：维持网格在一个可控的平均阻抗区间，通过注入脉冲或局部重置来修正偏差。
    """

    def __init__(self, mesh: Any, wire: Any, target_resistance: float = 25.0, tolerance: float = 5.0):
        self.mesh = mesh
        self.wire = wire
        self.target = float(target_resistance)
        self.tolerance = float(tolerance)
        self.resonance_frequency = 0.0

    def assess(self) -> Dict[str, float]:
        avg = self.mesh.average_resistance()
        delta = avg - self.target
        return {"avg": avg, "delta": delta}

    def governance_step(self) -> Dict[str, Any]:
        """评估网格状态并在必要时应用纠偏动作，返回本次治理动作摘要。"""
        s = self.assess()
        avg = s["avg"]
        delta = s["delta"]

        action = "stable"
        new_avg = avg

        # 若偏差超过容忍度，则应用纠偏
        if abs(delta) > self.tolerance:
            if delta > 0:
                # 阻抗偏高：施加强脉冲以促成更多坍缩
                pulse = min(3.0, 1.0 + delta / 10.0)
                vec = [pulse] * self.mesh.grid_size
                new_avg = self.mesh.apply_impulse(vec, collapse_rate=0.02)
                action = f"applied_strong_pulse_{pulse:.2f}"
            else:
                # 阻抗偏低：温和注入以防止过度坍塌，或做局部重置
                pulse = 0.3
                vec = [pulse] * self.mesh.grid_size
                new_avg = self.mesh.apply_impulse(vec, collapse_rate=0.005)
                action = f"applied_weak_pulse_{pulse:.2f}"

        # 计算一个启发式共振频率（阻抗越低，频率越高）
        self.resonance_frequency = max(0.0, 100.0 / (1.0 + new_avg))

        return {
            "avg_resistance": float(new_avg),
            "action": action,
            "resonance_frequency": float(self.resonance_frequency),
        }
