import pandas as pd
import os
import matplotlib.pyplot as plt

path = os.getcwd() + '\\data\\'
path = 'C:\\Users\\Matias.MSI\\PycharmProjects\\backtesting\\'

file = 'resultsEqty.csv'
df3 = pd.read_csv(path+file)
df3 = df3.loc[df3.Result != 0]


n_bins = 500

fig, axs = plt.subplots(nrows=3, ncols=1)

axs[0].hist(df3['Result'], bins=n_bins)
axs[0].set_title('Results by trade')

axs[1].hist(df3['Result'], bins=n_bins, range=(-5, 50))
axs[1].set_title('Results by trade')

axs[2].hist(df3['Result'], bins=n_bins, range=(-7, 7))
axs[2].set_title('Results by trade')

plt.show()
