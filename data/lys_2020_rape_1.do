*** This Do File creates tables from the Psychometric properties of the polish updated Illinois rape myth acceptance scale study 1 ***

* clear
clear

* import study 1 dataset and convert to cvs
import spss using "study1 reliability and factor analysis.sav", clear
export delimited "rape_1.csv", replace

* renames covariates
rename field cov_field
rename gender cov_gender
rename age cov_age
rename subsample cov_subsample
rename field_cat cov_field_cat

* drop unnecessary variables
drop rma_sum

* rename responses as needed; cov_gender
label define genderlbl 1 "Male" 2 "Female"
label values cov_gender genderlbl

* rename responses as needed; cov_field
label define fieldlbl 1 "Internet Sample" 2 "Material Engineering" 3 "Medicine (before classes on violence)" 5 "Psychology (1st year)" 6 "Philosophy" 7 "History" 8 "Law" 9 "Russian Philology" 10 "Pedagogy" 11 "Chemistry" 12 "Applied Linguistics", replace
label values cov_field fieldlbl

* rename responses as needed; cov_subsample
label define subsamplelbl 1 "Internet" 2 "Paper-Pencil"
label values cov_subsample subsamplelbl

* rename responses as needed; cov_field_cat
label define field_catlbl 1 "Human" 2 "Social" 3 "Medical" 4 "STEM"
label values cov_field_cat field_catlbl

* adds id
gen id = _n

* reorder variables
order id cov_field cov_subsample cov_field_cat cov_gender cov_age, first

* save cleaned dataset
save "rape_1.csv", replace

* creates long data from wide data
local question_cols rma1	rma2	rma3	rma4	rma5	rma6	rma7	rma8	rma9	rma10	rma11	rma12	rma13	rma14	rma15	rma16	rma17	rma18	rma19

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop rma1	rma2	rma3	rma4	rma5	rma6	rma7	rma8	rma9	rma10	rma11	rma12	rma13	rma14	rma15	rma16	rma17	rma18	rma19

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov_field cov_subsample cov_field_cat cov_gender cov_age, first

* saves final dataset
export delimited using "lys_2020_rape_1.csv", replace