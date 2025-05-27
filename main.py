
# import libraries
from fetchdata import fetchxldata, clean_bbg_df
import pandas as pd
from yieldcurve import yieldcurve

# main function
def main() :

    # fetch par rates from excel file sources from bbg
    bbg_source = fetchxldata("data/USD_SOFR.xlsx") # convert bbg data to pandas

    # clean bbg data
    bbg_source_clean = clean_bbg_df(bbg_source)

    # SOFR yield curve
    sofryc = yieldcurve('SOFR YC', bbg_source_clean)
    sofryc.bootstrap()


    
# execute main function  
main()