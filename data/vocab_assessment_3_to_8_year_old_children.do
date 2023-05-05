* Source: https://psyarxiv.com/4z86w/
* License: CC-By Attribution 4.0 International 

clear all 
set more off
version 17.0 

import delimited "clean_data.txt", clear
egen id = group(subjid)
ren (correct trial responsetime) (resp item rt) 
replace rt = rt/1000 

order id item resp
compress 
export delimited "vocab_assessment_3_to_8_year_old_children.csv", replace 
