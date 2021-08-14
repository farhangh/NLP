
# list of hyper parameters
hp = { "data" : "../data/raw/input/projetOADcomments.parquet",  # the main data including the sirens and the descriptions
       "ext_descriptions":"../data/raw/input/sidetrade.csv", # ext descritpion for companies from sidetrade provider
       "authorized_sirens" : "../data/authorized_sirens.csv", # list of authosides sirens
       "GTs" : "../data/all_known_greentech.xlsx", # list of already known GreenTechs
       "GTs_sheet" : "FICHIER COMPLET", # corresponding sheet name
       "kwd_exclude" : "../data/keywords_for_exclude_candidate.xlsx", # keywords to exclude the sorens
       "kwd" : "../data/sector_keywords.json", # keywords for GreenTechs
       "weights" : "../data/keyword_weights.xlsx", # list of weights to enhance the GreenTech detection
       "w_sheet" : "frequency-ratio weights", # corresponding sheet name

       "n_kwd_min" : 3, # minimum number of keywords for a siren to be detected as GreenTech : threshold > n_kwd_min
       "fPG" : 1.46, # factor to enhance the detection for sirens mentioned as potentially GreenTech in the main data


       #"candidates_out" : "./GT_candidates_s6.xlsx",
       "candidates_out" : "../data/raw/output/candidates.xlsx", #final candidate list
       "cand_sheet" : "GreenTech candidates", # corresponding sheet name

       # models :
       "col_uniqueCount" : "count_sum_unique", # column name for unique keyword count model
       "col_countSum" : "count_sum", # column name for keyword count model
       "col_countUniqueFw" : "count_unique_fw", # column name for unique keyword count weighted by GreenTech frequencies
       "col_countUniqueRw" : "count_unique_rw", # column name for unique keyword count weighted by GreenTech to non-GrrenTech frequency ratio
       "col_count_fw" : "count_fw", # column name for keyword count weighted by GreenTech frequencies
       "col_count_rw" : "count_rw", # column name for keyword count weighted by GreenTech to non-GrrenTech frequency ratio

        # predictions column name for each model :
       "col_count_unique_pred" : "count_unique_pred",
       "col_count_pred" : "count_pred",
       "col_unique_fw_pred" : "c_unique_fw_pred",
       "col_unique_rw_pred" : "c_unique_rw_pred",
       "col_fw_pred" : "c_fw_pred",
       "col_rw_pred" : "c_rw_pred",

       # prediction columns selected for stackiing
       #"pred_cols" : [ "SIREN", "count_unique_pred", "count_pred", "c_unique_fw_pred", "c_unique_rw_pred", "c_fw_pred", "c_rw_pred"  ]
       "pred_cols": ["SIREN", "count_unique_pred"]

}


# weights to stack different models
ppd = { hp["col_count_unique_pred"] : 0.5,
        hp["col_count_pred"] : 0.2,
        hp["col_unique_fw_pred"] : 0.05,
        hp["col_unique_rw_pred"] : 0.1,
        hp["col_fw_pred"] : 0.05,
        hp["col_rw_pred"] : 0.1
      }
