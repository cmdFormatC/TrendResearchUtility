import pandas as pd

#создатель листа seller, если он кнчн нужен
def makeSellersInfo(df):
    #рубим лишнее после слеша
    df['C1'] = df['category'].str.replace(' / ', '/').str.split('/', expand=True)[0]
    #Разделение столбца на два
    df['subject'] = df['subject'].str.replace(' / ', '/')
    df[['S1', 'S2']] = df['subject'].str.split('/', expand=True)
    #Съебываем это все в свобную таблицу по указанынм категориям и скалдываем revenue
    pivot_table = df.groupby(['C1','S1', 'S2', 'seller'])['revenue'].sum().reset_index()
    return pivot_table


#создатель листа s2
def makeS2Sheet(df):
    #Обрезка длинных названий и разделка сабджекта
    df['C1'] = df['category'].apply(lambda x: str(x).split('/')[0] if pd.notna(x) else '')
    df['S1'] = df['subject'].apply(lambda x: str(x).split('/')[0] if pd.notna(x) else '')
    df['S2'] = df['subject'].apply(lambda x: str(x).split('/')[1] if pd.notna(x) and len(str(x).split('/')) > 1 else '')
    results = pd.DataFrame()

    # Как я понял групировка по уникальному названию сабжекта
    groups = df.groupby('S2')

    # циклом по этим названиям и подсчеты
    for name, group in groups:
        data = {
            'C1': group['C1'].iloc[0],
            'S1': group['S1'].iloc[0],
            'S2': name,
            'Total Revenue': group['revenue'].sum(),
            'SCU Count': group['id'].nunique(),
            'Seller Count': group['seller'].nunique(),
            'Top1 Seller Revenue': group.groupby('seller')['revenue'].sum().nlargest(1).values[0],
            '% Top1': group.groupby('seller')['revenue'].sum().nlargest(1).values[0] / group['revenue'].sum() * 100,
            'Top6 Sellers Revenue': group.groupby('seller')['revenue'].sum().nlargest(6).sum(),
            '% Top6': group.groupby('seller')['revenue'].sum().nlargest(6).sum() / group['revenue'].sum() * 100,
            'Total Lost Revenue': group['lost_profit'].sum(),
            '% Lost Revenue': group['lost_profit'].sum() / group['revenue'].sum() * 100,
            'Max Reviews': group['comments'].max(),
            'Average Price': group['final_price_average'].mean(),
            'Purchase Percentage': group['purchase_after_return'].mean(),
            'Average SPP': group['client_sale'].mean()
        }

        #Запись каждой итерации
        results = pd.concat([results, data], ignore_index=True)
        return results
    
#Для тестирования 

#Опредение датафрейма
df = pd.read_excel('output.xlsx', engine='openpyxl')

#Создание селлеров
seller_table = makeSellersInfo(df)
seller_table.to_excel('sellerinfo.xlsx', index=False)

#Создание S2
s2_table = makeS2Sheet(df)
s2_table.to_excel('S2Info.xlsx', index=False)


#ИНДЕКСЫ ИГНОРИТЬ ВСЕГДА, ТАК КАК ЭТО БАЙТ НА ХУЙНЮ С ВЗАИМНОЙ ЗАВИСИМОСТЬЮ