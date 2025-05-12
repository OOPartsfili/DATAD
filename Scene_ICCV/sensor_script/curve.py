import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import viridis

# 生成时间数据
t = np.linspace(0, 10, 500)  # 从0到10秒，共500个点

# 生成y值数据，振幅随时间增大，频率也随时间增大
y = np.sin(t * (1 + 0.5 * t)) * (1 + t)  # 频率增加因子为0.5 * t

# 创建图像和颜色映射
fig, ax = plt.subplots(figsize=(10, 5))
cmap = viridis

# 归一化时间值到[0, 1]区间以映射颜色
norm = plt.Normalize(t.min(), t.max())

# 绘制每一小段
for i in range(len(t)-1):
    ax.plot(t[i:i+2], y[i:i+2], color=cmap(norm(t[i])))

# 添加颜色条
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, label='Time (s)')

# 设置图表标题和标签
ax.set_title('Trajectory')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Position')
plt.show()
