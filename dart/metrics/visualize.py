import matplotlib.pyplot as plt
import pandas as pd


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
