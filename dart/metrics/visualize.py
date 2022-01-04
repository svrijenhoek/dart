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

    @staticmethod
    def boxplot(df):
        df.boxplot(column=list(df.columns)[2:8], by='rec_type', grid=False)
        df.boxplot(column=list(df.columns)[7:], by='rec_type', grid=False)
        # df['alternative_voices'] = df['alternative_voices'].where(df['alternative_voices'] <= 1, 1)
        plt.show(block=True)

    @staticmethod
    def violin_plot_per_distance(df, output_folder):
        pd.options.mode.chained_assignment = None
        columns = list(df.columns)[2:8]
        metrics = ['kl', 'kl_symm', 'jsd', 'jsd_root']
        for i, column in enumerate(columns):
            fig, axs = plt.subplots(ncols=len(metrics))
            fig.suptitle(column)
            df1 = df[['rec_type']]
            try:
                df1['kl'], df1['kl_symm'], df1['jsd'], df1['jsd_root'] = df[column].str
                print(column)
                print(df1.groupby('rec_type').mean())
                for a, metric in enumerate(metrics):
                    sns.violinplot(data=df1, x=metric, y="rec_type", inner="quart", split=True, ax=axs[a],
                                   title=column)
            except ValueError:
                pass
        plt.show(block=True)
