import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

time = [0.1, 0.5, 1, 5]

plt.rcParams.update({'font.size': 23})

random3x3empty = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 100, 100, 100],
    'Draw': [0, 0, 0, 0],
    'Loss': [50, 0, 0, 0]
})

greedy3x3empty = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 70, 80],
    'Loss': [50, 10, 30, 20]
})

random3x3hard = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 90, 100],
    'Draw': [0, 0, 0, 0],
    'Loss': [50, 10, 10, 0]
})

greedy3x3hard = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'win': [50, 70, 100, 90],
    'draw': [0, 0, 0, 0],
    'loss': [50, 30, 0, 10]
})

fig, ax1 = plt.subplots(figsize=(10, 10))
tidy = greedy3x3empty.melt(id_vars='Time').rename(columns=str.title)
print(tidy)

sns.barplot(x='Time', y='Value', hue='Variable',
            #'#F6F7EB',
            data=tidy, ax=ax1, palette=['#44BBA4', '#ED1C24'])
sns.despine(fig)
plt.xlabel('Time')
plt.ylabel('Percentage')
plt.title('Win percentages on 3x3empty.txt vs. Greedy player')
plt.savefig('3x3empty_greedy.png')
plt.show()





