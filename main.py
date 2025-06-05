
# import libraries
from fetchdata import fetchxldata, clean_bbg_df
import pandas as pd
from InterestRateCurves.yieldcurve_noInterpolation import yieldcurve
from printfunctions import printdictionary, printList
import matplotlib.pyplot as plt 
import numpy as np

# main function
if __name__ == "__main__" : 

    # fetch par rates from excel file sources from bbg
    bbg_source = fetchxldata("data/USD_SOFR.xlsx") # convert bbg data to pandas

    # clean bbg data
    bbg_source_clean = clean_bbg_df(bbg_source)

    print(bbg_source_clean)

    # SOFR yield curve
    sofryc = yieldcurve('SOFR YC', bbg_source_clean)
    sofryc.fit()

    print(len(sofryc.discountfactors))
    print(len(sofryc.zr))
    print(len(sofryc.fr))
    #printdictionary(sofryc.discountfactors)

    # plot
    plt.plot(list(range(1, 51)), sofryc.zr)
    plt.xticks(np.arange(1,52,3))
    plt.yticks(np.arange(0.01,0.11,0.005))
    plt.grid()
    plt.show()

   
    


