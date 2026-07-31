*** This Stata Do File processes the spain_2025_inequality study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_inequality"

* import study dataset (semicolon delimited, quote-wrapped headers)

import delimited "3522_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

rename *, lower

* generate row id

gen long id = _n

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress

save "spain_2025_inequality_master.dta", replace

**# Bookmark 1: inequality

* ============================================================
* inequality (P9DESIGU_1 to P9DESIGU_7)
* ============================================================

use "spain_2025_inequality_master.dta", clear

local survey_cols p9desigu_1 p9desigu_2 p9desigu_3 p9desigu_4 p9desigu_5 p9desigu_6 p9desigu_7

keep id cov_* `survey_cols'

replace p9desigu_1 = . if inlist(p9desigu_1, 98, 99)
replace p9desigu_2 = . if inlist(p9desigu_2, 98, 99)
replace p9desigu_3 = . if inlist(p9desigu_3, 98, 99)
replace p9desigu_4 = . if inlist(p9desigu_4, 98, 99)
replace p9desigu_5 = . if inlist(p9desigu_5, 98, 99)
replace p9desigu_6 = . if inlist(p9desigu_6, 98, 99)
replace p9desigu_7 = . if inlist(p9desigu_7, 98, 99)

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
export delimited using "spain_2025_inequality_inequality.csv", replace

**# Bookmark 2: leaders

* ============================================================
* leaders (VALORALIDERES_1 to VALORALIDERES_4)
* 0 = N.P. (filtered out by LIDERESCONOCE), treated as missing
* ============================================================

use "spain_2025_inequality_master.dta", clear

local survey_cols valoralideres_1 valoralideres_2 valoralideres_3 valoralideres_4

keep id cov_* `survey_cols'

replace valoralideres_1 = . if inlist(valoralideres_1, 0, 98, 99)
replace valoralideres_2 = . if inlist(valoralideres_2, 0, 98, 99)
replace valoralideres_3 = . if inlist(valoralideres_3, 0, 98, 99)
replace valoralideres_4 = . if inlist(valoralideres_4, 0, 98, 99)

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
export delimited using "spain_2025_inequality_leaders.csv", replace

**# Bookmark 3: recognition

* ============================================================
* recognition (LIDERESCONOCE_1 to LIDERESCONOCE_4)
* sentinel 9 cleared first, then 7 (no conoce) remapped to 0
* ============================================================

use "spain_2025_inequality_master.dta", clear

local survey_cols lideresconoce_1 lideresconoce_2 lideresconoce_3 lideresconoce_4

keep id cov_* `survey_cols'

replace lideresconoce_1 = . if lideresconoce_1 == 9
replace lideresconoce_2 = . if lideresconoce_2 == 9
replace lideresconoce_3 = . if lideresconoce_3 == 9
replace lideresconoce_4 = . if lideresconoce_4 == 9

replace lideresconoce_1 = 0 if lideresconoce_1 == 7
replace lideresconoce_2 = 0 if lideresconoce_2 == 7
replace lideresconoce_3 = 0 if lideresconoce_3 == 7
replace lideresconoce_4 = 0 if lideresconoce_4 == 7

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
export delimited using "spain_2025_inequality_recognition.csv", replace

**# Bookmark 4: personal

* ============================================================
* personal (P4, P10, P11)
* all coded 1 = most, 5 = least, no remap required
* ============================================================

use "spain_2025_inequality_master.dta", clear

local survey_cols p4 p10 p11

keep id cov_* `survey_cols'

replace p4 = . if inlist(p4, 8, 9)
replace p10 = . if p10 == 9
replace p11 = . if inlist(p11, 8, 9)

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
export delimited using "spain_2025_inequality_personal.csv", replace

**# Bookmark 5: trajectory

* ============================================================
* trajectory (P5, P6, P12)
* sentinels cleared first, then recode to ordered scale
* 1 = menos, 2 = igual, 3 = mas
* recode used so the mapping is simultaneous, not sequential
* ============================================================

use "spain_2025_inequality_master.dta", clear

local survey_cols p5 p6 p12

keep id cov_* `survey_cols'

replace p5 = . if inlist(p5, 8, 9)
replace p6 = . if inlist(p6, 8, 9)
replace p12 = . if inlist(p12, 8, 9)

recode p5 (1 = 3) (2 = 1) (3 = 2)
recode p6 (1 = 3) (2 = 1) (3 = 2)
recode p12 (1 = 3) (2 = 1) (3 = 2)

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
export delimited using "spain_2025_inequality_trajectory.csv", replace