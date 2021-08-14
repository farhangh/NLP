# -*- coding: utf-8 -*-
"""
Created on Thu March 11 2021

@author: M77100
"""

import os
import sys
import json
import errno
from os import path
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score


def computeClassAtt( y_true, y_pred, method="---" ) :
    """Function to give the goodness of classification ( scores, precisions and etc)

    Parameters
    ----------
    y_true : numpy array
        true labels
    y_pred : numpy array
        predicted labels
    method : str
        model name or explanation

    Returns
    -------
    classification accuracy and precision per class : pd.DataFrame

    """

    acc = round( accuracy_score( y_true, y_pred ), 2 )

    M = confusion_matrix( y_true, y_pred )
    print( "Confusion Matrix for ", method, ":\n", M)

    GT_acc =  round( M[1,1] / (M[1,0]+M[1,1]), 2 )
    nGT_acc = round( M[0,0] / (M[0,1]+M[0,0]),2 )

    GT_prec = round( precision_score( y_true, y_pred ),2 )
    nGT_prec = round( precision_score( y_true, y_pred,  pos_label=0 ), 2 )

    return pd.DataFrame( {"method":method, "overal_accuracy":[acc], "GT_accuracy":[GT_acc], "GT_precision":[GT_prec],
                         "nonGT_accuracy":[nGT_acc], "nonGT_precision":[nGT_prec] })



def predict( df, inpCol, predCol, seuil=0.  ) :
    """ Function to compute the predicted label for a given count method

    Parameters
    ----------
    df : pd.DataFrame

    inpCol : str
        column name including the count sum
    predCol : str
        column name for predicted labels
    seuil : float
        threshold on count sum to compute the prediction lables

    Returns
    -------
    dataframe with predicted column added : pd.DataFrame

    """

    df[ predCol ] = 0
    df.loc[ df[ inpCol ] > seuil, predCol ] = 1
    return df


def computeMatchInfo( df, inpCol, predCol, true_label="label", method="---", seuil=0. ) :
    """ Compute the predicted label for a given method as well as the goodness of the classification

    Parameters
    ----------
    df : pd.DataFrame

    inpCol : str
        column name including the count sum
    predCol : str
        column name including the predicted labels
    true_label : str
        column name including the true labels
    method : str
        model name or explanation
    seuil : float
        threshold on count sum to compute the prediction lables

    Returns
    -------
    dataframe with predicted column added : pd.DataFrame

    """
    df_data = predict( df, inpCol, predCol, seuil=seuil )
    df_ca = computeClassAtt( df_data[true_label], df_data[predCol], method )
    df_ca["threshold"] = seuil

    return df_data, df_ca


def readKeywordsTheme( fname ) :
    """Function to read the json file including the keywords and corresponding thematics

    Parameters
    ----------
    fname : str
        file path

    Returns
    -------
    keywords and corresponding thematics : dict

    """
    try :
        if not path.isfile( fname ):
            raise FileNotFoundError( errno.ENOENT, os.strerror( errno.ENOENT ), fname )

        with open(fname, "r") as f:
            theme_kw = json.load( f )

        return theme_kw

    except UnicodeDecodeError :
        raise ValueError ( fname, "file should have json format.")



def computeWordMatrix( Docs, Keywords ) :
    """Applying CountVectorizer on description for given keywords

    Parameters
    ----------
    Docs : list of str
        descriptions
    Keywords : list of str
        vocabularies

    Returns
    -------
    Words count matrix : numpy array

    """

    w2vec_count = CountVectorizer( ngram_range=(1, 4), vocabulary=Keywords )
    X_Count = w2vec_count.fit_transform( Docs )

    return X_Count


def readWeights( fname="./weightsAllConfirmed.xlsx", sheet_name="frequency-ratio weights" ) :
    """Reading the excel file contains the keywords weights

    Parameters
    ----------
    fname : str
        path to the weight excel file
    sheet_name : str
        corresponding sheet name

    Returns
    -------
    dataframe : pandas dataframe

    """
    try :
        dff = pd.read_excel( fname, sheet_name=sheet_name )
    except ValueError :
        raise ValueError("Weight file should have excel format.")

    return dff



def normData( df, inSirenName="./siren_in.csv", gtName="./Greentech_All_VF4_green.xlsx", gt_sheet_name="FICHIER COMPLET" ) :
    """Including only the relevant SIRENs and excluding the already known GTs.

    Parameters
    ----------
    df : pandas dataframe
        data
    inSirenName : str
        path to the csv file including the authorized sirens to analysis
    gtName : str
        GreenTech excel file
    gt_sheet_name : str
        corresponding sheet name for the GreenTechs

    Returns
    -------
    df : pandas dataframe
        filtered data

    """
    sirens_g = pd.read_excel( gtName, gt_sheet_name)["SIREN"].tolist()
    print( "Number of known GreenTechs:", len(sirens_g))

    sirens = pd.read_csv( inSirenName )["siren"].tolist()
    print("Number of whole eligible companies:", len(sirens))

    return df[ ( df["SIREN"].isin( sirens ) ) & ( ~df["SIREN"].isin( sirens_g ) ) ]


def uniqueKwdTheme( theme_kw ) :
    """Extracting the keywords with only one thematic

    Parameters
    ----------
    theme_kw : dict
        keywords and their corresponding thematics

    Returns
    -------
    ukt : dict
        keywords with only one thematic

    """
    return { k : theme_kw[k][0] for k in theme_kw if len( theme_kw[k] )==1 }

def giveTheme( row ) :
    """Theme selection from keywwords

    Parameters
    ----------
    row : list
        themes and keywords

    Returns
    -------
    theme : str
        the most probable theme

    """
    themeCount = Counter( row[0] )
    lenKw = len( row[1] )
    theme = ""
    for k in themeCount :
        if themeCount[k] ==  lenKw :
            theme = k
    return theme


def extractGTs( Preds, df, theme_kw ) :
    """Extracting the description of the GT candidates from the initial data

    Parameters
    ----------
    Preds : pandas dataframe
        stacked prediction
    df : pandas dataframe
        data
    theme_kw : dict
        keywords and their corresponding thematics

    Returns
    -------
    dfgt : pandas dataframe
        sirens for GreeTech candidates with corresponding keywords

    """
    ukt = uniqueKwdTheme( theme_kw ) # keys : kwd, value : unique corresponding theme

    sirens_gt = Preds[ Preds["is_GT"]==1 ]["SIREN"].tolist()
    df_selected_cols = ["SIREN", "oad_comment", "extracted_kw", "inTheme"]
    cols = df_selected_cols + ["isPG"] if "isPG" in df.columns else df_selected_cols
    dfgt = df[ df.SIREN.isin( sirens_gt ) ][ cols ]
    dfgt["matched_keywords"] = dfgt["extracted_kw"].apply( lambda x : sorted(list(x.keys())) )

    #dfgt[ "inTheme_maximal" ] = dfgt[ "inTheme" ].apply( Counter ).apply( lambda d : [ k for k in d if d[k]>1 ] )
    #dfgt[ "inTheme_minimal" ] = dfgt[ "keywords" ].apply( lambda x : [ ukt[k] for k in x if k in list(ukt)  ]  )
    #dfgt[ "themeP"] = dfgt[ "inTheme_maximal" ] +  dfgt[ "inTheme_minimal" ]
    #dfgt[ "themeP"] = dfgt[ "themeP"].apply( lambda x : list( set(x) )  )

    dfgt[ "sector" ] = dfgt[ ["inTheme", "matched_keywords"] ].apply( giveTheme, axis=1 )

    dfgt.reset_index(inplace=True)
    dfgt = dfgt.drop(columns=["extracted_kw", "index", "inTheme"])
    #dfgt = dfgt.drop(columns=["extracted_kw", "index", "inTheme", "inTheme_maximal", "inTheme_minimal"])

    return dfgt


def flatten( liste ) :
    """flatten a list containing sub-lists

    Parameters
    ----------
    liste : list
        list with sub-lists

    Returns
    -------
    a flatten list : list

    """
    return list(set([ e for sublist in liste for e in sublist ]))
    # TODO :
    # more efficient to use
    # import itertools
    # list(itertools.chain(*list2d))
