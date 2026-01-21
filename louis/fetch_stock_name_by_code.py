import logging
import sys
import warnings
from pathlib import Path
from typing import Optional
import pandas as pd
import tushare as ts
import requests

warnings.filterwarnings("ignore")

# --------------------------- 全局日志配置 --------------------------- #
LOG_FILE = Path("fetch_stock_name.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("fetch_stock_name_by_code")

stock_dict = {}
# 初始化pro接口
# pro = ts.pro_api('1ec16733c012b923a9d2ce4cdc914f3b1d121c797c0233d7c18247d3')
pro = ts.pro_api('2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211')

stock_info_df = None


# 启动时只获取一次股票列表
def fetch_all_stock_info():
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
    return df


# 根据股票代码查找名称
def get_name_by_code_in_tushare(code: str) -> str | None:
    global stock_info_df
    try:
        if stock_info_df is None or stock_info_df.empty:
            stock_info_df = fetch_all_stock_info()
        row = stock_info_df[stock_info_df['ts_code'].str.startswith(code) | (stock_info_df['symbol'] == code)]
        if not row.empty:
            return row.iloc[0]['name']
        logger.warning("股票代码 %s 在 Tushare 中未找到对应名称", code)
    except Exception as e:
        logger.error("Tushare 查询股票代码 %s 异常：%s", code, e)
    return None


def get_code_name_dict() -> dict[str, str]:
    global stock_dict
    stocklist_csv = Path("./stocklist.csv")
    if not stocklist_csv.exists():
        logger.warning("未找到 %s，请检查文件路径", stocklist_csv)
        stocklist_csv = Path("./louis/stocklist.csv")
    logger.warning("重新使用 %s，文件路径", stocklist_csv)
    df = pd.read_csv(stocklist_csv)
    stock_dict = dict(zip(df["symbol"].astype(str).str.zfill(6), df["name"]))

    logger.info("从 %s 读取到 %d 只股票",
                stocklist_csv, len(stock_dict))
    return stock_dict


def get_stock_name_by_code(code: str) -> Optional[str]:
    """根据股票代码获取股票名称"""
    global stock_dict
    if not stock_dict:
        get_code_name_dict()
    code = str(code).zfill(6)
    stock_name = stock_dict.get(code, None)
    if stock_name:
        return stock_name

    logger.warning("股票代码 %s 未在本地列表中找到，尝试使用 Tushare 查询", code)
    stock_name = get_name_by_code_in_tushare(code)
    if stock_name:
        return stock_name
    return f'股票{code}'


def fetch_stock_name_from_local() -> Optional[str]:
    stock_list = ['000007', '000021', '000301', '000415', '000623', '000720', '000776', '000850', '000863', '000925',
                  '000973', '001207', '001229', '001231', '001299', '001316', '002009', '002048', '002083', '002111',
                  '002167', '002168', '002169', '002177', '002179', '002183', '002185', '002228', '002245', '002297',
                  '002324', '002338', '002367', '002389', '002438', '002501', '002585', '002601', '002626', '002631',
                  '002664', '002669', '002774', '002923', '002933', '002937', '002953', '600038', '600064', '600115',
                  '600165', '600178', '600230', '600284', '600345', '600348', '600416', '600435', '600456', '600501',
                  '600506', '600523', '600590', '600623', '600667', '600703', '600736', '600744', '600784', '600862',
                  '600893', '600909', '600927', '600973', '601021', '601096', '601163', '601599', '601601', '601616',
                  '601688', '601888', '603002', '603058', '603081', '603085', '603278', '603283', '603297', '603332',
                  '603344', '603638', '603656', '603660', '603757', '603867', '603868', '603936', '603979', '605088',
                  '605338', '605507']
    for code in stock_list:
        stock_name = get_stock_name_by_code(code)
        print(f"股票代码: {code}, 股票名称: {stock_name}")
    print(f"从本地获取到 {len(stock_list)} 只股票")


if __name__ == "__main__":
    # fetch_stock_name_from_local()

    url = "http://wechat.liuazhi.xyz/stock_list.txt"
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    stock_list_str = response.text
    stock_list = [
        code.strip()
        for code in stock_list_str.split(',')
        if code.strip()
    ]
    print(f"从远程获取到 {len(stock_list)} 只股票")
    for code in stock_list:
        stock_name = get_stock_name_by_code(code)
        print(f"股票代码: {code}, 股票名称: {stock_name}")
