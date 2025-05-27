# Objective : fetchdata from folder /InteretsRateCurves/data/

# import libraries
import pandas as pd

# function to fetch data in MS Excel (.csv or .xlsx format)
def fetchxldata(xl_filename) :
    '''
    ------
    Inputs :

    xl_filename : str
    name of the MS Excel (.xlsx or .csv) file in /InteretsRateCurves/data/

    Output :
    df : pandas.DataFrame
    .xlsx or .csv converted to pandas.DataFrame
    ------

    '''

    # check filetype of file
    if xl_filename[-4:] == str('xlsx') :
        df = pd.read_excel(f'{xl_filename}')
    elif xl_filename[-3:] == str('csv') :
        df = pd.read_csv(f'{xl_filename}')
    else :
        print('Incorrect format or filetype not included in name')

    return df


# clean df generated from bbg file

def clean_bbg_df (df) :
    '''
    ------
    Inputs :

    df : pandas.DataFrame
    BBG df generated from function fetchxldata()

    Output :
    df_clean : pandas.DataFrame
    cleaned pandas.DataFrame obj 
    ------

    '''
    # columns 
    Tenor = []
    Descript = []
    Swap_parrate = []

    # lambda function to convert Tenor in bbg file to ACT/360
    daycount_ACTby360 = lambda time_unit : 7/360 if time_unit == 'W' else 30/360 if time_unit == 'M' else 1

    # loop through each row, change col Tenor, keep Description, Convert col Yield to %age, drop rest
    for index, row in df.iterrows() :
        Tenor.append(float(row['Tenor'][:-1]) * daycount_ACTby360(str(row['Tenor'][-1:])))
        Descript.append(str(row['Description']))
        Swap_parrate.append(float(row['Yield'])/100)

    # create clean_df
    clean_dict = {'Tenor' : Tenor, 'Description' : Descript , 'Par rate' : Swap_parrate }
    clean_df = pd.DataFrame(clean_dict)

    return clean_df
    