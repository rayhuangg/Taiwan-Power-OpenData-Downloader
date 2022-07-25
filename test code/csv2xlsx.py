from operator import index
import pandas as pd

def csv_to_xlsx_pd():
    csv = pd.read_csv('2022_07_02.csv', encoding='utf-8', index_col=0)
    csv.to_excel('1.xlsx', sheet_name='data', index=False)

if __name__ == '__main__':
    csv_to_xlsx_pd()