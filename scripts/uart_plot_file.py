from multiprocessing import Process

import matplotlib.pyplot as plt


def plot(filename):
    x = []
    y = []
    with open(filename, "r") as f:
        for line in f:
            if not line.startswith("#"):
                split = line.split()
                if len(split) >= 2:
                    x.append(float(split[0]))
                    y.append(float(split[1]))
    print(f"Plotting file {filename}")
    plt.plot(x, y)
    plt.xlabel("Time (s)", fontsize=20)
    plt.ylabel("LVDS positive (V)", fontsize=20)
    plt.show()


if __name__ == "__main__":
    process0 = Process(target=plot, args=(r'/home/neo/Desktop/debug_dsail_ch0_20210929_1658.txt',))
    process1 = Process(target=plot, args=(r'/home/neo/Desktop/debug_dsail_ch1_20210929_1658.txt',))
    process0.start()
    process1.start()