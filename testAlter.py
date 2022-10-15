from matplotlib import pyplot as plt

import alterobj


# Test on AlternativeObject
import cor
import data

data.load_rpe("resources/56769032/56769032.json")

obj = cor.judge_line_list[0].note_y_object

_, axes = plt.subplots(2, 2)

x = [i/10 for i in range(2000)]
y = [obj.get_value(i/10, 200) for i in range(2000)]

axes[0][0].plot(x, y)
plt.show()
