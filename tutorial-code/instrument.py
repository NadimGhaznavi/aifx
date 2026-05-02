# instrument.py

import pandas as pd
import utils


class Instrument:
    def __init__(self, ob):
        self.name = ob["name"]
        self.ins_type = ob["type"]
        self.displayName = ob["displayName"]

        self.pipLocation = pow(10, ob["pipLocation"])  # -4 -> 0.0001
        self.marginRate = ob["marginRate"]

    def __repr__(self):
        return str(vars(self))

    # Data retrival here is a file based data cache using Pickle
    # Each file contains one instrument (e.g. CAD_USD)
    @classmethod
    def get_instruments_df(cls):
        return pd.read_pickle(utils.get_instruments_data_filename())

    # Return the list of intruments as a list of DataFrames.
    @classmethod
    def get_instruments_list(cls):
        df = cls.get_instruments_df()
        return [Instrument(x) for x in df.to_dict(orient="records")]


if __name__ == "__main__":
    print(Instrument.get_instruments_list())
