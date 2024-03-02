import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

CLEAN_USER_TABLE_PATH = '../data/User_table_cleaned.csv'



def get_from_action_data(fname, chunk_size=50000):
    reader = pd.read_csv(fname, header=0, iterator=True)
    chunks = []
    loop = True
    while loop:
        try:
            chunk = reader.get_chunk(chunk_size)[
                ["user_id", "sku_id", "type", "time"]]
            chunks.append(chunk)
        except StopIteration:
            loop = False
            print("Iteration is stopped")

    df_ac = pd.concat(chunks, ignore_index=True)

    # type=4 -> purchse action
    df_ac = df_ac[df_ac['type'] == 4]

    return df_ac[["user_id", "sku_id", "time"]]


def get_data_from_each_month():
    df_ac = []
    df_ac.append(get_from_action_data(fname=ACTION_02_FILE_PATH))
    df_ac.append(get_from_action_data(fname=ACTION_03_FILE_PATH))
    df_ac.append(get_from_action_data(fname=ACTION_04_FILE_PATH))
    df_ac = pd.concat(df_ac, ignore_index=True)

    # convert time column to datetime type
    df_ac['time'] = pd.to_datetime(df_ac['time'])

    #  convert time to days of the week (Monday is 1, Sunday is 7).
    df_ac['time'] = df_ac['time'].apply(lambda x: x.weekday() + 1)

    return df_ac

# visualize traffic for each 
def visualize_weekly_traffic():
    df_ac = get_data_from_each_month()

    # analyze traffic on users amount
    df_user = df_ac.groupby('time')['user_id'].nunique()
    df_user = df_user.to_frame().reset_index()
    df_user.columns = ['weekday', 'user_num']

    # anaylze traffice on sold items amount
    df_ui = df_ac.groupby('time', as_index=False).size()
    df_ui.columns = ['weekday', 'user_item_num']
    

    # visualizer
    bar_width = 0.2
    opacity = 0.4

    plt.figure(figsize=(9,6))

    plt.bar(df_user['weekday'], df_user['user_num'], bar_width, 
            alpha=opacity, color='#3498db', label='Active Users')
    plt.bar(df_ui['weekday']+bar_width*2, df_ui['user_item_num'], 
            bar_width, alpha=opacity, color='#e67e22', label='Items Sold')

    plt.xlabel('weekday')
    plt.ylabel('number')
    plt.title('A Week Purchase Table')
    plt.xticks(df_user['weekday'] + bar_width * 3 / 2., (1,2,3,4,5,6,7))

    plt.tight_layout() 
    plt.legend(prop={'size':10})

    plt.savefig('./Weekly purchase data visualisation.png',dpi = 200)


def visualize_monthly_traffic():
    df_ac = get_from_action_data(fname=ACTION_02_FILE_PATH)
    df_ac['time'] = pd.to_datetime(df_ac['time']).apply(lambda x: x.day)


    # analyze traffic on users amount
    df_user = df_ac.groupby('time')['user_id'].nunique()
    df_user = df_user.to_frame().reset_index()
    df_user.columns = ['day', 'user_num']

    # anaylze traffice on sold items amount
    df_ui = df_ac.groupby('time', as_index=False).size()
    df_ui.columns = ['day', 'user_item_num']


    bar_width = 0.2
    opacity = 0.4
    day_range = range(1,len(df_user['day']) + 1)
    plt.figure(figsize=(14,10))

    plt.bar(df_user['day'], df_user['user_num'], bar_width, 
            alpha=opacity, color='#3498db', label='Active Users')

    plt.bar(df_ui['day']+bar_width*2, df_ui['user_item_num'], 
            bar_width, alpha=opacity, color='#e67e22', label='Items Sold')

    plt.xlabel('day')
    plt.ylabel('number')
    plt.title('February Purchase Table')
    plt.xticks(df_user['day'] + bar_width * 3 / 2., day_range)
    plt.tight_layout() 
    plt.legend(prop={'size':15})

    plt.savefig('./Feb purchase data visualisation.png',dpi = 200)

if __name__ == "__main__":
    visualize_weekly_traffic()
    visualize_monthly_traffic()