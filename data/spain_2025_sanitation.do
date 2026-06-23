*** This Stata Do File processes the spain_2025_sanitation study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2025_sanitation"

import delimited "3531_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

destring _all, replace force

gen id = _n

* rename covariates

rename SEXO cov_sex
rename EDAD cov_age
rename ESTUDIOS cov_education

* clean covariates

replace cov_age = . if cov_age == 99
replace cov_education = . if cov_education == 9

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

label define education_lbl 1 "Sin estudios" 2 "Primaria" 3 "Secundaria 1a etapa" 4 "Secundaria 2a etapa" 5 "F.P." 6 "Superiores" 7 "Otros"
label values cov_education education_lbl

save "spain_2025_master.dta", replace

**# Table 1: system

* ============================================================
* system (P1, P2, P12)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P1 P2 P12

keep id cov_* `survey_cols'

replace P1 = . if inlist(P1, 8, 9)
replace P2 = . if inlist(P2, 98, 99)
replace P12 = . if inlist(P12, 8, 9)

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
drop P1 P2 P12
export delimited using "spain_2025_sanitation_system.csv", replace

**# Table 2: services

* ============================================================
* services (P4ES_1 to P4ES_6)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P4ES_1 P4ES_2 P4ES_3 P4ES_4 P4ES_5 P4ES_6

keep id cov_* `survey_cols'

replace P4ES_1 = . if inlist(P4ES_1, 98, 99)
replace P4ES_2 = . if inlist(P4ES_2, 98, 99)
replace P4ES_3 = . if inlist(P4ES_3, 98, 99)
replace P4ES_4 = . if inlist(P4ES_4, 98, 99)
replace P4ES_5 = . if inlist(P4ES_5, 98, 99)
replace P4ES_6 = . if inlist(P4ES_6, 98, 99)

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
drop P4ES_1 P4ES_2 P4ES_3 P4ES_4 P4ES_5 P4ES_6
export delimited using "spain_2025_sanitation_services.csv", replace

**# Table 3: primary

* ============================================================
* primary (P5D, P5E, P5F, P5G, P5H)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P5D_1 P5D_2 P5D_3 P5D_4 P5E_1 P5E_2 P5E_3 P5E_4 P5E_5 P5F P5G P5H

keep id cov_* `survey_cols'

replace P5D_1 = . if inlist(P5D_1, 0, 8, 9)
replace P5D_2 = . if inlist(P5D_2, 0, 8, 9)
replace P5D_3 = . if inlist(P5D_3, 0, 8, 9)
replace P5D_4 = . if inlist(P5D_4, 0, 8, 9)
replace P5E_1 = . if inlist(P5E_1, 0, 98, 99)
replace P5E_2 = . if inlist(P5E_2, 0, 98, 99)
replace P5E_3 = . if inlist(P5E_3, 0, 98, 99)
replace P5E_4 = . if inlist(P5E_4, 0, 98, 99)
replace P5E_5 = . if inlist(P5E_5, 0, 98, 99)
replace P5F = . if inlist(P5F, 0, 8, 9)
replace P5G = . if inlist(P5G, 0, 9)
replace P5H = . if inlist(P5H, 0, 8, 9)

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
drop P5D_1 P5D_2 P5D_3 P5D_4 P5E_1 P5E_2 P5E_3 P5E_4 P5E_5 P5F P5G P5H
export delimited using "spain_2025_sanitation_primary.csv", replace

**# Table 4: emergency | dropped to it being a single-item table

**# Table 5: specialist

* ============================================================
* specialist (P7C, P7D, P7E)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P7C_1 P7C_2 P7C_3 P7D_1 P7D_2 P7D_3 P7E

keep id cov_* `survey_cols'

replace P7C_1 = . if inlist(P7C_1, 0, 8, 9)
replace P7C_2 = . if inlist(P7C_2, 0, 8, 9)
replace P7C_3 = . if inlist(P7C_3, 0, 8, 9)
replace P7D_1 = . if inlist(P7D_1, 0, 98, 99)
replace P7D_2 = . if inlist(P7D_2, 0, 98, 99)
replace P7D_3 = . if inlist(P7D_3, 0, 98, 99)
replace P7E = . if inlist(P7E, 0, 8, 9)

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
drop P7C_1 P7C_2 P7C_3 P7D_1 P7D_2 P7D_3 P7E
export delimited using "spain_2025_sanitation_specialist.csv", replace

**# Table 6: mental

* ============================================================
* mental (P8D, P8E, P8F, P8G)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P8D_1 P8D_2 P8D_3 P8D_4 P8E P8F P8G

keep id cov_* `survey_cols'

replace P8D_1 = . if inlist(P8D_1, 0, 8, 9)
replace P8D_2 = . if inlist(P8D_2, 0, 8, 9)
replace P8D_3 = . if inlist(P8D_3, 0, 8, 9)
replace P8D_4 = . if inlist(P8D_4, 0, 8, 9)
replace P8E = . if inlist(P8E, 0, 8, 9)
replace P8F = . if inlist(P8F, 0, 8, 9)
replace P8G = . if inlist(P8G, 0, 8, 9)

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
drop P8D_1 P8D_2 P8D_3 P8D_4 P8E P8F P8G
export delimited using "spain_2025_sanitation_mental.csv", replace

**# Table 7: hospital

* ============================================================
* hospital (P9B, P9C, P9D)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P9B_1 P9B_2 P9C_1 P9C_2 P9C_3 P9C_4 P9C_5 P9D

keep id cov_* `survey_cols'

replace P9B_1 = . if inlist(P9B_1, 0, 8, 9)
replace P9B_2 = . if inlist(P9B_2, 0, 8, 9)
replace P9C_1 = . if inlist(P9C_1, 0, 98, 99)
replace P9C_2 = . if inlist(P9C_2, 0, 98, 99)
replace P9C_3 = . if inlist(P9C_3, 0, 98, 99)
replace P9C_4 = . if inlist(P9C_4, 0, 98, 99)
replace P9C_5 = . if inlist(P9C_5, 0, 98, 99)
replace P9D = . if inlist(P9D, 0, 8, 9)

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
drop P9B_1 P9B_2 P9C_1 P9C_2 P9C_3 P9C_4 P9C_5 P9D
export delimited using "spain_2025_sanitation_hospital.csv", replace

**# Table 8: diagnostics

* ============================================================
* diagnostics (P10_1 to P10_4)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P10_1 P10_2 P10_3 P10_4

keep id cov_* `survey_cols'

replace P10_1 = . if inlist(P10_1, 8, 9)
replace P10_2 = . if inlist(P10_2, 8, 9)
replace P10_3 = . if inlist(P10_3, 8, 9)
replace P10_4 = . if inlist(P10_4, 8, 9)

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
drop P10_1 P10_2 P10_3 P10_4
export delimited using "spain_2025_sanitation_diagnostics.csv", replace

**# Table 9: coordination

* ============================================================
* coordination (P11, P13)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P11 P13

keep id cov_* `survey_cols'

replace P11 = . if inlist(P11, 6, 8, 9)
replace P13 = . if inlist(P13, 9)

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
drop P11 P13
export delimited using "spain_2025_sanitation_coordination.csv", replace

**# Table 10: regional

* ============================================================
* regional (P19_1 to P19_4)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P19_1 P19_2 P19_3 P19_4

keep id cov_* `survey_cols'

replace P19_1 = . if inlist(P19_1, 0, 8, 9)
replace P19_2 = . if inlist(P19_2, 0, 8, 9)
replace P19_3 = . if inlist(P19_3, 0, 8, 9)
replace P19_4 = . if inlist(P19_4, 0, 8, 9)

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
drop P19_1 P19_2 P19_3 P19_4
export delimited using "spain_2025_sanitation_regional.csv", replace

**# Table 11: digital

* ============================================================
* digital (P14, P15, P17, P20)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P14 P15 P17 P20

keep id cov_* `survey_cols'

replace P14 = . if inlist(P14, 3, 8, 9)
replace P15 = . if inlist(P15, 3, 4, 9)
replace P17 = . if inlist(P17, 4, 9)
replace P20 = . if inlist(P20, 8, 9)

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
drop P14 P15 P17 P20
export delimited using "spain_2025_sanitation_digital.csv", replace

**# Table 12: aicomfort

* ============================================================
* aicomfort (P22_1 to P22_4)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P22_1 P22_2 P22_3 P22_4

keep id cov_* `survey_cols'

replace P22_1 = . if inlist(P22_1, 98, 99)
replace P22_2 = . if inlist(P22_2, 98, 99)
replace P22_3 = . if inlist(P22_3, 98, 99)
replace P22_4 = . if inlist(P22_4, 98, 99)

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
drop P22_1 P22_2 P22_3 P22_4
export delimited using "spain_2025_sanitation_aicomfort.csv", replace

**# Table 13: aiconcern

* ============================================================
* aiconcern (P23, P24)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P23 P24

keep id cov_* `survey_cols'

replace P23 = . if inlist(P23, 8, 9)
replace P24 = . if inlist(P24, 8, 9)

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
drop P23 P24
export delimited using "spain_2025_sanitation_aiconcern.csv", replace

**# Table 14: airegulation

* ============================================================
* airegulation (P25_1 to P25_3)
* ============================================================

use "spain_2025_master.dta", clear

local survey_cols P25_1 P25_2 P25_3

keep id cov_* `survey_cols'

replace P25_1 = . if inlist(P25_1, 8, 9)
replace P25_2 = . if inlist(P25_2, 8, 9)
replace P25_3 = . if inlist(P25_3, 8, 9)

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
drop P25_1 P25_2 P25_3
export delimited using "spain_2025_sanitation_airegulation.csv", replace