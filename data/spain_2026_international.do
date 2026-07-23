*** This Stata Do File processes the spain_2026_international study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_international"

* ============================================================
* Import
* ============================================================

import delimited "3564_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

foreach v of varlist _all {
    local lbl : variable label `v'
    if strpos("`lbl'", ":") > 0 {
        local newname = trim(substr("`lbl'", 1, strpos("`lbl'", ":") - 1))
        local newname = subinstr("`newname'", `"""', "", .)
        capture rename `v' `newname'
    }
}

rename *, lower

* destring
destring _all, replace force

* row id
gen long id = _n

* ============================================================
* Clean covariates
* ============================================================

rename sexo cov_sex
rename edad cov_age

replace cov_age = . if cov_age >= 99

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

* compress and save master
compress
save "spain_2026_international_master.dta", replace

**# Table 1: confidence

* ============================================================
* confidence (OOIICONFIANZA_1 to _10), trust 1-10, sentinel 98/99
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols ooiiconfianza_1 ooiiconfianza_2 ooiiconfianza_3 ooiiconfianza_4 ooiiconfianza_5 ooiiconfianza_6 ooiiconfianza_7 ooiiconfianza_8 ooiiconfianza_9 ooiiconfianza_10

keep id cov_* `survey_cols'

replace ooiiconfianza_1 = . if inlist(ooiiconfianza_1, 98, 99)
replace ooiiconfianza_2 = . if inlist(ooiiconfianza_2, 98, 99)
replace ooiiconfianza_3 = . if inlist(ooiiconfianza_3, 98, 99)
replace ooiiconfianza_4 = . if inlist(ooiiconfianza_4, 98, 99)
replace ooiiconfianza_5 = . if inlist(ooiiconfianza_5, 98, 99)
replace ooiiconfianza_6 = . if inlist(ooiiconfianza_6, 98, 99)
replace ooiiconfianza_7 = . if inlist(ooiiconfianza_7, 98, 99)
replace ooiiconfianza_8 = . if inlist(ooiiconfianza_8, 98, 99)
replace ooiiconfianza_9 = . if inlist(ooiiconfianza_9, 98, 99)
replace ooiiconfianza_10 = . if inlist(ooiiconfianza_10, 98, 99)

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
drop ooiiconfianza_1 ooiiconfianza_2 ooiiconfianza_3 ooiiconfianza_4 ooiiconfianza_5 ooiiconfianza_6 ooiiconfianza_7 ooiiconfianza_8 ooiiconfianza_9 ooiiconfianza_10
export delimited using "spain_2026_international_confidence.csv", replace

**# Table 2: influence

* ============================================================
* influence (OOIIINFLUENCIA_1 to _10), influence 1-10, sentinel 98/99
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols ooiiinfluencia_1 ooiiinfluencia_2 ooiiinfluencia_3 ooiiinfluencia_4 ooiiinfluencia_5 ooiiinfluencia_6 ooiiinfluencia_7 ooiiinfluencia_8 ooiiinfluencia_9 ooiiinfluencia_10

keep id cov_* `survey_cols'

replace ooiiinfluencia_1 = . if inlist(ooiiinfluencia_1, 98, 99)
replace ooiiinfluencia_2 = . if inlist(ooiiinfluencia_2, 98, 99)
replace ooiiinfluencia_3 = . if inlist(ooiiinfluencia_3, 98, 99)
replace ooiiinfluencia_4 = . if inlist(ooiiinfluencia_4, 98, 99)
replace ooiiinfluencia_5 = . if inlist(ooiiinfluencia_5, 98, 99)
replace ooiiinfluencia_6 = . if inlist(ooiiinfluencia_6, 98, 99)
replace ooiiinfluencia_7 = . if inlist(ooiiinfluencia_7, 98, 99)
replace ooiiinfluencia_8 = . if inlist(ooiiinfluencia_8, 98, 99)
replace ooiiinfluencia_9 = . if inlist(ooiiinfluencia_9, 98, 99)
replace ooiiinfluencia_10 = . if inlist(ooiiinfluencia_10, 98, 99)

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
drop ooiiinfluencia_1 ooiiinfluencia_2 ooiiinfluencia_3 ooiiinfluencia_4 ooiiinfluencia_5 ooiiinfluencia_6 ooiiinfluencia_7 ooiiinfluencia_8 ooiiinfluencia_9 ooiiinfluencia_10
export delimited using "spain_2026_international_influence.csv", replace

**# Table 3: eu

* ============================================================
* eu (UE_1 to _5), agreement 1-5, sentinel 8/9
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols ue_1 ue_2 ue_3 ue_4 ue_5

keep id cov_* `survey_cols'

replace ue_1 = . if inlist(ue_1, 8, 9)
replace ue_2 = . if inlist(ue_2, 8, 9)
replace ue_3 = . if inlist(ue_3, 8, 9)
replace ue_4 = . if inlist(ue_4, 8, 9)
replace ue_5 = . if inlist(ue_5, 8, 9)

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
drop ue_1 ue_2 ue_3 ue_4 ue_5
export delimited using "spain_2026_international_eu.csv", replace

**# Table 4: un

* ============================================================
* un (ONU_1 to _6), agreement 1-5, sentinel 8/9
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols onu_1 onu_2 onu_3 onu_4 onu_5 onu_6

keep id cov_* `survey_cols'

replace onu_1 = . if inlist(onu_1, 8, 9)
replace onu_2 = . if inlist(onu_2, 8, 9)
replace onu_3 = . if inlist(onu_3, 8, 9)
replace onu_4 = . if inlist(onu_4, 8, 9)
replace onu_5 = . if inlist(onu_5, 8, 9)
replace onu_6 = . if inlist(onu_6, 8, 9)

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
drop onu_1 onu_2 onu_3 onu_4 onu_5 onu_6
export delimited using "spain_2026_international_un.csv", replace

**# Table 5: media

* ============================================================
* media (P7, P9, P10), 1-4 scale, sentinel 8/9
* P7 interes, P9 confianza, P10 simplificacion (all mucho to nada)
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols p7 p9 p10

keep id cov_* `survey_cols'

replace p7 = . if inlist(p7, 8, 9)
replace p9 = . if inlist(p9, 8, 9)
replace p10 = . if inlist(p10, 8, 9)

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
drop p7 p9 p10
export delimited using "spain_2026_international_media.csv", replace

**# Table 6: threat

* ============================================================
* threat (P16, P18), 1-4 scale (mucho to nada), sentinel 8/9
* P16 impact on daily life, P18 worry about global war
* ============================================================

use "spain_2026_international_master.dta", clear

local survey_cols p16 p18

keep id cov_* `survey_cols'

replace p16 = . if inlist(p16, 8, 9)
replace p18 = . if inlist(p18, 8, 9)

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
drop p16 p18
export delimited using "spain_2026_international_threat.csv", replace