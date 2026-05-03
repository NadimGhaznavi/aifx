# tutorial-code/utils.py

from aifx.constants.DDir import DDir
from aifx.constants.DFile import DFile
from aifx.constants.DPairs import DPair as PAIR
from aifx.constants.DFrequency import DFrequency as FREQ


def get_his_data_filename(pair, granularity):
    return f"{DDir.HISTORICAL_DATA}/{pair}_{granularity}{DFile.DOT_PICKLE}"


def get_instruments_data_filename():
    return DFile.INSTRUMENTS


if __name__ == "__main__":
    print(get_his_data_filename(PAIR.EUR_USD, FREQ.H1))
    print(get_instruments_data_filename())
