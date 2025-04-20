from flask import Flask, render_template, send_from_directory
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():

    data_tgbrg = pd.read_csv('淘股吧热股.csv').to_dict('records')
    data_xqrg = pd.read_csv('雪球热股.csv').to_dict('records')
    data_dfcfrg = pd.read_csv('东方财富热搜.csv').to_dict('records')
    data_thsrg = pd.read_csv('同花顺热搜.csv').to_dict('records')

    return render_template('/index.html',tgbrgs = data_tgbrg, xqrgs = data_xqrg,data_dfcfrgs = data_dfcfrg,data_thsrgs = data_thsrg)


if __name__ == '__main__':
    app.run(debug=True)
