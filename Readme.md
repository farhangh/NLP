#Greentech matching

####Procédure
1. Requêter les données
        i.  Nouveaux projets crées dans l'OAD depuis la table GDC<TASDOS
        ii. Requeter les commentaires de validation et de décision à partir de la table GDC<VAOS_VALIDATION_OAD_SDC
        iii. Table BCP<TBSIGRA pour obtenir les SIREN
2. Lancer le script de consolidation des projets OAD (OADProjectsBuider.py)
3. Construire la liste de SIREN qui entre dans le périmètre:
        i. Télécharger la derniere version de la base SIRENE
        ii. Executer le script INSEE_builder.py
4. Lancer le script main.py permettant de calculer les candidats GT

 
 ####Requete des projets ouverts dans l'OAD
 ##### Requete permettant d'extraire les dossier crée dans l'OAD à partir d'une date 

**Attention à changer la date ici '01/01/2021** 

`SELECT NUMERA,DCRENR,CNUPRJ, PFCFAP, PFCCAP,PFCPRO,CINTRL,PFCSTA,C_SS_SECTEUR_GICS FROM GDC.TEASSDOS WHERE DCRENR > TO_DATE ('01/01/2021')`

##### Requeter les SIREN pour les NUMERA dans BCP 
`SELECT DISTINCT NUMERA, NSIREN FROM BCP.TBLSIGRA`

##### Requeter les commentaire de décision et de validation

`SELECT VAOS_COMMENTAIRE_VALIDATION, CNUPRJ, VAOS_DATE_VALIDATION_OAD_SDC FROM GDC.VAOS_VALIDATION_OAD_SDC WHERE VAOS_DATE_VALIDATION_OAD_SDC >TO_DATE ('01/01/2021')`

`SELECT CPRO_COMMENTAIRE_DECISION, CNUPRJ, CPRO_DCRENR FROM GDC.CPRO_CARACTERISTIQUE_PROJET WHERE CPRO_DCRENR >TO_DATE ('01/01/2021')`


 ####Running the main program
All hyper parameters should be firstly tuned in the settings.py.
This includes all input files and the output file name. 
It is also possible to change the column names for different 
models. The weights to stack the models' predictions should be 
given in settings as well. You can find the description of all 
keys in the settings.py.

#####model 1
Extracting the keywords for each description and sum over unique 
extracted keywords, corresponding column : "col_uniqueCount".

#####model 2
Extracting the keywords for each description and sum over 
extracted keywords (i.t. keyword repeatition included), corrsponding
column : "col_countSum".

#####model 3
Sum over the unique extracted keywords which are weighed by 
their frequencies as appear in the reference GreenTech 
descriptions, corresponding column : "col_countUniqueFw".

#####model 4
Sum over the unique extracted keywords which are weighed by 
their ratio of GreenTech frequency to non-GreenTech frequency,
corresponding column : "col_countUniqueRw".

#####model 5
Similar to model 2 with the keywords weighed by 
their frequencies as appear in the reference GreenTech 
descriptions, corresponding column : "col_count_fw".

#####model 6
Similar to model 2 with keywords weighed by 
their ratio of GreenTech frequency to non-GreenTech frequency,
corresponding column : "col_count_rw".
