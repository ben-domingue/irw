*** This Stata Do File processes the spain_2023_science study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2023_science"

import delimited "3406_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

rename *, lower

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2023_science_master.dta", replace

**# Bookmark 1: interest

* ============================================================
* interest (P1, P2_1 to P2_7)
* 1-5 interest in science and technology, general and specific advances
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p1 p2_1 p2_2 p2_3 p2_4 p2_5 p2_6 p2_7

keep id cov_* `survey_cols'

replace p1 = . if inlist(p1, 8, 9)
replace p2_1 = . if inlist(p2_1, 8, 9)
replace p2_2 = . if inlist(p2_2, 8, 9)
replace p2_3 = . if inlist(p2_3, 8, 9)
replace p2_4 = . if inlist(p2_4, 8, 9)
replace p2_5 = . if inlist(p2_5, 8, 9)
replace p2_6 = . if inlist(p2_6, 8, 9)
replace p2_7 = . if inlist(p2_7, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_interest.csv", replace

**# Bookmark 2: science

* ============================================================
* science (P3ES_1 to P3ES_6)
* 1-5 association of words with science
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p3es_1 p3es_2 p3es_3 p3es_4 p3es_5 p3es_6

keep id cov_* `survey_cols'

replace p3es_1 = . if inlist(p3es_1, 8, 9)
replace p3es_2 = . if inlist(p3es_2, 8, 9)
replace p3es_3 = . if inlist(p3es_3, 8, 9)
replace p3es_4 = . if inlist(p3es_4, 8, 9)
replace p3es_5 = . if inlist(p3es_5, 8, 9)
replace p3es_6 = . if inlist(p3es_6, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_science.csv", replace

**# Bookmark 3: technology

* ============================================================
* technology (P4ES_1 to P4ES_6)
* 1-5 association of words with technology
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p4es_1 p4es_2 p4es_3 p4es_4 p4es_5 p4es_6

keep id cov_* `survey_cols'

replace p4es_1 = . if inlist(p4es_1, 8, 9)
replace p4es_2 = . if inlist(p4es_2, 8, 9)
replace p4es_3 = . if inlist(p4es_3, 8, 9)
replace p4es_4 = . if inlist(p4es_4, 8, 9)
replace p4es_5 = . if inlist(p4es_5, 8, 9)
replace p4es_6 = . if inlist(p4es_6, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_technology.csv", replace

**# Bookmark 4: activities

* ============================================================
* activities (P5_1 to P5_6)
* 1-5 interest in science and technology related activities
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p5_1 p5_2 p5_3 p5_4 p5_5 p5_6

keep id cov_* `survey_cols'

replace p5_1 = . if inlist(p5_1, 8, 9)
replace p5_2 = . if inlist(p5_2, 8, 9)
replace p5_3 = . if inlist(p5_3, 8, 9)
replace p5_4 = . if inlist(p5_4, 8, 9)
replace p5_5 = . if inlist(p5_5, 8, 9)
replace p5_6 = . if inlist(p5_6, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_activities.csv", replace

**# Bookmark 5: engagement

* ============================================================
* engagement (P6_1 to P6_4)
* 1-5 frequency of science related actions in daily life
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p6_1 p6_2 p6_3 p6_4

keep id cov_* `survey_cols'

replace p6_1 = . if inlist(p6_1, 8, 9)
replace p6_2 = . if inlist(p6_2, 8, 9)
replace p6_3 = . if inlist(p6_3, 8, 9)
replace p6_4 = . if inlist(p6_4, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_engagement.csv", replace

**# Bookmark 6: utility

* ============================================================
* utility (P7ES_1 to P7ES_4)
* 1-5 usefulness of science knowledge for various matters
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p7es_1 p7es_2 p7es_3 p7es_4

keep id cov_* `survey_cols'

replace p7es_1 = . if inlist(p7es_1, 8, 9)
replace p7es_2 = . if inlist(p7es_2, 8, 9)
replace p7es_3 = . if inlist(p7es_3, 8, 9)
replace p7es_4 = . if inlist(p7es_4, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_utility.csv", replace

**# Bookmark 7: situations

* ============================================================
* situations (P8ES_1 to P8ES_4)
* 1-5 usefulness of own science training in situations
* code 7 is No procede (not applicable), recoded to missing
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p8es_1 p8es_2 p8es_3 p8es_4

keep id cov_* `survey_cols'

replace p8es_1 = . if inlist(p8es_1, 7, 8, 9)
replace p8es_2 = . if inlist(p8es_2, 7, 8, 9)
replace p8es_3 = . if inlist(p8es_3, 7, 8, 9)
replace p8es_4 = . if inlist(p8es_4, 7, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_situations.csv", replace

**# Bookmark 8: functions

* ============================================================
* functions (P9_1 to P9_5)
* 1-5 usefulness of science for different functions
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p9_1 p9_2 p9_3 p9_4 p9_5

keep id cov_* `survey_cols'

replace p9_1 = . if inlist(p9_1, 8, 9)
replace p9_2 = . if inlist(p9_2, 8, 9)
replace p9_3 = . if inlist(p9_3, 8, 9)
replace p9_4 = . if inlist(p9_4, 8, 9)
replace p9_5 = . if inlist(p9_5, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_functions.csv", replace

**# Bookmark 9: benefits

* ============================================================
* benefits (P10_1 to P10_4)
* 1-5 agreement with benefits of scientific advances
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p10_1 p10_2 p10_3 p10_4

keep id cov_* `survey_cols'

replace p10_1 = . if inlist(p10_1, 8, 9)
replace p10_2 = . if inlist(p10_2, 8, 9)
replace p10_3 = . if inlist(p10_3, 8, 9)
replace p10_4 = . if inlist(p10_4, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_benefits.csv", replace

**# Bookmark 10: dangers

* ============================================================
* dangers (P11_1 to P11_4)
* 1-5 agreement with dangers of scientific advances
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p11_1 p11_2 p11_3 p11_4

keep id cov_* `survey_cols'

replace p11_1 = . if inlist(p11_1, 8, 9)
replace p11_2 = . if inlist(p11_2, 8, 9)
replace p11_3 = . if inlist(p11_3, 8, 9)
replace p11_4 = . if inlist(p11_4, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_dangers.csv", replace

**# Bookmark 11: future

* ============================================================
* future (P12, P13)
* 1-5 benefits and risks in the next 20 years
* code 3 is a (NO LEER) volunteered midpoint, recoded to missing
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p12 p13

keep id cov_* `survey_cols'

replace p12 = . if inlist(p12, 3, 8, 9)
replace p13 = . if inlist(p13, 3, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_future.csv", replace

**# Bookmark 12: cuts

* ============================================================
* cuts (P14, P15, P16)
* favor or against cutting science spending by different actors
* ============================================================

use "spain_2023_science_master.dta", clear

local survey_cols p14 p15 p16

keep id cov_* `survey_cols'

replace p14 = . if inlist(p14, 8, 9)
replace p15 = . if inlist(p15, 8, 9)
replace p16 = . if inlist(p16, 8, 9)

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
keep id cov_* item resp
export delimited using "spain_2023_science_cuts.csv", replace