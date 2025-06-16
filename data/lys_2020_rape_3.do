*** This Do File creates tables from the Psychometric properties of the polish updated Illinois rape myth acceptance scale study 3 ***

* clear
clear

* import study 3 dataset and convert to cvs
import spss using "study 3 validity.sav", clear
export delimited "rape_3.csv", replace

* generate any needed variables from study 2; cov_subsample
gen cov_subsample = 2
label define subsamplelbl 1 "Internet" 2 "Paper-Pencil"
label values cov_subsample subsamplelbl

* renames covariates
rename field cov_field
rename gender cov_gender
rename age cov_age
rename field_cat cov_field_cat

* drop unnecessary variables
drop unjust
drop sj
drop sds_sum
drop rwa_sum
drop sdo
drop rma_sum_4
drop rma_sum_5
drop nr_part
drop nr
drop _v1
drop hs
drop bs
drop cult_cons
drop ec_cons
drop diff_bio
drop diff_soc

* rename responses as needed; cov_gender
label define genderlbl 1 "Male" 2 "Female"
label values cov_gender genderlbl

* rename responses as needed; cov_field_cat
label define field_catlbl 1 "Human" 2 "Social" 3 "Medical" 4 "STEM"
label values cov_field_cat field_catlbl

* adds id
gen id = _n

* reorder variables
order id cov_field cov_subsample cov_field_cat cov_gender cov_age, first

* save cleaned dataset
save "rape_3.csv", replace

* creates long data from wide data
local question_cols asi1 asi2 asi3 asi4 asi5 asi6 asi7 asi8 asi9 asi10 asi11 asi12 asi13 asi14 asi15 asi16 asi17 asi18 asi19 asi20 asi21 asi22 cons1 cons2 cons3 cons4 cons5 cons6 cons7 cons8 cons9 cons10 cons11 cons12 cons13 cons14 cons15 cons16 cons17 cons18 cons19 cons20 diff1 diff2 diff3 diff4 diff5 diff6 diff7 diff8 diff9 diff10 diff11 diff12 diff13 kpnts2 kpnts3 kpnts5 kpnts7 kpnts8 kpnts10 kpnts11 kpnts13 kpnts14 kpnts16 kpnts17 kpnts19 kpnts20 kpnts22 kpnts23 kpnts24 rma1 rma2 rma3 rma4 rma5 rma6 rma7 rma8 rma9 rma10 rma11 rma12 rma13 rma14 rma15 rma16 rma17 rma18 rma19 rma_alk_4 rma_alk_5 rma_mt_4 rma_mt_5 rma_nr_4 rma_nr_5 rma_sa_4 rma_sa_5 rma_sl_4 rma_sl_5 rwa1 rwa2 rwa3 rwa4 rwa5 rwa6 rwa7 rwa8 rwa9 rwa10 rwa11 rwa12 sds1 sds2 sds3 sds4 sds5 sds6 sds7 sds8 sds9 sds10 sds11 sds12 sds13 sds14 sds15 sds16 sds17 sds18 sds19 sds20 sds21 sds22 sds23 sds24 sds25 sds26 sds27 sds28 sds29 sj1 sj2 sj3 sj4 sj5 sj6 sj7 sj8 unjust1 unjust2 unjust3 unjust4 unjust5 unjust6 unjust7 unjust8 unjust9 unjust10

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

drop asi1 asi2 asi3 asi4 asi5 asi6 asi7 asi8 asi9 asi10 asi11 asi12 asi13 asi14 asi15 asi16 asi17 asi18 asi19 asi20 asi21 asi22 cons1 cons2 cons3 cons4 cons5 cons6 cons7 cons8 cons9 cons10 cons11 cons12 cons13 cons14 cons15 cons16 cons17 cons18 cons19 cons20 diff1 diff2 diff3 diff4 diff5 diff6 diff7 diff8 diff9 diff10 diff11 diff12 diff13 kpnts2 kpnts3 kpnts5 kpnts7 kpnts8 kpnts10 kpnts11 kpnts13 kpnts14 kpnts16 kpnts17 kpnts19 kpnts20 kpnts22 kpnts23 kpnts24 rma1 rma2 rma3 rma4 rma5 rma6 rma7 rma8 rma9 rma10 rma11 rma12 rma13 rma14 rma15 rma16 rma17 rma18 rma19 rma_alk_4 rma_alk_5 rma_mt_4 rma_mt_5 rma_nr_4 rma_nr_5 rma_sa_4 rma_sa_5 rma_sl_4 rma_sl_5 rwa1 rwa2 rwa3 rwa4 rwa5 rwa6 rwa7 rwa8 rwa9 rwa10 rwa11 rwa12 sds1 sds2 sds3 sds4 sds5 sds6 sds7 sds8 sds9 sds10 sds11 sds12 sds13 sds14 sds15 sds16 sds17 sds18 sds19 sds20 sds21 sds22 sds23 sds24 sds25 sds26 sds27 sds28 sds29 sj1 sj2 sj3 sj4 sj5 sj6 sj7 sj8 unjust1 unjust2 unjust3 unjust4 unjust5 unjust6 unjust7 unjust8 unjust9 unjust10

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
save "rape_3.csv", replace

* create subset of tables
local base_items asi cons diff kpnts rma rma_alk rma_mt rma_nr rma_sa rma_sl rwa sds sj unjust
foreach prefix of local base_items {
    preserve
    if inlist("`prefix'", "asi", "cons", "diff", "kpnts", "rma", "rwa", "sds", "sj", "unjust") {
        keep if regexm(item, "^`prefix'[0-9]")
    }
    else {
        keep if regexm(item, "^`prefix'_")
    }
    export delimited using "lys_2020_rape_3_`prefix'.csv", replace
    restore
}