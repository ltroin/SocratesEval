import numpy as np
import matplotlib.pyplot as plt
from pivot import pivot

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 12


data = pivot.values.T
row_labels = pivot.columns.tolist()   # Evaluator
col_labels = pivot.index.tolist()     # MODEL

avg_row = np.nanmean(data, axis=0, keepdims=True)
data_with_avg = np.vstack([avg_row, data])
row_labels_with_avg = ['Avg.'] + row_labels

fig, ax = plt.subplots(figsize=(12,3))
im = ax.imshow(
    data_with_avg, aspect='auto', cmap='gray',
    vmin=np.nanmin(data_with_avg), vmax=np.nanmax(data_with_avg)
)
cbar = fig.colorbar(im, ax=ax, orientation='vertical')

ax.set_xticks(np.arange(len(col_labels)))
ax.set_xticklabels(col_labels, rotation=20, ha='right')
ax.set_yticks(np.arange(len(row_labels_with_avg)))
ax.set_yticklabels(row_labels_with_avg, rotation=20, ha='right')

thresh = (np.nanmax(data_with_avg) + np.nanmin(data_with_avg)) / 2
for i in range(data_with_avg.shape[0]):
    for j in range(data_with_avg.shape[1]):
        val = data_with_avg[i, j]
        color = 'black' if val > thresh else 'white'
        ax.text(j, i, f"{val:.1f}", ha='center', va='center', color=color)

plt.tight_layout(pad=0.1)

fig.savefig(
    'heatmap.pdf',
    format='pdf',
    dpi=500,
    bbox_inches='tight',
    pad_inches=0
)

plt.show()
