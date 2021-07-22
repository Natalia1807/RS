def prefilter_items(data):
    
    # Оставим только 5000 самых популярных товаров
    popularity = data.groupby('item_id')['quantity'].sum().reset_index()
    popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
    top_5000 = popularity.sort_values('n_sold', ascending=False).head(5000).item_id.tolist()
    #добавим, чтобы не потерять юзеров
    data.loc[~data['item_id'].isin(top_5000), 'item_id'] = 999999 
    
    # Уберем самые популярные 
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index()
    popularity['user_id'] = popularity['user_id'] / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)
    top_popular = popularity[popularity['share_unique_users'] > 0.2].item_id.tolist()
    data.loc[data['item_id'].isin(top_popular), 'item_id'] = 999999
    
    # Уберем самые непопулярные 
    unpopular = popularity[popularity['share_unique_users'] < 0.02].item_id.tolist()
    data.loc[data['item_id'].isin(unpopular), 'item_id'] = 999999 
    
    # Уберем товары, которые не продавались за последние 12 месяцев
    period = data.week_no.max() - 48
    sold_actual = data[data.week_no >= period].item_id.unique().tolist()
    data.loc[~data['item_id'].isin(sold_actual), 'item_id'] = 999999
    
    # Уберем не интересные для рекоммендаций категории (department)
    dep_size = item_features.groupby('department')['item_id'].nunique().\
                                       sort_values(ascending=False).reset_index()
    dep_size.rename(columns={'item_id': 'n_items'}, inplace=True)
    departments = dep_size[dep_size.n_items < 150].department.tolist()

    items_in_deparmments = item_features[item_features.department.isin(departments)].item_id.unique().tolist()
    data.loc[data['item_id'].isin(items_in_deparmments), 'item_id'] = 999999
    
    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    data['price'] = data['sales_value'] / np.maximum(data['quantity'], 1)
    data.loc[data['price'] < 2, 'item_id'] = 999999
    
    # Уберем слишком дорогие товары
    data.loc[data['price'] > 50, 'item_id'] = 999999

    return data

def postfilter_items():
    pass

def get_similar_items_recommendation(self, user, N=5):
    """Рекомендуем товары, похожие на топ-N купленных юзером товаров"""

    # your_code
        
    recs = model.similar_items(itemid_to_id[user], N=N)
    recs= [id_to_itemid[rec[0]] for rec in recs]
        
    assert len(recs) == N, 'Количество рекомендаций != {}'.format(N)
    return  recs
    
def get_similar_users_recommendation(self, user, N=5):
    """Рекомендуем топ-N товаров, среди купленных похожими юзерами"""
    
    # your_code
    try:
        res = [id_to_itemid[rec[0]] for rec in model.recommend(userid=userid_to_id[user], 
                                        user_items=csr_matrix(user_item_matrix).tocsr(),   # на вход user-item matrix
                                        N=N, 
                                        filter_already_liked_items=False, 
                                        recalculate_user=True)]
    except KeyError: 
        res = None

    assert len(res) == N, 'Количество рекомендаций != {}'.format(N)
    return res