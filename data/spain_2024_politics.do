*** This Stata Do File processes the spain_2024_politics study (CIS 3490) ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2024_politics"

* import raw data (semicolon delimited, quote-wrapped plain variable names)

import delimited "3490_num.csv", delimiter(";") varnames(1) case(lower) encoding("UTF-8") clear

* destring

destring _all, replace force

* generate row id

gen long id = _n

* rename covariates (locked set: cov_sex, cov_age)

rename sexo cov_sex
rename edad cov_age

* clean covariates
* edad is true age (18 to 94 observed), no sentinel codes present

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

* save master

compress

save "spain_2024_politics_master.dta", replace

**# Bookmark 1: beliefs

* ============================================================
* beliefs (VALORES1_1 to VALORES1_5), 1-5 agreement scale
* code 3 is the unread (NO LEER) midpoint, recoded to missing
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols valores1_1 valores1_2 valores1_3 valores1_4 valores1_5

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace valores1_1 = . if inlist(valores1_1, 3, 8, 9)
replace valores1_2 = . if inlist(valores1_2, 3, 8, 9)
replace valores1_3 = . if inlist(valores1_3, 3, 8, 9)
replace valores1_4 = . if inlist(valores1_4, 3, 8, 9)
replace valores1_5 = . if inlist(valores1_5, 3, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_beliefs.csv", replace

**# Bookmark 2: values

* ============================================================
* values (VALORES2_1 to VALORES2_4), 1-5 agreement scale
* code 3 is the unread (NO LEER) midpoint, recoded to missing
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols valores2_1 valores2_2 valores2_3 valores2_4

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace valores2_1 = . if inlist(valores2_1, 3, 8, 9)
replace valores2_2 = . if inlist(valores2_2, 3, 8, 9)
replace valores2_3 = . if inlist(valores2_3, 3, 8, 9)
replace valores2_4 = . if inlist(valores2_4, 3, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_values.csv", replace

**# Bookmark 3: inperson

* ============================================================
* inperson (PRESEN_1 to PRESEN_3), 1-4 willingness scale
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols presen_1 presen_2 presen_3

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace presen_1 = . if inlist(presen_1, 8, 9)
replace presen_2 = . if inlist(presen_2, 8, 9)
replace presen_3 = . if inlist(presen_3, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_inperson.csv", replace

**# Bookmark 4: online

* ============================================================
* online (ONLINE_1 to ONLINE_3), 1-4 willingness scale
* code 7 is N.P. (no devices or no internet access), recoded to missing
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols online_1 online_2 online_3

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace online_1 = . if inlist(online_1, 7, 8, 9)
replace online_2 = . if inlist(online_2, 7, 8, 9)
replace online_3 = . if inlist(online_3, 7, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_online.csv", replace

**# Bookmark 5: associations

* ============================================================
* associations (ASOCIACIONES_1 to ASOCIACIONES_11), 1-4 membership scale
* scale runs from most attachment (1) to never belonged (4)
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols asociaciones_1 asociaciones_2 asociaciones_3 asociaciones_4 asociaciones_5 asociaciones_6 asociaciones_7 asociaciones_8 asociaciones_9 asociaciones_10 asociaciones_11

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace asociaciones_1 = . if inlist(asociaciones_1, 8, 9)
replace asociaciones_2 = . if inlist(asociaciones_2, 8, 9)
replace asociaciones_3 = . if inlist(asociaciones_3, 8, 9)
replace asociaciones_4 = . if inlist(asociaciones_4, 8, 9)
replace asociaciones_5 = . if inlist(asociaciones_5, 8, 9)
replace asociaciones_6 = . if inlist(asociaciones_6, 8, 9)
replace asociaciones_7 = . if inlist(asociaciones_7, 8, 9)
replace asociaciones_8 = . if inlist(asociaciones_8, 8, 9)
replace asociaciones_9 = . if inlist(asociaciones_9, 8, 9)
replace asociaciones_10 = . if inlist(asociaciones_10, 8, 9)
replace asociaciones_11 = . if inlist(asociaciones_11, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_associations.csv", replace

**# Bookmark 6: actions

* ============================================================
* actions (ACTI_1 to ACTI_13), 1-4 participation scale
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols acti_1 acti_2 acti_3 acti_4 acti_5 acti_6 acti_7 acti_8 acti_9 acti_10 acti_11 acti_12 acti_13

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace acti_1 = . if inlist(acti_1, 8, 9)
replace acti_2 = . if inlist(acti_2, 8, 9)
replace acti_3 = . if inlist(acti_3, 8, 9)
replace acti_4 = . if inlist(acti_4, 8, 9)
replace acti_5 = . if inlist(acti_5, 8, 9)
replace acti_6 = . if inlist(acti_6, 8, 9)
replace acti_7 = . if inlist(acti_7, 8, 9)
replace acti_8 = . if inlist(acti_8, 8, 9)
replace acti_9 = . if inlist(acti_9, 8, 9)
replace acti_10 = . if inlist(acti_10, 8, 9)
replace acti_11 = . if inlist(acti_11, 8, 9)
replace acti_12 = . if inlist(acti_12, 8, 9)
replace acti_13 = . if inlist(acti_13, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_actions.csv", replace

**# Bookmark 7: difficulty

* ============================================================
* difficulty (PROBLE, FINMES), 1-5 easy to difficult scale
* code 3 is the unread (NO LEER) midpoint, recoded to missing
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols proble finmes

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace proble = . if inlist(proble, 3, 8, 9)
replace finmes = . if inlist(finmes, 3, 8, 9)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_difficulty.csv", replace

**# Bookmark 8: political

* ============================================================
* political (ESCIDEOL 1-10, PROBVOTO 0-10)
* sentinels differ by item, recoded separately
* probvoto code 97 is N.P. and matches the filtered cases exactly
* ============================================================

use "spain_2024_politics_master.dta", clear

local survey_cols escideol probvoto

keep id cov_* `survey_cols'

* per-item sentinel recodes on wide data

replace escideol = . if inlist(escideol, 98, 99)
replace probvoto = . if inlist(probvoto, 97, 98, 99)

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id item resp cov_*
export delimited using "spain_2024_politics_political.csv", replace