*** This Stata Do File processes the argentina_2012_tobacco study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\argentina_2012_tobacco"

import delimited "EMTA2012_Argentina_BaseUsuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

* drop weight, design, and household roster variables

drop caseid gatsstrata gatscluster gatsweight selectee region

drop hh*

destring _all, replace force

**# Bookmark 0: covariates and master save

* rename covariates
* a01 is sex and age is the codebook's finalized respondent age (15 to 97, no sentinel)

rename a01 cov_sex
rename age cov_age

* clean covariates

label define sex_lbl 1 "Varón" 2 "Mujer", replace
label values cov_sex sex_lbl

gen long id = _n

compress

save "argentina_2012_tobacco_master.dta", replace

**# Bookmark 1: harm

* ============================================================
* harm (H01, H02A to H02G, H03)
* yes/no believes tobacco use causes each serious illness
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more harm belief
* sentinels: 7 No sabe, 9 Se niega
* ============================================================

use "argentina_2012_tobacco_master.dta", clear

local survey_cols h01 h02a h02b h02c h02d h02e h02f h02g h03

keep id cov_* `survey_cols'

replace h01 = . if inlist(h01, 7, 9)
replace h02a = . if inlist(h02a, 7, 9)
replace h02b = . if inlist(h02b, 7, 9)
replace h02c = . if inlist(h02c, 7, 9)
replace h02d = . if inlist(h02d, 7, 9)
replace h02e = . if inlist(h02e, 7, 9)
replace h02f = . if inlist(h02f, 7, 9)
replace h02g = . if inlist(h02g, 7, 9)
replace h03 = . if inlist(h03, 7, 9)

* reverse so higher resp means more belief in harm

replace h01 = 3 - h01
replace h02a = 3 - h02a
replace h02b = 3 - h02b
replace h02c = 3 - h02c
replace h02d = 3 - h02d
replace h02e = 3 - h02e
replace h02f = 3 - h02f
replace h02g = 3 - h02g
replace h03 = 3 - h03

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
label values resp .
export delimited using "argentina_2012_tobacco_harm.csv", replace

**# Bookmark 2: policy

* ============================================================
* policy (HAR04A, HAR04B, H05, H06)
* favor or oppose tobacco control laws and tax increases
* reversed from 1 A favor 2 En contra so higher means more support
* sentinels: 7 No sabe, 9 Se niega
* ============================================================

use "argentina_2012_tobacco_master.dta", clear

local survey_cols har04a har04b h05 h06

keep id cov_* `survey_cols'

replace har04a = . if inlist(har04a, 7, 9)
replace har04b = . if inlist(har04b, 7, 9)
replace h05 = . if inlist(h05, 7, 9)
replace h06 = . if inlist(h06, 7, 9)

* reverse so higher resp means more policy support

replace har04a = 3 - har04a
replace har04b = 3 - har04b
replace h05 = 3 - h05
replace h06 = 3 - h06

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
label values resp .
export delimited using "argentina_2012_tobacco_policy.csv", replace
