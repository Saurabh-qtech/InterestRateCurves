# import libraries
import numpy as np
import math
from scipy.optimize import minimize

# create class yieldcurve

class yieldcurve :

    # constructor 1
    def __init__(self, name_) :
        self.name = name_ # name of the curve
        self.calibration_instruments = None  # market instruments to calibrate yield curve

    # constructor 2
    def __init__(self, name_, cal_instruments) :
        self.name = name_ # name of the curve
        self.calibration_instruments = cal_instruments  # market instruments to calibrate yield curve
        self.numberofInstruments = len(cal_instruments) # number of calibration instruments 
        self.minTenor = cal_instruments['Tenor'].min() # min Tenor of calibration inst
        self.maxTenor = cal_instruments['Tenor'].max() # max Tenor of calibration inst
        # zero rates : zr (# annual compunded rates)
        self.zr = np.ones(math.ceil(self.maxTenor)) * 0.01  # intial guess : flat curve 1% rates
        # fwd rates
        self.fr = self.forward_rates(self.zr)
        # Discount rate
        self.discountfactors = self.DiscountFactor(self.zr)

    # curve building
    def what_is_curve_buidling(self, i) :
        overview = 'The process of buidling the IR curve (/ curve stripping) involves creating a zero rates (zr) curve that would make the theoretical price of the \
                    liquid instruments equal to the prices observed in the market (also known as calibration) \
                    '
        process = 'all swaps are annual pmt (bith fixed anf float leg), so we can create zero coupon rate from yr 1 to 50 and not include any fractional year \
              . swaps with tenor < 1yr are based on 1 year zr curve '
        
        if i == 0 :
            print(overview)
        else:
            print(process)


    # fwd rates : fr (# 1 yr fwd rates)
    def forward_rates (self, zr) :
        fr = [] # list of fwd rates

        Fplus1product = 1  # initialize cumm fwd rate

        for i in range(len(zr)) :
                
            f = ((1 + zr[i]) ** (i + 1)) / Fplus1product - 1  # calculate forward rate

            if not np.isfinite(f):
                    f = 0.0

            fr.append(f) # add forward rate to list

            Fplus1product = Fplus1product * (1 + f)  # increment the cumulative forward rate

        return fr

        
    # Discount factors 
    def DiscountFactor (self, zr) :

        discountfactors = {}   # intialize discount factors to a Dictionary

        for idx , row in self.calibration_instruments.iterrows() :

            if row['Tenor'] <= 1 :
                discountfactors[row['Tenor']] = 1 / (1 + zr[0] * row['Tenor'])

            for i in range(2 , int(self.maxTenor) + 1) :
                discountfactors[i] = 1 / (1 + zr[i-1]) ** (i)

        return discountfactors


    # Calculate error in price using current zero rates
    def pricing_error (self, zr) :

        error_total = 0     # cummulative error

        # For all instruments calculate PV_fixed - PV_float
        # { We get PV_fixed from calibration instruments and zc curve 
        # We get PV_float from fr curve }

        fr = self.forward_rates(zr)
        discountfactors = self.DiscountFactor(zr)

        for idx, row in self.calibration_instruments.iterrows() :       # iterate through calibration instruments

            tenor = row['Tenor']

            if tenor <= 1 :
                error = row['Par rate'] - fr[0]

            else :
                t = 1
                PV_float = 0
                PV_fixed = 0
                while (t <= int(row['Tenor'])) :
                    PV_float = PV_float + fr[t-1] * 1 * discountfactors.get(t, 0)
                    PV_fixed = PV_fixed + discountfactors.get(t, 0)
                    t = t + 1           # increment payment year
                if PV_fixed == 0:
                    continue
                error = row['Par rate'] - PV_float / PV_fixed

            error_total = error_total + error ** 2      # track error
        
        return error_total
    
    # fit / calibrate zero curve to IRS par rates
    def fit (self) :

        result = minimize(self.pricing_error, self.zr)
        self.zr = result.x
        self.fr = self.forward_rates(self.zr)
        self.discountfactors = self.DiscountFactor(self.zr)


    # Yield curve observed from using pricing_error and fit, we see sharp jumps and falls - indicating too much fit to some instruments (assuming forward staes are stable)
    # We introduce some type of interpolation technique to calculate yield curve






        

        
    


    

