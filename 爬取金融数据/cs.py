import requests
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
from tools import *
from datetime import datetime,timedelta
import os
import sys
import io
import tkinter as tk
import akshare as ak
import streamlit as st

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def all_stocks():
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建完整文件路径
    csv_filename = os.path.join(script_dir, "所有个股.csv")
    stock_zh_a_spot_em_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')

    print("success")
all_stocks()