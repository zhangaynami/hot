from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rcParams

# 生成图表的函数
def generate_chart(df, output_file, title=None):
    if df.empty:
        print("DataFrame为空，无法生成图表")
        return
    
    # 设置绘图风格
    sns.set(style="whitegrid")
    # 动态设置字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  
    plt.rcParams['axes.unicode_minus'] = False  

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制表格
    ax.axis('off')
    table = ax.table(
        cellText=df.values, 
        colLabels=df.columns, 
        cellLoc='center', 
        loc='center'
    )
    table.auto_set_font_size(False)
    # 调整单元格格式
    for key, cell in table.get_celld().items():
        cell.set_height(0.05)
        cell.set_fontsize(10)
    table.set_fontsize(14)
    # 自动调整列宽和表格缩放
    table.scale(1, 1.5)
    table.auto_set_column_width(col=list(range(len(df.columns))))  
    # 添加标题（如果提供了标题）
    if title:
        fig.suptitle(title, fontsize=18, y=1.15)  # y参数调整标题垂直位置
    # 保存图表
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# 获取同花顺人气榜单
def get_ths_hot_list():

    # 设置Chrome选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 如果不需要看到浏览器运行，可以开启无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')  # 设置窗口尺寸
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 使用webdriver-manager自动管理chromedriver版本
    service = Service(ChromeDriverManager().install())

    # 初始化webdriver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        print("正在抓取数据...")
        # 访问目标网站
        driver.get('https://eq.10jqka.com.cn/webpage/ths-hot-list/index.html?showStatusBar=true#/')

        # 等待动态内容加载完成
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.page'))  # 假设'.content'是你需要等待的元素
        )      
        time.sleep(3)
        # 执行滚动确保元素可见
        driver.execute_script("window.scrollBy(0, 300)")
        # 获取页面源码
        table = driver.find_element(By.CSS_SELECTOR,'.page')
        get_content = table.find_elements(By.CSS_SELECTOR, '#stock-container-a')

        result = [] 
        for content in get_content:
            get_detail_content = content.find_elements(By.CSS_SELECTOR, '[data-v-50b86fe9]>[data-v-50b86fe9]')   
            for i in get_detail_content:
                # 抓标题
                detail_content = []
                get_detail_contents = i.find_elements(By.CSS_SELECTOR, '[data-v-2e888cf8]>div')
                for i1 in get_detail_contents:
                    detail_content.append(i1.text)
                # 抓标签
                get_detail_tip =  i.find_elements(By.CSS_SELECTOR, '[data-v-4b7d5302] .mt-12.flex.flex-1')                
                detail_tip =  []                
                for i2 in get_detail_tip:
                    detail_tip.append(i2.text.replace('\n', '+'))
                # 合并标题和标签
                final_result = detail_content + detail_tip
 
                result.append(final_result) 
        result = result[1:22]        
        column_names = ['id', '排名', '公司', '涨跌幅',"热度","概念"]
        df = pd.DataFrame(result)
        df.columns = column_names
        df = df.drop(columns=df.columns[0])
        output_file_png = 'E:/小程序/人气榜/同花顺人气榜单.png' 

        generate_chart(df, output_file_png,"同花顺人气榜单")
            # 将DataFrame写入Excel文件中的特定工作表
        # if len(result) > 0:
        #     df.columns = df.iloc[0]  # 设置列名为第一行的内容
        #     df = df[1:]  # 删除第一行，因为它现在是列名
        #         # 写入Excel文件
        # output_file = 'E:/小程序/人气榜/同花顺人气榜单.xlsx'

        # df.to_excel(output_file, index=False)
        # with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        #     df.to_excel(writer, sheet_name='同花顺人气榜单', index=False)
        print("抓取成功")
        return df
        
    except Exception as e:
        print(f"抓取过程中发生错误: {str(e)}")
    finally:
        driver.quit()

# 获取东方财富人气榜单
def get_top_stocks():
    # 配置浏览器选项
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    # 自动管理ChromeDriver版本
    service = Service(ChromeDriverManager().install())  
    # 启动浏览器
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://guba.eastmoney.com/rank/')
    try:
        # 显式等待表格加载完成（最多等待10秒）
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.stock_tbody'))
        )
        # 滚动到表格位置确保内容可见
        table = driver.find_element(By.CSS_SELECTOR, '.rank_table')
        driver.execute_script("arguments[0].scrollIntoView(true);", table)
        time.sleep(1)  # 等待滚动完成
        # 提取前10行数据（跳过表头）
        rows = driver.find_elements(By.CSS_SELECTOR, '.rank_table tr')
        result = [] 
        for row in rows:
            tds = row.find_elements(By.CSS_SELECTOR, 'td')
            stock_data =[]
            for td in tds:
                stock_data.append(td.text)
            result.append(stock_data)
        print("抓取成功")
        df = pd.DataFrame(result)

        output_file_png = 'E:/小程序/人气榜/东方财富人气榜单.png' 
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])  # 删除原来的第一行（现在是列名）
        df = df.drop(columns=[df.columns[0],df.columns[1],df.columns[2], df.columns[-2], df.columns[-1]])
        print("东方财富人气榜单输出成功")
        generate_chart(df, output_file_png,"东方财富人气榜单")
        return df

        # if len(result) > 0:
        #     df.columns = df.iloc[0]  # 设置列名为第一行的内容
        #     df = df[1:]  # 删除第一行，因为它现在是列名
        #         # 写入Excel文件

    
        # output_file = 'E:/小程序/人气榜/东方财富人气榜单.xlsx'
        # df.to_excel(output_file, index=False)
        # with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        #     df.to_excel(writer, sheet_name='东方财富人气榜单', index=False)
    except Exception as e:
        print(f"抓取过程中发生错误: {str(e)}")
        return []
    finally:
        driver.quit()


# 获取资金流向
def get_funds_data_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式（可选）
    # ========== SSL错误修复关键配置 ==========
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--disable-quic')  # 禁用QUIC协议
    # ========== 反爬绕过配置 ==========
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # ========== 常规优化配置 ==========
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://data.10jqka.com.cn/funds/ggzjl/")
    driver.refresh()
    try:
        print("开始抓取资金流向")
        table = driver.find_element(By.CSS_SELECTOR, "#J-ajax-main")
        # 查看流入
        click_rank = table.find_element(By.CSS_SELECTOR, ".m-table.J-ajax-table [field='zjjlr']")
        click_rank.click()
        time.sleep(2)

        table_title = table.find_elements(By.CSS_SELECTOR, ".m-table.J-ajax-table>thead th")
        table_title_text = []
        for i in table_title:
            table_title_text.append(i.text)

        table_row = table.find_elements(By.CSS_SELECTOR, ".m-table.J-ajax-table>tbody tr")
        count_num =0 
        table_text = []
        for i in table_row: 
            if count_num<20:
                table_text_detail = []
                for j in i.find_elements(By.CSS_SELECTOR, "td"):
                    table_text_detail.append(j.text)
                table_text.append(table_text_detail)
                count_num+=1
            else:
                break
        print("抓取资金流向成功")

        df = pd.DataFrame(table_text)
        df.columns = table_title_text
        # print(df)
        # output_file_png = 'E:/小程序/人气榜/资金流向.png' 
        # generate_chart(df, output_file_png,"资金流向")
        # if len(table_text) > 0:
        #     df.columns = table_title_text
        #     output_file = 'E:/小程序/人气榜/资金流向.xlsx'
        #     df.to_excel(output_file, index=False)
        #     with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        #         df.to_excel(writer, sheet_name='资金流向', index=False)

        return df
    except Exception as e:
        print(f"抓取过程中发生错误: {str(e)}")
    finally:
        driver.quit()



# 获取热门板块
def get_industry_data_selenium():
    # 配置浏览器驱动（需提前安装ChromeDriver）
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式（可选）
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get("https://q.10jqka.com.cn/thshy/")

    try:
        # 显式等待页面加载完成
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#maincont"))
        )
        # 解析表格数据
        table = driver.find_element(By.CSS_SELECTOR, "#maincont")

        table_title = table.find_elements(By.CSS_SELECTOR, ".m-table.m-pager-table>thead th")
        table_title_text = []
        for i in table_title:
            table_title_text.append(i.text)

        table_row = table.find_elements(By.CSS_SELECTOR, ".m-table.m-pager-table>tbody tr")

        count_num =0 
        table_text = []
        for i in table_row: 
            if count_num<20:
                table_text_detail = []
                for j in i.find_elements(By.CSS_SELECTOR, "td"):
                    table_text_detail.append(j.text)
                table_text.append(table_text_detail)
                count_num+=1
            else:
                break

        print("抓取热门板块成功")
        df = pd.DataFrame(table_text)
        df.columns = table_title_text
        return df
        # output_file_png = 'E:/小程序/人气榜/热门板块.png' 
        # generate_chart(df, output_file_png,"热门板块")


        # if len(table_text) > 0:
        #     df.columns = table_title_text
        #     output_file = 'E:/小程序/人气榜/热门板块.xlsx'
        #     df.to_excel(output_file, index=False)
        #     with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        #         df.to_excel(writer, sheet_name='热门板块', index=False)
    except Exception as e:
        print(f"抓取过程中发生错误: {str(e)}")
    finally:
        driver.quit()

