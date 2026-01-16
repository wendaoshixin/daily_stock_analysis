import logging
import sys
import warnings
from pathlib import Path
from typing import Optional
import pandas as pd

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
    return stock_dict.get(code, f'股票{code}')


if __name__ == "__main__":
    stock_name = get_stock_name_by_code("000017")
    print(stock_name)
    stock_name = get_stock_name_by_code("000019")
    print(stock_name)
