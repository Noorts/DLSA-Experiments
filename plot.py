import matplotlib.pyplot as plt
n = [1,2,4,8]
s = [43/43, 43/23, 43/13, 43/8]


plt.scatter(n, s, label="Speedup")
plt.plot(n, n, label="Optimal speedup", color="red")
plt.xlabel("Number of workers")
plt.ylabel("Speedup")
plt.legend()
plt.show()
