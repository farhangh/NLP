# -*- coding: utf-8 -*-
"""
Created on Thu March 11 2021

@author: M77100
"""
import pandas as pd
from time import time
from settings import hp
from models import excludeAntiPatts
from tools import normData, extractGTs
from categs import countAll, predictAll, stackAll, buildOutputInference

if __name__ == '__main__' :

    t0 = time()
    data = pd.read_parquet( hp["data"] )
    print( "Number of companies in the initial database:", len(data) )

    data = normData( data, hp["authorized_sirens"], hp["GTs"], hp["GTs_sheet"] )
    print( "Number of companies after excluding the known GTs and unauthorised sirens :", len(data) )

    data, siren_exc_list = excludeAntiPatts( data, hp["kwd_exclude"] )
    print( "Number of eligible companies after being excluded by anti-pattern keywords:", len(data) )

    data_initial = data.copy()


    print( "Applying the GT search models on the data ..." )
    data, theme_kw = countAll( data, fKeywords=hp["kwd"], fWeights=hp["weights"], w_sheet_name=hp["w_sheet"] )

    print( "Classifying with respect to the given thresholds ... " )
    data, sum_mean = predictAll( data, n_min=hp["n_kwd_min"], fPG=hp["fPG"] )

    print( "Labeling the companies ..." )
    preds = stackAll( data, hp["pred_cols"] )

    print( "Extracting the GreenTech candidates ..." )
    df_gt = extractGTs( preds, data, theme_kw )

    outName = hp["candidates_out"]
    print( "Saving the candidates in ", outName, "..." )
    #df_gt = buildOutputInference(df_gt,)
    df_gt.to_excel(outName, sheet_name=hp["cand_sheet"] )

    print( "Elapsed time :", round( (time()-t0)/60, 1) , "mins" )
