from datetime import datetime,timedelta
import seaborn as sns
import matplotlib.pyplot as plt

'''
=========获取交易日=========
'''
def get_yesterday_date(date_str):
    # 根据给定的日期字符串计算昨天的日期
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    yesterday = date_obj - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


'''
=========输出图表=========
'''
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