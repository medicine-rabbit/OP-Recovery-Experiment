
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

# Load your data here
data = {
    'date': ['2025-05-02', '2025-05-03'],
    'sfr_owl': [1.96, 7.58],
    'delta_hrv': [-14, -15]
}

df = pd.DataFrame(data)

# Calculate correlation coefficient
correlation, p_value = pearsonr(df['sfr_owl'], df['delta_hrv'])

# Plot
plt.figure(figsize=(8, 6))
plt.scatter(df['sfr_owl'], df['delta_hrv'], color='blue', label='Sessions')
plt.plot(np.unique(df['sfr_owl']),
         np.poly1d(np.polyfit(df['sfr_owl'], df['delta_hrv'], 1))(np.unique(df['sfr_owl'])),
         color='orange', linestyle='--', label='Trend Line')
plt.title('SFR[OWL] vs ΔHRV (post - pre)')
plt.xlabel('SFR[OWL]')
plt.ylabel('ΔHRV (ms)')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f"Correlation: {correlation:.3f}, p-value: {p_value:.3f}")
