import akshare as ak
import pandas as pd
import os


stock_gdfx_free_holding_analyse_em_df = ak.stock_gdfx_free_holding_analyse_em(date="20240930")
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建完整文件路径
csv_filename = os.path.join(script_dir, "流通股东.csv")
stock_gdfx_free_holding_analyse_em_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')


print(stock_gdfx_free_holding_analyse_em_df)