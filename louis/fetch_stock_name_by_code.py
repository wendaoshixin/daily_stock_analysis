import logging
import sys
import warnings
from pathlib import Path
from typing import Optional
import pandas as pd
import tushare as ts

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


if __name__ == "__main__":
    stock_name = get_stock_name_by_code("000018")
    print(stock_name)
    stock_name = get_stock_name_by_code("000019")
    print(stock_name)
