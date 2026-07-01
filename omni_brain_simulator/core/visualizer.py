import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

class OmniVisualizer:
    """
    超脑视觉测绘器：将抽象的 W-Y 维间数据转化为全息可视化影像

    参数:
    - headless: 如果为 True，使用 Agg 后端并保存帧到文件而不是打开交互窗口
    - save_dir: 当 headless 时，保存帧的目录
    """
    def __init__(self, headless: bool = False, save_dir: Optional[str] = None):
        self.headless = bool(headless)
        self.save_dir = save_dir
        if self.headless:
            matplotlib.use('Agg')
        else:
            plt.ion()
        self.fig, (self.ax_w, self.ax_y) = plt.subplots(1, 2, figsize=(12, 5))
        self.fig.patch.set_facecolor('#0f0f0f')
        self.frame_idx = 0

    def update(self, space_w: np.ndarray, space_y: np.ndarray):
        self.ax_w.clear()
        self.ax_y.clear()

        self.ax_w.imshow(space_w, cmap='magma', origin='lower')
        self.ax_w.set_title("W-Domain (Reality Flow)", color='white')
        self.ax_w.axis('off')

        self.ax_y.imshow(space_y, cmap='Blues_r', origin='lower')
        self.ax_y.set_title("Y-Domain (Mirror Projection)", color='cyan')
        self.ax_y.axis('off')

        plt.tight_layout()

        if self.headless:
            if self.save_dir:
                import os
                os.makedirs(self.save_dir, exist_ok=True)
                path = os.path.join(self.save_dir, f"frame_{self.frame_idx:04d}.png")
                self.fig.savefig(path, dpi=150)
            self.frame_idx += 1
        else:
            plt.pause(0.05)

    def save_snapshot(self, path: str):
        self.fig.savefig(path)
