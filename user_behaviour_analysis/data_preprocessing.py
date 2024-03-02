import pandas as pd
import gc
from collections import Counter
import numpy as np


# data validation
USER_FILE_PATH = '../data/JData_User.csv'
PRODUCT_FILE_PATH = '../data/JData_Product.csv'
COMMENT_FILE_PATH = '../data/JData_Comment.csv'
ACTION_02_FILE_PATH = '../data/JData_Action_201602.csv'
ACTION_03_FILE_PATH = '../data/JData_Action_201603.csv'
ACTION_04_FILE_PATH = '../data/JData_Action_201604.csv'

ACTION_02_FILE_PATH_DEDUP = '../data/JData_Action_201602_dedup.csv'
ACTION_03_FILE_PATH_DEDUP = '../data/JData_Action_201603_dedup.csv'
ACTION_04_FILE_PATH_DEDUP = '../data/JData_Action_201604_dedup.csv'

CLEAN_USER_TABLE_PATH = '../data/User_table.csv'

def user_action_id_check():
    # validate that users from action tables are subsets from user table
    df_user = pd.read_csv('../data/JData_User.csv')
    df_user = df_user.loc[:,'user_id'].to_frame()
    df_month2 = pd.read_csv('../data/JData_Action_201602.csv')
    df_month3 = pd.read_csv('../data/JData_Action_201603.csv')
    df_month4 = pd.read_csv('../data/JData_Action_201604.csv')
    assert len(df_month2) == len(pd.merge(df_user,df_month2))
    assert len(df_month3) == len(pd.merge(df_user,df_month3))
    assert len(df_user) == len(pd.merge(df_user,df_month4))
    print("users action tables validated.")
    del df_user, df_month2, df_month3, df_month4
    gc.collect()


# validate depilicate data and deduplicate if found
def deduplicate(filepath, filename, newpath):
    df_file = pd.read_csv(filepath)
    before = df_file.shape[0]
    df_file.drop_duplicates(inplace=True)
    after = df_file.shape[0]
    n_dup = after - before
    if n_dup != 0:
        print(' No. of duplicate records for ' + filename + ' is :' + str(n_dup))
        df_file.to_csv(newpath, index=None)
    else:
        print('no duplicates found for file ' + filename)
    del df_file
    gc.collect()

# analyze duplicate data allocation group by 'type'
def check_duplicate(filepath):
    df_month3 = pd.read_csv(filepath)
    IsDuplicated = df_month3.duplicated(subset=['user_id','type'],keep=False) 
    IsDuplicated = df_month3.duplicated(keep=False) 
    df_d=df_month3[IsDuplicated]
    #print(df_d.head(10))
    print(df_d.groupby('type').count())
    del df_month3,df_d
    gc.collect()


# create a new user table caculate user behavior

# helper function to count numbers of each behavior type
def add_type_count(group):
    behavior_type = group.type.astype(int)
    type_cnt = Counter(behavior_type)

    # 1->brose 2->addToCart 3->delete 4->buyAsFav 5->save 6->click
    group['browse_num'] = type_cnt[1]
    group['addcart_num'] = type_cnt[2]
    group['delcart_num'] = type_cnt[3]
    group['buy_num'] = type_cnt[4]
    group['favor_num'] = type_cnt[5]
    group['click_num'] = type_cnt[6]

    return group[['user_id', 'browse_num','addcart_num','delcart_num','buy_num','favor_num','click_num']]


def get_from_action_data(fname, chunk_size=50000):
    reader = pd.read_csv(fname, header=0, iterator=True)
    chunks = []
    loop = True

    while loop:
        try:
            chunk = reader.get_chunk(chunk_size)[["user_id","type"]]
            chunks.append(chunk)
        except StopIteration:
            loop = False
            print("Iteration stopped.")

    
    df_ac = pd.concat(chunks, ignore_index=True)
    
    df_ac = df_ac.groupby(['user_id'],as_index=False).apply(add_type_count)

    df_ac = df_ac.drop_duplicates('user_id')
    
    return df_ac


# merge user actions from three month tables
def merge_action_tables():
    df_ac = []
    df_ac.append(get_from_action_data(fname=ACTION_02_FILE_PATH))
    df_ac.append(get_from_action_data(fname=ACTION_03_FILE_PATH))
    df_ac.append(get_from_action_data(fname=ACTION_04_FILE_PATH))

    # concact three df and apply sum on usr_id group
    df_ac = pd.concat(df_ac, ignore_index=True)
    df_ac = df_ac.groupby(['user_id'], as_index=False).sum()

    # create conversion column
    df_ac['buy_addcart_ratio'] = df_ac['buy_num'] / df_ac['addcart_num']
    df_ac['buy_browse_ratio'] = df_ac['buy_num'] / df_ac['browse_num']
    df_ac['buy_click_ratio'] = df_ac['buy_num'] / df_ac['click_num']
    df_ac['buy_favor_ratio'] = df_ac['buy_num'] / df_ac['favor_num']

    # Set conversion rate fields greater than 1 to 1 
    # print((df_ac['buy_addcart_ratio'] > 1.).sum())
    df_ac.loc[df_ac['buy_addcart_ratio'] > 1., 'buy_addcart_ratio'] = 1.
    df_ac.loc[df_ac['buy_browse_ratio'] > 1., 'buy_browse_ratio'] = 1.
    df_ac.loc[df_ac['buy_click_ratio'] > 1., 'buy_click_ratio'] = 1.
    df_ac.loc[df_ac['buy_favor_ratio'] > 1., 'buy_favor_ratio'] = 1.


    # get additional info from user table
    df_usr = pd.read_csv(USER_FILE_PATH, header=0)
    df_usr = df_usr[["user_id", "age", "sex", "user_lv_cd"]]

    # merge df_usr and df_ac into user behavior table
    user_table = pd.merge(df_usr, df_ac, on=['user_id'], how='left')

    user_table.to_csv(CLEAN_USER_TABLE_PATH, index=False)

    del df_ac, df_usr, user_table
    gc.collect()


# clean user table

def clean_user_table(fname):
    df_user = pd.read_csv(fname, header=0)
    pd.options.display.float_format = '{:,.3f}'.format
    # print(df_user.describe())

    # save only records from active users [to exclude user with missing info, web crawlers etc.]
    to_drop_list = np.array([])

    # users with missing info
    to_drop_list = np.concatenate(
        (
            to_drop_list, df_user[df_user['age'].isnull()].index.to_numpy()
        )
    )


    # users with no interactions
    to_drop_list = np.concatenate((
        to_drop_list, (
        df_user[
            df_user['browse_num'].isnull() & df_user['addcart_num'].isnull() & df_user['delcart_num'].isnull() & df_user['buy_num'].isnull() \
            & df_user['favor_num'].isnull() & df_user['click_num'].isnull()
        ].index.to_numpy()
    )))

    # inactive users
    to_drop_list = np.concatenate(
        (
            to_drop_list, 
            (
                df_user[df_user['buy_browse_ratio']<0.0005].index.to_numpy()
            )
        )
    )
    

    df_user.drop(to_drop_list, axis=0, inplace=True)
    df_user.to_csv('../data/User_table_cleaned.csv',index=False)
    del df_user
    gc.collect()



if __name__ == "__main__":
    #user_action_id_check()
    #deduplicate(ACTION_02_FILE_PATH, 'Feb. action', ACTION_02_FILE_PATH[:4] + '_dedup.csv')
    # deduplicate(ACTION_03_FILE_PATH, 'Mar. action', ACTION_03_FILE_PATH[:4] + '_dedup.csv')
    # deduplicate(ACTION_04_FILE_PATH, 'Apr. action', ACTION_04_FILE_PATH[:4] + '_dedup.csv')
    # deduplicate(COMMENT_FILE_PATH, 'Comment', COMMENT_FILE_PATH[:4] + '_dedup.csv')
    # deduplicate(PRODUCT_FILE_PATH, 'Product', PRODUCT_FILE_PATH[:4] + '_dedup.csv')
    # deduplicate(USER_FILE_PATH, 'User', USER_FILE_PATH[:4] + '_dedup.csv')
    # check_duplicate(ACTION_02_FILE_PATH)
    # merge_action_tables()
    clean_user_table(CLEAN_USER_TABLE_PATH)
