import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path


class Visualize:

    @staticmethod
    def print_mean(df):
        print(df.groupby('type')['mean'].mean())
        print(df.groupby('type')['std'].mean())

    @staticmethod
    def plot(df, title):
        plt.figure(title)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')['mean'].plot(legend=True, title=title)
        plt.xticks(rotation='vertical')
        plt.draw()

    @staticmethod
    def violin_plot(df, output_folder):
        columns = list(df.columns)[2:8]
        fig, axs = plt.subplots(ncols=len(columns))
        for i, column in enumerate(columns):
            sns.violinplot(data=df, x=column, y="rec_type", inner="quart", split=True, ax=axs[i])
        plt.show(block=True)
        fig.savefig(Path(output_folder+'metrics.png'))

        columns = list(df.columns)[7:]
        fig, axs = plt.subplots(ncols=len(columns))
        for i, column in enumerate(columns):
            sns.violinplot(data=df, x=column, y="rec_type", inner="quart", split=True, ax=axs[i])
        plt.show(block=True)
        fig.savefig(Path(output_folder+'alternative_voices.png'))
