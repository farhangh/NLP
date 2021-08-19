#Running the main program
All hyper parameters should be firstly tuned in the settings.py.
This includes all input files and the output file name. 
It is also possible to change the column names for different 
models. The weights to stack the models' predictions should be 
given in settings as well. You can find the description of all 
keys in the settings.py.

#model 1
Extracting the keywords for each description and sum over unique 
extracted keywords, corresponding column : "col_uniqueCount".

#model 2
Extracting the keywords for each description and sum over 
extracted keywords (i.t. keyword repeatition included), corrsponding
column : "col_countSum".

#model 3
Sum over the unique extracted keywords which are weighed by 
their frequencies as appear in the reference GreenTech 
descriptions, corresponding column : "col_countUniqueFw".

#model 4
Sum over the unique extracted keywords which are weighed by 
their ratio of GreenTech frequency to non-GreenTech frequency,
corresponding column : "col_countUniqueRw".

#model 5
Similar to model 2 with the keywords weighed by 
their frequencies as appear in the reference GreenTech 
descriptions, corresponding column : "col_count_fw".

#model 6
Similar to model 2 with keywords weighed by 
their ratio of GreenTech frequency to non-GreenTech frequency,
corresponding column : "col_count_rw".
