import numpy as np
from numpy.lib.twodim_base import tri
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
# sns.set_theme(style="ticks", palette="Set2")
files=["saved_ordered_ins", "saved_ordered2"]
max_length = 65
for j in files:
    all_depths = []
    # max_length = 0
    d = np.empty((2, 81))
    d[:] = np.nan
    data = pd.DataFrame(data=d,columns=np.arange(1, 82))

    for i in [3]:
        lines = np.array([list(map(int, line.split(","))) for line in open(f'./{j}_3x3e.txt') if line !="\n"])
        lines = [[l[0], l[-1]] for l in lines]

        empty_depths = {}

        for empty, depth in lines:
            empty_depths[empty] = depth

        emptys = list(empty_depths.keys())
        depths = list(empty_depths.values())

        data.loc[i, emptys] = depths

    
    data = data.iloc[:, ::-1]
    data.columns = pd.CategoricalIndex(data.columns, name="turn")
    data.columns = [f"a-{int(column)}" for column in data.columns]

    data["id"] = data.index

    data_new = pd.wide_to_long(data,stubnames="a-", i="id", j="turn").reindex()

    data_new.columns = ["depth"]

    # sns.lineplot(data=data.T)
    sns.lineplot(data=data_new, x="turn", y="depth", label=j, marker= "o", dashes=False, alpha=.7)

xlabels = [str(i) for i in np.arange(0, 90, 10)]
# x
# print(data_new)
# plt.xticks(np.flip(np.arange(0, 90, 10)))
plt.xlim(85, -1)# plt.yscale('symlog', subsy=[2, 3, 4, 5, 6, 7, 8, 9])

# plt.xlim(0, 68)
# plt.ylim(bottom=0)
plt.grid(True, which="both")
plt.xlabel("empty squares left")
plt.legend([f"version: {time}"for time in files])
plt.ylim(-.5)
plt.show()

# # print(data)