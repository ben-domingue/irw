*** This Stata Do File processes the spain_2018_housing study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2018_housing"

* import from CIS fixed-width ASCII (positions from ES3212 syntax file)
infix ///
    P3_1 32 P3_2 33 P3_3 34 P3_4 35 P3_5 36 P3_6 37 P3_7 38 P3_8 39 P3_9 40 P3_10 41 ///
    P4_1 42 P4_2 43 P4_3 44 P4_4 45 P4_5 46 P4_6 47 P4_7 48 ///
    P6_1 52 P6_2 53 P6_3 54 P6_4 55 P6_5 56 P6_6 57 ///
    P9_1 60 P9_2 61 P9_3 62 P9_4 63 P9_5 64 P9_6 65 ///
    P12 71 ///
    P13_1 72 P13_2 73 P13_3 74 P13_4 75 P13_5 76 P13_6 77 P13_7 78 ///
    P21_1 160 P21_2 161 P21_3 162 P21_4 163 ///
    P22 182 P23 183 P24 186 ///
    P25_1 187 P25_2 188 P25_3 189 P25_4 190 P25_5 191 ///
    P27_1 193 P27_2 194 P27_3 195 P27_4 196 P27_5 197 P27_6 198 ///
    P31 210 P32 211-213 ///
    using "DA3212.", clear

gen long id = _n

* rename covariates

rename P31 cov_sex
rename P32 cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress
save "spain_2018_master.dta", replace

**# Table 1: neighborhood

* ============================================================
* neighborhood (P3_1 to P3_10)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P3_1 P3_2 P3_3 P3_4 P3_5 P3_6 P3_7 P3_8 P3_9 P3_10

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_neighborhood.csv", replace

**# Table 2: problems

* ============================================================
* problems (P4_1 to P4_7)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P4_1 P4_2 P4_3 P4_4 P4_5 P4_6 P4_7

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_problems.csv", replace

**# Table 3: amenities

* ============================================================
* amenities (P6_1 to P6_6)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P6_1 P6_2 P6_3 P6_4 P6_5 P6_6

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_amenities.csv", replace

**# Table 4: dwelling

* ============================================================
* dwelling (P9_1 to P9_6)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P9_1 P9_2 P9_3 P9_4 P9_5 P9_6

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_dwelling.csv", replace

**# Table 5: building

* ============================================================
* building (P12, P13_1 to P13_7)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P12 P13_1 P13_2 P13_3 P13_4 P13_5 P13_6 P13_7

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_building.csv", replace

**# Table 6: ownership

* ============================================================
* ownership (P21_1 to P21_4)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P21_1 P21_2 P21_3 P21_4

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_ownership.csv", replace

**# Table 7: rentals

* ============================================================
* rentals (P22, P23, P24)
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P22 P23 P24

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_rentals.csv", replace

**# Table 8: opinions

* ============================================================
* opinions (P25_1 to P25_5)
* code 3 is the (NO LEER) volunteered midpoint, recoded to missing
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P25_1 P25_2 P25_3 P25_4 P25_5

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 3, 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_opinions.csv", replace

**# Table 9: measures

* ============================================================
* measures (P27_1 to P27_6)
* code 3 is the (NO LEER) volunteered midpoint, recoded to missing
* ============================================================

use "spain_2018_master.dta", clear

local survey_cols P27_1 P27_2 P27_3 P27_4 P27_5 P27_6

keep id cov_* `survey_cols'

foreach var of local survey_cols {
    replace `var' = . if inlist(`var', 3, 8, 9)
}

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
drop `survey_cols'
export delimited using "spain_2018_housing_measures.csv", replace