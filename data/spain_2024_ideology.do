*** This Stata Do File processes the spain_2024_ideology study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2024_ideology"

import delimited "3480_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

rename *, lower

gen long id = _n

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates

replace cov_age = . if cov_age == 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

order id cov_*, first

compress

save "spain_2024_ideology_master.dta", replace

**# Bookmark 1: identity

* ============================================================
* identity (P2_1 to P2_12)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols p2_1 p2_2 p2_3 p2_4 p2_5 p2_6 p2_7 p2_8 p2_9 p2_10 p2_11 p2_12

keep id cov_* `survey_cols'

replace p2_1 = . if inlist(p2_1, 7, 8, 9)
replace p2_2 = . if inlist(p2_2, 7, 8, 9)
replace p2_3 = . if inlist(p2_3, 7, 8, 9)
replace p2_4 = . if inlist(p2_4, 7, 8, 9)
replace p2_5 = . if inlist(p2_5, 7, 8, 9)
replace p2_6 = . if inlist(p2_6, 7, 8, 9)
replace p2_7 = . if inlist(p2_7, 7, 8, 9)
replace p2_8 = . if inlist(p2_8, 7, 8, 9)
replace p2_9 = . if inlist(p2_9, 7, 8, 9)
replace p2_10 = . if inlist(p2_10, 7, 8, 9)
replace p2_11 = . if inlist(p2_11, 7, 8, 9)
replace p2_12 = . if inlist(p2_12, 7, 8, 9)

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

* drop the (NO LEER) volunteered midpoint

replace resp = . if resp == 3

drop if missing(resp)
sort id item
keep id cov_* item resp
export delimited using "spain_2024_ideology_identity.csv", replace

**# Bookmark 2: welfare

* ============================================================
* welfare (P3_1 to P3_6)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols p3_1 p3_2 p3_3 p3_4 p3_5 p3_6

keep id cov_* `survey_cols'

replace p3_1 = . if inlist(p3_1, 8, 9)
replace p3_2 = . if inlist(p3_2, 8, 9)
replace p3_3 = . if inlist(p3_3, 8, 9)
replace p3_4 = . if inlist(p3_4, 8, 9)
replace p3_5 = . if inlist(p3_5, 8, 9)
replace p3_6 = . if inlist(p3_6, 8, 9)

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

* drop the (NO LEER) volunteered midpoint

replace resp = . if resp == 3

drop if missing(resp)
sort id item
keep id cov_* item resp
export delimited using "spain_2024_ideology_welfare.csv", replace

**# Bookmark 3: rights

* ============================================================
* rights (P6_1 to P6_4)
* ============================================================

use "spain_2024_ideology_master.dta", clear

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

* drop the (NO LEER) volunteered midpoint

replace resp = . if resp == 3

drop if missing(resp)
sort id item
keep id cov_* item resp
export delimited using "spain_2024_ideology_rights.csv", replace

**# Bookmark 4: society

* ============================================================
* society (P8_1 to P8_6)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols p8_1 p8_2 p8_3 p8_4 p8_5 p8_6

keep id cov_* `survey_cols'

replace p8_1 = . if inlist(p8_1, 8, 9)
replace p8_2 = . if inlist(p8_2, 8, 9)
replace p8_3 = . if inlist(p8_3, 8, 9)
replace p8_4 = . if inlist(p8_4, 8, 9)
replace p8_5 = . if inlist(p8_5, 8, 9)
replace p8_6 = . if inlist(p8_6, 8, 9)

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

* drop the (NO LEER) volunteered midpoint

replace resp = . if resp == 3

drop if missing(resp)
sort id item
keep id cov_* item resp
export delimited using "spain_2024_ideology_society.csv", replace

**# Bookmark 5: discomfort

* ============================================================
* discomfort (INCOMOAMBI_1 to INCOMOAMBI_3)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols incomoambi_1 incomoambi_2 incomoambi_3

keep id cov_* `survey_cols'

replace incomoambi_1 = . if inlist(incomoambi_1, 7, 8, 9)
replace incomoambi_2 = . if inlist(incomoambi_2, 7, 8, 9)
replace incomoambi_3 = . if inlist(incomoambi_3, 7, 8, 9)

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
export delimited using "spain_2024_ideology_discomfort.csv", replace

**# Bookmark 6: parties

* ============================================================
* parties (VALORAPART_1 to VALORAPART_12)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols valorapart_1 valorapart_2 valorapart_3 valorapart_4 valorapart_5 valorapart_6 valorapart_7 valorapart_8 valorapart_9 valorapart_10 valorapart_11 valorapart_12

keep id cov_* `survey_cols'

replace valorapart_1 = . if inlist(valorapart_1, 97, 98, 99)
replace valorapart_2 = . if inlist(valorapart_2, 97, 98, 99)
replace valorapart_3 = . if inlist(valorapart_3, 97, 98, 99)
replace valorapart_4 = . if inlist(valorapart_4, 97, 98, 99)
replace valorapart_5 = . if inlist(valorapart_5, 97, 98, 99)
replace valorapart_6 = . if inlist(valorapart_6, 97, 98, 99)
replace valorapart_7 = . if inlist(valorapart_7, 97, 98, 99)
replace valorapart_8 = . if inlist(valorapart_8, 97, 98, 99)
replace valorapart_9 = . if inlist(valorapart_9, 97, 98, 99)
replace valorapart_10 = . if inlist(valorapart_10, 97, 98, 99)
replace valorapart_11 = . if inlist(valorapart_11, 97, 98, 99)
replace valorapart_12 = . if inlist(valorapart_12, 97, 98, 99)

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
export delimited using "spain_2024_ideology_parties.csv", replace

**# Bookmark 7: leaders

* ============================================================
* leaders (LIDERESPOL_1 to LIDERESPOL_12)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols liderespol_1 liderespol_2 liderespol_3 liderespol_4 liderespol_5 liderespol_6 liderespol_7 liderespol_8 liderespol_9 liderespol_10 liderespol_11 liderespol_12

keep id cov_* `survey_cols'

replace liderespol_1 = . if inlist(liderespol_1, 97, 98, 99)
replace liderespol_2 = . if inlist(liderespol_2, 97, 98, 99)
replace liderespol_3 = . if inlist(liderespol_3, 97, 98, 99)
replace liderespol_4 = . if inlist(liderespol_4, 97, 98, 99)
replace liderespol_5 = . if inlist(liderespol_5, 97, 98, 99)
replace liderespol_6 = . if inlist(liderespol_6, 97, 98, 99)
replace liderespol_7 = . if inlist(liderespol_7, 97, 98, 99)
replace liderespol_8 = . if inlist(liderespol_8, 97, 98, 99)
replace liderespol_9 = . if inlist(liderespol_9, 97, 98, 99)
replace liderespol_10 = . if inlist(liderespol_10, 97, 98, 99)
replace liderespol_11 = . if inlist(liderespol_11, 97, 98, 99)
replace liderespol_12 = . if inlist(liderespol_12, 97, 98, 99)

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
export delimited using "spain_2024_ideology_leaders.csv", replace

**# Bookmark 8: sympathy

* ============================================================
* sympathy (SIMPAPART_1 to SIMPAPART_12)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols simpapart_1 simpapart_2 simpapart_3 simpapart_4 simpapart_5 simpapart_6 simpapart_7 simpapart_8 simpapart_9 simpapart_10 simpapart_11 simpapart_12

keep id cov_* `survey_cols'

replace simpapart_1 = . if inlist(simpapart_1, 95, 97, 98, 99)
replace simpapart_2 = . if inlist(simpapart_2, 95, 97, 98, 99)
replace simpapart_3 = . if inlist(simpapart_3, 95, 97, 98, 99)
replace simpapart_4 = . if inlist(simpapart_4, 95, 97, 98, 99)
replace simpapart_5 = . if inlist(simpapart_5, 95, 97, 98, 99)
replace simpapart_6 = . if inlist(simpapart_6, 95, 97, 98, 99)
replace simpapart_7 = . if inlist(simpapart_7, 95, 97, 98, 99)
replace simpapart_8 = . if inlist(simpapart_8, 95, 97, 98, 99)
replace simpapart_9 = . if inlist(simpapart_9, 95, 97, 98, 99)
replace simpapart_10 = . if inlist(simpapart_10, 95, 97, 98, 99)
replace simpapart_11 = . if inlist(simpapart_11, 95, 97, 98, 99)
replace simpapart_12 = . if inlist(simpapart_12, 95, 97, 98, 99)

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
export delimited using "spain_2024_ideology_sympathy.csv", replace

**# Bookmark 9: territorial

* ============================================================
* territorial (P9, IDENTIDAD)
* ============================================================

use "spain_2024_ideology_master.dta", clear

local survey_cols p9 identidad

keep id cov_* `survey_cols'

replace p9 = . if inlist(p9, 8, 9)
replace identidad = . if inlist(identidad, 7, 8, 9)

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
export delimited using "spain_2024_ideology_territorial.csv", replace