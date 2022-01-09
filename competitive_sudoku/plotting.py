import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

time = [0.1, 0.5, 1, 5]

plt.rcParams.update({'font.size': 15})

greedy3x3empty = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 100, 100],
    'Board': '3x3 empty',
    'Versus': 'Greedy player'
})  # done

greedy3x3random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 100, 100, 100],
    'Board': '3x3 random',
    'Versus': 'Greedy player'
})  # done


greedy3x3hard = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 100, 100, 100],
    'Board': '3x3 hard',
    'Versus': 'Greedy player'
})

greedy2x2easy = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 70, 100, 90],
    'Board': '2x2 easy',
    'Versus': 'Greedy player'
})

greedy3x3easy = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 100, 100],
    'Board': '3x3 easy',
    'Versus': 'Greedy player'
})

greedy2x3random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 70, 90, 90],
    'Board': '2x3 random',
    'Versus': 'Greedy player'
})

greedy3x4random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 100, 100],
    'Board': '3x4 random',
    'Versus': 'Greedy player'
})

greedy4x4random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 100, 100, 100],
    'Board': '4x4 random',
    'Versus': 'Greedy player'
})

a1_3x3empty = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 80, 65, 70],
    'Board': '3x3 empty',
    'Versus': 'A1'
})  # done

a1_3x3random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 100, 100],
    'Board': '3x3 random',
    'Versus': 'A1'
})  # done


a1_3x3hard = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 80, 100, 100],
    'Board': '3x3 hard',
    'Versus': 'A1'
})  # done

a1_2x2easy = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 100, 100, 100],
    'Board': '2x2 easy',
    'Versus': 'A1'
})  # done

a1_3x3easy = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 90, 100, 100],
    'Board': '3x3 easy',
    'Versus': 'A1'
})  # done

a1_2x3random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 60, 60, 70],
    'Board': '2x3 random',
    'Versus': 'A1'
})  # done

a1_3x4random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 70, 100, 100],
    'Board': '3x4 random',
    'Versus': 'A1'
})  # done

a1_4x4random = pd.DataFrame({
    'Time': [0.1, 0.5, 1, 5],
    'Win': [50, 70, 90, 100],
    'Board': '4x4 random',
    'Versus': 'A1'
})  #

df = pd.concat([greedy2x2easy, greedy2x3random, greedy3x3easy, greedy3x3empty, greedy3x3random, greedy3x3hard,
                greedy3x4random, greedy4x4random, a1_2x2easy, a1_2x3random, a1_3x3easy, a1_3x3empty, a1_3x3random,
                a1_3x3hard, a1_3x4random, a1_4x4random], ignore_index=True)
print(df)
# print(a1)
# fig, ax1 = plt.subplots(figsize=(10, 10))
# tidy = a1_4x4random.melt(id_vars='Time').rename(columns=str.title)
# print(tidy)


sns.factorplot(x='Time', y='Win', hue='Board', col='Versus', kind='bar', saturation=1, palette='muted',
               data=df)
# sns.barplot(x='Time', y='Value', hue='Variable',
            #'#F6F7EB',
#             data=tidy, ax=ax1, palette=['#44BBA4', '#ED1C24'])
# sns.despine(fig)
plt.ylim(0, 100)
plt.xlabel('Time')
plt.ylabel('Percentage')
# plt.title('Win percentages vs. our A1 agent')
plt.savefig('vs_a1.png')
plt.show()








