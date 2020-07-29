import matplotlib.pyplot as plt
import pandas as pd


class Visualize:

    @staticmethod
    def print_mean(df, value):
        print(df.groupby('type')[value].mean())

    @staticmethod
    def plot(df, value):
        plt.figure()
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
        df = df.sort_values('date', ascending=True)
        df.set_index('date', inplace=True)
        df.groupby('type')[value].plot(legend=True)
        plt.xticks(rotation='vertical')
        plt.draw()
