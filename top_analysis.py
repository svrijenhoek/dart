import dart.Util
import pandas as pd


pd.set_option('display.float_format', '{:.5f}'.format)

config = dart.Util.read_full_config_file()
articles = dart.Util.read_pickle(config['articles'])
recommendations = dart.Util.read_pickle(config['recommendations'])
behavior_file = dart.Util.read_behavior_file(config['behavior_file'])

recommendation_types = ['lstur', 'naml', 'pop', 'random']


def retrieve_articles(newsids):
    return articles[articles['newsid'].isin(newsids)]


df = pd.DataFrame(columns=articles.category.unique())
recommendation_df = pd.DataFrame(columns=articles.category.unique())
history_df = pd.DataFrame(columns=articles.category.unique())

for i, impression in enumerate(behavior_file):
    if i % 1000 == 0:
        print(i)
    impr_index = impression['impression_index']

    pool_articles = retrieve_articles(article for article in impression['items_without_click'])
    df = df.append(pool_articles['category'].value_counts(normalize=True))

    reading_history = retrieve_articles([_id for _id in impression['history']])
    value_count = reading_history['category'].value_counts(normalize=True)
    value_count['impr_index'] = impr_index
    history_df = history_df.append(value_count)

    # for rec_type in recommendation_types:
    #     recommendation = recommendations.loc[
    #         (recommendations['impr_index'] == impr_index) &
    #         (recommendations['type'] == rec_type)]
    #     recommendation_articles = retrieve_articles([_id for _id in recommendation.iloc[0].articles])
    #     value_count = recommendation_articles['category'].value_counts(normalize=True)
    #     value_count['rec_type'] = rec_type
    #     value_count['impr_index'] = impr_index
    #     recommendation_df = recommendation_df.append(value_count)

history_df = history_df.set_index('impr_index')
history_df = history_df.fillna(0)
# recommendation_df = recommendation_df.set_index('impr_index')
recommendation_df = recommendation_df.fillna(0)

print(articles.category.value_counts(normalize=True))
print('===MEAN===')
# print(df.mean())
# print(recommendation_df.groupby('rec_type').mean().T)
print(history_df.mean().T)
print('===STD===')
# print(df.std())
# print(recommendation_df.groupby('rec_type').std().T)
print(history_df.std().T)


