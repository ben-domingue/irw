*** This Do File creates tables from the Psychometric properties of the polish updated Illinois rape myth acceptance scale study 2 ***

* clear
clear

* import study 2 dataset and convert to cvs
import spss using "study2 stability.sav", clear
export delimited "rape_2.csv", replace

* generate any needed variables from study 1; cov_subsample
gen cov_subsample = 2
label define subsamplelbl 1 "Internet" 2 "Paper-Pencil"
label values cov_subsample subsamplelbl

* renames covariates
rename field cov_field
rename gender cov_gender
rename age cov_age
rename field_cat cov_field_cat

* drop unnecessary variables
drop _v1
drop nr_part
drop rma_sum_1_1
drop rma_sum_1_2
drop rma_sum_2_1
drop rma_sum_2_2
drop rma_sum_3_1
drop rma_sum_3_2
drop rma_sum_4_1
drop rma_sum_4_2
drop rma_sum_5_1
drop rma_sum_5_2

* rename responses as needed; cov_field
label define fieldlbl 1 "Internet Sample" 2 "Material Engineering" 3 "Medicine (before classes on violence)" 5 "Psychology (1st year)" 6 "Philosophy" 7 "History" 8 "Law" 9 "Russian Philology" 10 "Pedagogy" 11 "Chemistry" 12 "Applied Linguistics", replace
label values cov_field fieldlbl

* rename responses as needed; cov_field_cat
label define field_catlbl 1 "Human" 2 "Social" 3 "Medical" 4 "STEM"
label values cov_field_cat field_catlbl

* adds id
gen id = _n

* reorder variables
order id cov_field cov_subsample cov_field_cat cov_gender cov_age, first

* renames pre_rma to rma_pre for simplicity and consistency later on
forvalues i = 1/19 { 
    rename pre_rma`i' rma_pre`i' 
}

* save cleaned dataset
save "rape_2.csv", replace

* creates long data from wide data
local question_cols rma_pre1 rma_pre2 rma_pre3 rma_pre4 rma_pre5 rma_pre6 rma_pre7 rma_pre8 rma_pre9 rma_pre10 rma_pre11 rma_pre12 rma_pre13 rma_pre14 rma_pre15 rma_pre16 rma_pre17 rma_pre18 rma_pre19 rma1 rma2 rma3 rma4 rma5 rma6 rma7 rma8 rma9 rma10 rma11 rma12 rma13 rma14 rma15 rma16 rma17 rma18 rma19 rma_sa_1_1 rma_mt_1_1 rma_nr_1_1 rma_sl_1_1 rma_sa_1_2 rma_mt_1_2 rma_nr_1_2 rma_sl_1_2 rma_sa_2_1 rma_mt_2_1 rma_nr_2_1 rma_sl_2_1 rma_sa_2_2 rma_mt_2_2 rma_nr_2_2 rma_sl_2_2 rma_sa_3_1 rma_mt_3_1 rma_nr_3_1 rma_sl_3_1 rma_sa_3_2 rma_mt_3_2 rma_nr_3_2 rma_sl_3_2 rma_sa_4_1 rma_mt_4_1 rma_nr_4_1 rma_sl_4_1 rma_sa_4_2 rma_mt_4_2 rma_nr_4_2 rma_sl_4_2 rma_sa_5_1 rma_mt_5_1 rma_alk_5_1 rma_nr_5_1 rma_sa_5_2 rma_mt_5_2 rma_alk_5_2 rma_nr_5_2 rma_sl_5_2 rma_sl_5_1 rma_alk_4_1 rma_alk_4_2 rma_alk_5a_2 rma_alk_5a_1

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

drop rma_pre1 rma_pre2 rma_pre3 rma_pre4 rma_pre5 rma_pre6 rma_pre7 rma_pre8 rma_pre9 rma_pre10 rma_pre11 rma_pre12 rma_pre13 rma_pre14 rma_pre15 rma_pre16 rma_pre17 rma_pre18 rma_pre19 rma1 rma2 rma3 rma4 rma5 rma6 rma7 rma8 rma9 rma10 rma11 rma12 rma13 rma14 rma15 rma16 rma17 rma18 rma19 rma_sa_1_1 rma_mt_1_1 rma_nr_1_1 rma_sl_1_1 rma_sa_1_2 rma_mt_1_2 rma_nr_1_2 rma_sl_1_2 rma_sa_2_1 rma_mt_2_1 rma_nr_2_1 rma_sl_2_1 rma_sa_2_2 rma_mt_2_2 rma_nr_2_2 rma_sl_2_2 rma_sa_3_1 rma_mt_3_1 rma_nr_3_1 rma_sl_3_1 rma_sa_3_2 rma_mt_3_2 rma_nr_3_2 rma_sl_3_2 rma_sa_4_1 rma_mt_4_1 rma_nr_4_1 rma_sl_4_1 rma_sa_4_2 rma_mt_4_2 rma_nr_4_2 rma_sl_4_2 rma_sa_5_1 rma_mt_5_1 rma_alk_5_1 rma_nr_5_1 rma_sa_5_2 rma_mt_5_2 rma_alk_5_2 rma_nr_5_2 rma_sl_5_2 rma_sl_5_1 rma_alk_4_1 rma_alk_4_2 rma_alk_5a_2 rma_alk_5a_1

drop if missing(item) | item == ""

* encode any needed variables
gen cov_age2 = cov_age
drop cov_age
rename cov_age2 cov_age
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov_field cov_subsample cov_field_cat cov_gender cov_age, first

* save cleaned dataset
save "rape_2.csv", replace

* create subset of tables
local base_items rma rma_pre rma_sa rma_mt rma_nr rma_sl rma_alk
foreach prefix of local base_items {
    preserve
    if inlist("`prefix'", "rma", "rma_pre") {
        keep if regexm(item, "^`prefix'[0-9]")
    }
    else {
        keep if regexm(item, "^`prefix'_")
    }
    export delimited using "lys_2020_rape_2_`prefix'.csv", replace
    restore
}