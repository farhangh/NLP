# -*- coding: utf-8 -*-
"""
Created on Thu March 11 2021

@author: M77100
"""

import os
import errno
import numpy as np
import pandas as pd
from os import path
from settings import hp
from itertools import chain
from functools import reduce
from collections import Counter
from flashtext import KeywordProcessor


def kwdProcess( ser, liste ) :
    """Function to extract the keywords from a description

    Parameters
    ----------
    ser : pandas serie
        column of the dtaframe containing the description
    liste : list
        list of keywords

    Returns
    -------
    ser2 : pandas seire
        list of extracted keywords

    """
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_list( liste )
    ser2 = ser.apply( keyword_processor.extract_keywords )
    return ser2



def excludeAntiPatts( df=pd.DataFrame, fname="liste_mots_clefs_a_exclure_generique.xlsx" ) :
    """Function to read the exclusion keywords and exlude the corresponding sirens

    Parameters
    ----------
    df : pandas dataframe
        data
    fname : str
        file path

    Returns
    -------
    df : pandas dataframe
        data with some siren excluded
    exc_list : list
        list of excluded sirens

    """
    try :
        if not path.isfile( fname ):
            raise FileNotFoundError( errno.ENOENT, os.strerror( errno.ENOENT ), fname )

        df_exc = pd.read_excel( fname )
        k_list = df_exc["Exclure les entreprises avec ces mots clefs"].tolist()

        dff = df.copy()
        dff["exc"] = kwdProcess( dff["oad_comment"], k_list ).apply( len )
        exc_list = dff[ dff["exc"]>0 ]["SIREN"].tolist()

        return df[ ~df["SIREN"].isin( exc_list ) ], exc_list

    except ValueError :
        raise ValueError("Weight file should have excel format.")


# model 1
def uniqueCount( df, theme_kw ) :
    """extract the keywords for each description and sum over unique extracted keywords

    Parameters
    ----------
    df : pandas dataframe
        data
    theme_kw : dict
        keywords and the corresponding thematics

    Returns
    -------
    df : pandas dataframe
        adds new columns to data

    """
    df["extracted_kw"] = kwdProcess( df["oad_comment"], list( theme_kw.keys() )).apply(Counter)

    df[ "inTheme" ] = df["extracted_kw"].apply( lambda ll :
                                    list(chain.from_iterable([ theme_kw[y] for y in ll if y in theme_kw.keys() ])) )
    #df["count_sum_unique"] = df["extracted_kw"].apply( lambda x : len( x.keys() ))
    df[ hp["col_uniqueCount"] ] = df["extracted_kw"].apply( lambda x : len( x.keys() ))
    df["keywords"] = df["extracted_kw"].apply( list )


    return df



# model 2
def countSum( df, X_Count) :
    """extract the keywords for each description and sum over extracted keywords ( kwd repeatition included)

    Parameters
    ----------
    df : pandas dataframe
        data
    X_Count : numpy array
        CountVectoriser matrix

    Returns
    -------
    df : pandas dataframe
        adds a new column to data

    """

    count_sum = X_Count.sum(axis=1)
    #df[ "count_sum"] = count_sum
    df[ hp["col_countSum"] ] = count_sum

    return df



w2list =lambda poid, kwd, col :  poid[ poid["keywords"].isin( kwd.keys() ) ][col].tolist()
""" reading the requested weight

Parameters
----------
poid : pandas dataframe
    weight dataframe
kwd : dict
    keywords list found in a description and their corresponding number of repeatitions
col : str
    requested weight column

Returns
-------
w2list : list
    list of wights

"""

def wsu( td, Poid, inColWeight, outColSum ) :
    """Sum over the wighted extracted keywords acoording to the requested weight type.

    Parameters
    ----------
    td : pandas dataframe
        data
    Poid : pandas dataframe
        weight dataframe
    inColWeight : str
        requested weight column
    outColSum : str
        column name for the weighted sum

    Returns
    -------
    td : pandas dataframe
        adds new columns to data

    """

    td[outColSum] = td[ "extracted_kw" ] \
        .apply( lambda kw_d : reduce( lambda x,y : x+y,
                                     w2list( Poid, kw_d, inColWeight) if len(w2list( Poid, kw_d, inColWeight))>0 else [0]
                                    )
              )
    return td



# model 3
def countUniqueFw( df, Poid ) :
    """Weighs the unique keywords by greens frequency and sum over.

    Parameters
    ----------
    df : pandas dataframe
        data
    Poid : pandas dataframe
        weight data frame

    Returns
    -------
    df : pandas dataframe
        adds new columns to data

    """
#    df = wsu( df, Poid, "fw_1", "count_unique_fw" )
    df = wsu( df, Poid, "fw_1", hp["col_countUniqueFw"] )


    return df



# model 4
def countUniqueRw( df, Poid ) :
    """Weighs the unique keywords by greens to non-greens frequency ratio and sum over.

    Parameters
    ----------
    df : pandas dataframe
        data
    Poid : pandas dataframe
        weight data frame

    Returns
    -------
    df : pandas dataframe
        adds new columns to data

    """
#    df = wsu( df, Poid, "rw", "count_unique_rw" )
    df = wsu( df, Poid, "rw", hp["col_countUniqueRw"] )
    return df



# model 5
# sum count weihgted by greens frequency
def countFw1( df, X_Count, Poid ) :
    """Weighs the keywords (repeatition included) by greens frequency and sum over.

    Parameters
    ----------
    df : pandas dataframe
        data
    X_Count : numpy array
        CountVectoriser matrix
    Poid : pandas dataframe
        weight data frame

    Returns
    -------
    df : pandas dataframe
        adds new columns to data

    """

    Weights_fw1 = np.array( Poid["fw_1"] ).reshape(-1,1)
    count_fw1 = X_Count.dot( Weights_fw1 ).ravel()
#    df["count_fw"] = count_fw1
    df[ hp["col_count_fw"] ] = count_fw1

    return df


# model 6
# sum count weihgted by greens to non-greens frequency ratio
def countRw( df, X_Count, Poid ) :
    """Weighs the keywords (repeatition included) by greens to non-greens frequency ratio and sum over.

    Parameters
    ----------
    df : pandas dataframe
        data
    X_Count : numpy array
        CountVectoriser matrix
    Poid : pandas dataframe
        weight data frame

    Returns
    -------
    df : pandas dataframe
        adds new columns to data

    """

    Weights_rw = np.array( Poid["rw"] ).reshape(-1,1)
    count_rw = X_Count.dot( Weights_rw ).ravel()
#    df["count_rw"] = count_rw
    df[ hp["col_count_rw"] ] = count_rw

    return df



def fitModels( df, Theme_kw, X_Count, Poid ) :
    """Fits all the 6 models to the data

    Parameters
    ----------
    df : pandas dataframe
        data
    Theme_kw : dict
        keywords and their corresponding thematics
    X_Count : numpy array
        CountVectoriser matrix
    Poid : pandas dataframe
        weight data frame

    Returns
    -------
    df : pandas dataframe
        data with extracted and summed over keywords

    """
    # counting the unique keywords and adding corresponding themes (model 1)
    df = uniqueCount( df, Theme_kw )
    # some on all word counts and ferequencies for a given description (model 2)
    df = countSum( df, X_Count)
    # unique sum count weihgted by greens frequency (model 3)
    df = countUniqueFw( df, Poid )
    # unique sum count weihgted by greens frequency ratio (model 4)
    df = countUniqueRw( df, Poid )
    # sum count weihgted by greens frequency  (model 5)
    df = countFw1( df, X_Count, Poid )
    # sum count weihgted by greens to non-greens frequency ratioy  (model 6)
    df = countRw( df, X_Count, Poid )

    return df
