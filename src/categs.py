# -*- coding: utf-8 -*-
"""
Created on Thu March 11 2021

@author: M77100
"""

import time
import numpy as np
import pandas as pd
from scipy import stats
from models import fitModels
from settings import hp, ppd
from datetime import datetime
from tools import readKeywordsTheme, computeWordMatrix, readWeights, predict



def countAll( df, fKeywords="./all_thematicKW.json", fWeights="./weightsAllConfirmed.xlsx",
             w_sheet_name="frequency-ratio weights" ) :

    """Reads the keywords and weights data to fit all models to tha main data

    Parameters
    ----------
    df : pandas dataframe
        initial main data
    fKeywords : str
        json file to read keywords and their corresponding thematics
    fWeights : str
        excel file to read the weights
    w_sheet_name : str
        corrsponding sheet name for the weight data file

    Returns
    -------
    df : pandas dataframe
        data with extracted and summed over keywords

    """
    # reading keywords list
    theme_kw = readKeywordsTheme( fKeywords )

    # computing the word matrix
    X_count = computeWordMatrix( Docs=df.oad_comment.tolist(), Keywords=list( theme_kw.keys() ) )

    # Reading the weights
    poid = readWeights(fWeights, w_sheet_name)

    df = fitModels( df, theme_kw, X_count, poid )

    return df, theme_kw


def computeMeanSum( df, cols ) :
    """Compute the average value of each model over all sirens

    Parameters
    ----------
    df : pandas dataframe
         data
    cols : list
        list of columns including the models

    Returns
    -------
    sum_mean : dict
        model name and the corresponding mean value
    sum_mean_list : list
        list of mean values

    """
    model_cols = [ x[0] for x in cols ]
    sum_mean = { x : stats.describe( df[x] ).mean for x in model_cols }
    sum_mean_list = [ sum_mean[k] for k in sum_mean ]

    return sum_mean, sum_mean_list


def predictAll( df, n_min=5, fPG=1.46 ) :
    """Makes prediction for the different sum models.

    Parameters
    ----------
    df : pandas dataframe
         data
    n_min : int
        minimum number of unique keywords as a GT threshold
    fPG : float
        potentially-GT factor increases the probabiliry of being a GT.

    Returns
    -------
    df : pandas dataframe
        data with predictions for each sum model
    sum_mean : dict
        model name and the corresponding mean value

    """
    # TODO : replace french variable by english (done)
    # TODO : make the list of models dynamic and define in main or into the global params file ( done )
    cols = [ ( hp["col_uniqueCount"],  hp["col_count_unique_pred"] ), ( hp["col_countSum"],  hp["col_count_pred"]),
             ( hp["col_countUniqueFw"], hp["col_unique_fw_pred"] ), ( hp["col_countUniqueRw"], hp["col_unique_rw_pred"] ),
             ( hp["col_count_fw"], hp["col_fw_pred"] ), ( hp["col_count_rw"], hp["col_rw_pred"] )
             ]

    mean_sum, sum_mean_list  = computeMeanSum( df, cols )
    threshold_fac = n_min*1. / mean_sum[ hp["col_uniqueCount"] ]

    for i in range( len(cols) ) :
        if "isPG" in df.columns :
            df.loc[ df["isPG"]==True, cols[i][0] ] *= fPG
        df = predict( df, cols[i][0],  cols[i][1], seuil=sum_mean_list[i]*threshold_fac  )

    return df, mean_sum



def stackAll( df, cols, hmgn=False ) :
    """Stack all predictions through average method.

    Parameters
    ----------
    df : pandas dataframe
        initial main data
    cols : list
        list of prediction columns to be stacked

    Returns
    -------
    df : pandas dataframe
        adds the stacked prediction label

    """
    #FIX : can be risky to remove the first columns, could be better to use del df['siren] or df.drop(['siren'], axis = 1) (done)

    pred_cols = [ c for c in cols ]

    if "SIREN" in pred_cols :
        pred_cols.remove( "SIREN" )
    elif "siren" in pred_cols :
        pred_cols.remove( "siren" )


    poid_pred_dict = ppd

    # for equal contribution
    if hmgn :
        poid_pred_dict = { k : 1./len(poid_pred_dict) for k in poid_pred_dict }

    poid_pred = np.array( [ poid_pred_dict[k] for k in pred_cols ] )
    poid_pred = poid_pred / poid_pred.sum()

    Preds = df[ cols ].copy()
    Preds[ "proba_pred" ] = Preds[ pred_cols ].apply( lambda r : round( np.array(r).dot(poid_pred), 2), axis=1 )
    Preds[ "is_GT" ] = Preds[ "proba_pred" ].apply( lambda x : 0 if x<.5 else 1 )

    return Preds



def buildOutputInference(df, mapping_out):
    """
    Function to build output inference file following mapping
    """

    df = df.rename(mapping_out)
    df = df[list(mapping_out.values)]
    df['created_at'] = datetime.now()
    df['execId'] = str(int(time.time()))

    #merge with SIRENE/INSEE
    print('merge with SIRENE info')
    df_insee = pd.read_csv(hp.autorized_sirens)
    df_res_insee = df.merge(
        df_insee[['siren', 'denominationUniteLegale', 'activitePrincipaleUniteLegale', 'dateCreationUniteLegale']],
        left_on="SIREN", right_on="siren", how="left")
    del df_insee

    #merge with sidetrade
    print('merge with ext description')
    df_ext_desc = pd.read_csv(hp.ext_descriptions)
    df_res_insee_desc = df_res_insee.merge(
        df_ext_desc[['description','SIREN']],
        left_on="SIREN",right_on="SIREN",how="left")
    del df_ext_desc

    return df_res_insee_desc
