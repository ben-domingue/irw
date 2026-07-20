*** This Stata Do File processes the spain_2025_europe study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_europe"

* read raw data (semicolon-delimited; variable names are wrapped in double quotes)
import delimited "3523_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* strip surrounding double quotes from the imported variable names
foreach v of varlist _all {
    local clean = subinstr("`v'", char(34), "", .)
    capture rename `v' `clean'
}

rename *, lower
destring _all, replace force

gen long id = _n

* rename covariates (kept in every table, never counted as items)
rename sexo cov_sex
rename edad cov_age

* clean covariate sentinels (per-variable)
replace cov_age = . if inlist(cov_age, 99)

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress
save "spain_2025_europe_master.dta", replace

******************************************
***********  Process the data ************
******************************************

**# Bookmark 1: attention  (2 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p1 p2

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p1 = . if inlist(p1, 8, 9)
replace p2 = . if inlist(p2, 8, 9)

local question_cols p1 p2
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p1 p2
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_attention.csv", replace

**# Bookmark 2: impact  (4 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p4 p5 p6 p7

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p4 = . if inlist(p4, 8, 9)
replace p5 = . if inlist(p5, 8, 9)
replace p6 = . if inlist(p6, 8, 9)
replace p7 = . if inlist(p7, 8, 9)

local question_cols p4 p5 p6 p7
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p4 p5 p6 p7
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_impact.csv", replace

**# Bookmark 3: effects  (7 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p8_1 p8_2 p8_3 p8_4 p8_5 p8_6 p8_7

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p8_1 = . if inlist(p8_1, 8, 9)
replace p8_2 = . if inlist(p8_2, 8, 9)
replace p8_3 = . if inlist(p8_3, 8, 9)
replace p8_4 = . if inlist(p8_4, 8, 9)
replace p8_5 = . if inlist(p8_5, 8, 9)
replace p8_6 = . if inlist(p8_6, 8, 9)
replace p8_7 = . if inlist(p8_7, 8, 9)

local question_cols p8_1 p8_2 p8_3 p8_4 p8_5 p8_6 p8_7
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p8_1 p8_2 p8_3 p8_4 p8_5 p8_6 p8_7
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_effects.csv", replace

**# Bookmark 4: awareness  (5 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p9_1 p9_2 p9_3 p9_4 p9_5

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p9_1 = . if inlist(p9_1, 9)
replace p9_2 = . if inlist(p9_2, 9)
replace p9_3 = . if inlist(p9_3, 9)
replace p9_4 = . if inlist(p9_4, 9)
replace p9_5 = . if inlist(p9_5, 9)

local question_cols p9_1 p9_2 p9_3 p9_4 p9_5
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p9_1 p9_2 p9_3 p9_4 p9_5
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_awareness.csv", replace

**# Bookmark 5: trust  (5 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p10_1 p10_2 p10_3 p10_4 p10_5

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p10_1 = . if inlist(p10_1, 0, 98, 99)
replace p10_2 = . if inlist(p10_2, 0, 98, 99)
replace p10_3 = . if inlist(p10_3, 0, 98, 99)
replace p10_4 = . if inlist(p10_4, 0, 98, 99)
replace p10_5 = . if inlist(p10_5, 0, 98, 99)

local question_cols p10_1 p10_2 p10_3 p10_4 p10_5
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p10_1 p10_2 p10_3 p10_4 p10_5
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_trust.csv", replace

**# Bookmark 6: policy  (5 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p12_1 p12_2 p12_3 p12_4 p12_5

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p12_1 = . if inlist(p12_1, 8, 9)
replace p12_2 = . if inlist(p12_2, 8, 9)
replace p12_3 = . if inlist(p12_3, 8, 9)
replace p12_4 = . if inlist(p12_4, 8, 9)
replace p12_5 = . if inlist(p12_5, 8, 9)

local question_cols p12_1 p12_2 p12_3 p12_4 p12_5
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p12_1 p12_2 p12_3 p12_4 p12_5
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_policy.csv", replace

**# Bookmark 7: agreement  (3 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p13 p14 p15

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p13 = . if inlist(p13, 8, 9)
replace p14 = . if inlist(p14, 8, 9)
replace p15 = . if inlist(p15, 8, 9)

local question_cols p13 p14 p15
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p13 p14 p15
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_agreement.csv", replace

**# Bookmark 8: spending  (15 items)
use "spain_2025_europe_master.dta", clear
keep id cov_* p16_1 p16_2 p16_3 p16_4 p16_5 p16_6 p16_7 p16_8 p16_9 p16_10 p16_11 p16_12 p16_13 p16_14 p16_15

* per-item sentinel recode on WIDE data (before reshape); keyed to each item's own scale
replace p16_1 = . if inlist(p16_1, 8, 9)
replace p16_2 = . if inlist(p16_2, 8, 9)
replace p16_3 = . if inlist(p16_3, 8, 9)
replace p16_4 = . if inlist(p16_4, 8, 9)
replace p16_5 = . if inlist(p16_5, 8, 9)
replace p16_6 = . if inlist(p16_6, 8, 9)
replace p16_7 = . if inlist(p16_7, 8, 9)
replace p16_8 = . if inlist(p16_8, 8, 9)
replace p16_9 = . if inlist(p16_9, 8, 9)
replace p16_10 = . if inlist(p16_10, 8, 9)
replace p16_11 = . if inlist(p16_11, 8, 9)
replace p16_12 = . if inlist(p16_12, 8, 9)
replace p16_13 = . if inlist(p16_13, 8, 9)
replace p16_14 = . if inlist(p16_14, 8, 9)
replace p16_15 = . if inlist(p16_15, 8, 9)

local question_cols p16_1 p16_2 p16_3 p16_4 p16_5 p16_6 p16_7 p16_8 p16_9 p16_10 p16_11 p16_12 p16_13 p16_14 p16_15
tempfile long_data
save `long_data', emptyok replace
foreach var of local question_cols {
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
drop p16_1 p16_2 p16_3 p16_4 p16_5 p16_6 p16_7 p16_8 p16_9 p16_10 p16_11 p16_12 p16_13 p16_14 p16_15
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2025_europe_spending.csv", replace