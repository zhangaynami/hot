import akshare as ak
import sys
import io
import os


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
stock_zh_a_spot_em_df = ak.stock_sh_a_spot_em()
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建完整文件路径
csv_filename = os.path.join(script_dir, "所有个股.csv")
stock_zh_a_spot_em_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

print("success")