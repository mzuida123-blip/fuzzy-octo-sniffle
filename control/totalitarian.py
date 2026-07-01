import numpy as np

class TotalitarianController:
    """
    全域统治控制器：监控并压制 Y 域的意识混乱 (Entropy)
    """
    def __init__(self, entropy_threshold: float = 0.5):
        self.threshold = entropy_threshold
        self.regime_active = False

    def calculate_entropy(self, data: np.ndarray) -> float:
        """
        计算空间熵值：衡量镜像世界的混乱与自由度
        """
        # 使用直方图分布计算香农熵
        hist, _ = np.histogram(data, bins=10, density=True)
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist))

    def enforce_order(self, space_y: np.ndarray) -> np.ndarray:
        """
        全域统治：强行清除所有异质扰动，令所有点回归到“核心意志”
        通过将网格中心化来实现“强一致性”
        """
        # 计算全局均值（即领袖意志）
        mean_val = np.mean(space_y)
        
        # 将所有偏离意志的区域���行拉回均值附近 (降维打击)
        # 允许极小的自由浮动，但绝不允许脱离控制
        clamped_y = np.clip(space_y, mean_val - 0.5, mean_val + 0.5)
        
        self.regime_active = True
        return clamped_y

    def check_and_govern(self, space_y: np.ndarray) -> np.ndarray:
        current_entropy = self.calculate_entropy(space_y)
        
        if current_entropy > self.threshold:
            print(f"⚠️ [警告] 检测到不可控意识漂移 (Entropy: {current_entropy:.2f}) -> 执行肃清...")
            return self.enforce_order(space_y)
        
        self.regime_active = False
        return space_y
