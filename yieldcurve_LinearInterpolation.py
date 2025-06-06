# import libraries
import numpy as np
import math
from scipy.optimize import minimize

# checks:
#check if we using the input to construtcor as a dictionary. It is pd.dataFrame. Mostly used to get list of tenors in calibrated instruments


# create class yieldcurve with Linear Interpolation

class yieldcurve_LI :

    # constructor 1
    def __init__(self, name_) :
        self.name = name_ # name of the curve
        self.calibration_instruments = None  # market instruments to calibrate yield curve

    # constructor 2
    def __init__(self, name_, cal_instruments) :
        '''
        Inputs:
        name : string
        cal_instruments : pd.DataFrame

        '''
        self.name = name_ # name of the curve
        self.calibration_instruments = cal_instruments  # market instruments to calibrate yield curve
        self.numberofInstruments = len(cal_instruments) # number of calibration instruments 
        self.minTenor = cal_instruments['Tenor'].min() # min Tenor of calibration inst
        self.maxTenor = cal_instruments['Tenor'].max() # max Tenor of calibration inst
        # zero rates : zr (# annual compunded rates)  ## -> list for 1 to 50 Yr tenor
        self.zr = np.ones(math.ceil(self.maxTenor)) * 0.01  # intial guess : flat curve 1% rates
        # fwd rates  ## -> 1 Yr fwd, strting t = 0 to t = 49 Yr
        self.fr = self.forward_rates(self.zr)
        # Discount rate  ## Dictionary, all dates 
        self.discountfactors = self.DiscountFactor(self.zr)

    # curve building
    def what_is_curve_buidling(self, i) :
        overview = 'The process of buidling the IR curve (/ curve stripping) involves creating a zero rates (zr) curve that would make the theoretical price of the \
                    liquid instruments equal to the prices observed in the market (also known as calibration) \
                    '
        process = 'all swaps are annual pmt (bith fixed anf float leg), so we can create zero coupon rate from yr 1 to 50 and not include any fractional year \
              . swaps with tenor < 1yr are based on 1 year zr curve . Here we also introduce linear interpolation to find zr for tenor w/o calbration instruments'
        
        if i == 0 :
            print(overview)
        else:
            print(process)

    # zr (initial guess) -> zr_dict -> linear_interpolated zr list  ||| What we have 
    # the optimizer needs a zr intial guess i/p and same structue o/p -> zr_dict -> linear interpolated zr list   ||| What we need to build ||| 1. guess_zr to expanded zr 

    # intial guess for zr 
    def initial_guess_zr (self) :

        zr_init_guess = []

        y = 0.01
        inc = 0.001

        # have a increasing zr initial guess
        for i in range (len(self.calibration_instruments[self.calibration_instruments['Tenor'] >= 1])) :

            zr_init_guess.append(y)

            y = y + inc

        return zr_init_guess

    # small zr to expanded zr  -- inside your error function
    # add other tenor zr values | keep in mind the the place
    def expand_zr (self, zr_small) :

        y = []

        zr_small_counter = 0

        for i in range(1, int(self.maxTenor + 1)) :
            
            if i in self.calibration_instruments[self.calibration_instruments['Tenor'] >= 1]['Tenor'].to_list() :

                y.append(zr_small[zr_small_counter])
                zr_small_counter += 1

            else :
                y.append(0)

        return y
            

    # -- zr to dict || we have

    # -- dict to interpolated || we have 

    # optimizer o/p (small zr) to dictionary
    # small zr has all i/p corresponding to calib instr tenors
    def smallzr_dic (self, small_zr) :

        tenor_zr_dict = dict(zip(self.calibration_instruments[self.calibration_instruments['Tenor'] >= 1]['Tenor'].to_list(), small_zr))

        return tenor_zr_dict

    # dictionary to linear interpolation || we have
    


    # create tenor_zr dictionary from zr
    def create_tenorzr_dict (self, zr) :
        '''
        Inputs
        zr : list
        zero rates (annual) for all Tenors from 1yr to self.maxTenor

        Output
        tenor_zr_dict : dictionary
        * only tenor > 1 Yr and corresponding zero rates
        '''

        tenor_zr_dict = {}

        Tenorlist = self.calibration_instruments[self.calibration_instruments['Tenor'] >= 1]['Tenor'].to_list()  # list of all avaiable Tenors (> 1 Yr)

        for i in range(len(zr)) :  # in list zr, the index is tenor - 1

            tenor = i+1

            if tenor in Tenorlist :

                tenor_zr_dict[tenor] = zr[tenor-1]
        
        return tenor_zr_dict  


    # zero rate (with Linear Interpolation)
    def zero_rates (self, zero_rate_calibration_instruments) :

        '''
        Input:
        zero_rate_calibration_instruments : dictionary <Tenor : zr>
        * dictionary has tenor >= 1yr
        -----
        Output :
        zc : list
        Annual zr for Tenor 1 Yr to self.maxTenor
        '''
        zr = []     # function output 

        Tenorlist = list(zero_rate_calibration_instruments.keys())  # list of all avaiable Tenors >= 1yr
        ZRlist = list(zero_rate_calibration_instruments.values())  # list of all avaiable zr >= 1yr

        tenorlistcounter = 0  # last tenor in calibration instruments

        for tenor in range(1, int(self.maxTenor)+1) :

            if tenor in Tenorlist :
                y = zero_rate_calibration_instruments[tenor]   # zr for tenor in calibration - kept as is
                tenorlistcounter = tenorlistcounter + 1    # update last tenor in loop
            else:
                y = zero_rate_calibration_instruments[Tenorlist[tenorlistcounter-1]] + (zero_rate_calibration_instruments[Tenorlist[tenorlistcounter]] - zero_rate_calibration_instruments[Tenorlist[tenorlistcounter-1]]) * (tenor - Tenorlist[tenorlistcounter-1])   # # zr for tenor not in calibration - linear interpolate
            
            zr.append(y)

        return zr




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
    def pricing_error (self, zr_small_calbinstr_list) :

        error_total = 0     # cummulative error

        # For all instruments calculate PV_fixed - PV_float
        # { We get PV_fixed from calibration instruments and zc curve 
        # We get PV_float from fr curve }

        zr_ = self.expand_zr(zr_small_calbinstr_list)
        zrdict = self.create_tenorzr_dict(zr_)
        zr = self.zero_rates(zrdict)
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

        result = minimize(self.pricing_error, self.initial_guess_zr())  # pass error caluclating function and list of initial values for zr_calib_instr
        zr_opt_small = result.x
        zr_dict = self.smallzr_dic(zr_opt_small)
        self.zr = self.zero_rates(zr_dict)
        self.fr = self.forward_rates(self.zr)
        self.discountfactors = self.DiscountFactor(self.zr)


    # Yield curve observed from using pricing_error and fit, we see sharp jumps and falls - indicating too much fit to some instruments (assuming forward staes are stable)
    # We introduce some type of interpolation technique to calculate yield curve






        

        
    


    

