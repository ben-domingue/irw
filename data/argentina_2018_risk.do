*** This Stata Do File processes the argentina_2018_risk study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\argentina_2018_risk"

* ============================================================
* pooled ENFR, four waves: 2018, 2013, 2009, 2005
* each wave is imported, renamed to harmonized names, and appended
* only items asked with the same wording and scale in all four waves are kept
* harmonized items: sg02 to sg05 mobility, self-care, activities, pain block
* plus sg06 anxiety/depression, all coded 1 to 3
* every observation is a distinct respondent, waves are never linked
* ============================================================

* wave 2018

import delimited "ENFR 2018 - Base usuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

drop id

destring _all, replace force

* crosswalk renames, wave 2018: bisg02-bisg06, sex bhch03, age bhch04

rename bisg02 sg02
rename bisg03 sg03
rename bisg04 sg04
rename bisg05 sg05
rename bisg06 sg06
rename bhch03 cov_sex
rename bhch04 cov_age

keep sg02 sg03 sg04 sg05 sg06 cov_sex cov_age

gen wave = 2018

tempfile w2018
save `w2018', replace

* wave 2013

import delimited "ENFR2013_baseusuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

drop id

destring _all, replace force

* crosswalk renames, wave 2013: bisg02-bisg06, sex bhch04, age bhch05

rename bisg02 sg02
rename bisg03 sg03
rename bisg04 sg04
rename bisg05 sg05
rename bisg06 sg06
rename bhch04 cov_sex
rename bhch05 cov_age

keep sg02 sg03 sg04 sg05 sg06 cov_sex cov_age

gen wave = 2013

tempfile w2013
save `w2013', replace

* wave 2009

import delimited "ENFR-2009 Base Usuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

drop identifi

destring _all, replace force

* crosswalk renames, wave 2009: bisg02-bisg06, sex bhch04, age bhch05

rename bisg02 sg02
rename bisg03 sg03
rename bisg04 sg04
rename bisg05 sg05
rename bisg06 sg06
rename bhch04 cov_sex
rename bhch05 cov_age

keep sg02 sg03 sg04 sg05 sg06 cov_sex cov_age

gen wave = 2009

tempfile w2009
save `w2009', replace

* wave 2005

import delimited "ENFR-2005 Base Usuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

drop identifi

destring _all, replace force

* crosswalk renames, wave 2005: cisg02-cisg06, sex chch04, age chch05

rename cisg02 sg02
rename cisg03 sg03
rename cisg04 sg04
rename cisg05 sg05
rename cisg06 sg06
rename chch04 cov_sex
rename chch05 cov_age

keep sg02 sg03 sg04 sg05 sg06 cov_sex cov_age

gen wave = 2005

* append the four waves

append using `w2009'

append using `w2013'

append using `w2018'

gen long id = _n

**# Bookmark 0: covariates and master save

* clean covariates
* no age sentinel exists in any wave codebook, observed ranges 18-98 and 18-104

label define sex_lbl 1 "Varón" 2 "Mujer", replace
label values cov_sex sex_lbl

compress

save "argentina_2018_risk_master.dta", replace

**# Bookmark 1: problems

* ============================================================
* problems (SG02 to SG06)
* 1-3 EQ-5D style health state items, mobility, self-care,
* usual activities, pain/discomfort, anxiety/depression
* higher already means more problems, no reversal
* no sentinel codes in any wave, verified in all four codebooks and data
* ============================================================

use "argentina_2018_risk_master.dta", clear

local survey_cols sg02 sg03 sg04 sg05 sg06

keep id wave cov_* `survey_cols'

tempfile long_data
save `long_data', emptyok replace

foreach var of local survey_cols {
    preserve
    keep id wave cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id wave item resp cov_*
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear
drop if missing(item) | item == ""
drop if missing(resp)
sort id item
keep id wave cov_* item resp
label values resp .
export delimited using "argentina_2018_risk_problems.csv", replace
