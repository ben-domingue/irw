*** This Stata Do File processes the argentina_2017_victimization study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\argentina_2017_victimization"

import spss using "ENV2017_Baseusuario.sav", clear

rename *, lower

* drop admin ids, weights, jefe variables, household roster, and derived/constructed variables
* the shipped id variable is the dwelling identifier and is regenerated as a row id later

drop id nvvnd nhogar

drop f_hogar f_persona

drop j_*

drop hdv* hcv* hho* hih*

drop tipo_hogar cantmiem miembros_18_mas menores_18 menores_10

drop nivel_instruccion condicion_actividad

drop hch02 hch10_*

destring _all, replace force

**# Bookmark 0: covariates and master save

* rename covariates
* hch03 is sex and hch04 is age of the selected household member per the codebook

rename hch03 cov_sex
rename hch04 cov_age

* clean covariates
* age Ns/Nc code is 999 per the codebook, not 99 (ages 99 and 100 are real)

replace cov_age = . if cov_age == 999

label define sex_lbl 1 "Varón" 2 "Mujer", replace
label values cov_sex sex_lbl

gen long id = _n

compress

save "argentina_2017_victimization_master.dta", replace

**# Bookmark 1: fear

* ============================================================
* fear (IPS02a to IPS02j)
* 1-4 how safe the respondent feels in each situation
* 1 Muy seguro to 4 Muy inseguro, higher already means more fear
* sentinels: 98 No aplica, 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ips02a ips02b ips02c ips02d ips02e ips02f ips02g ips02h ips02i ips02j

keep id cov_* `survey_cols'

replace ips02a = . if inlist(ips02a, 98, 99)
replace ips02b = . if inlist(ips02b, 98, 99)
replace ips02c = . if inlist(ips02c, 98, 99)
replace ips02d = . if inlist(ips02d, 98, 99)
replace ips02e = . if inlist(ips02e, 98, 99)
replace ips02f = . if inlist(ips02f, 98, 99)
replace ips02g = . if inlist(ips02g, 98, 99)
replace ips02h = . if inlist(ips02h, 98, 99)
replace ips02i = . if inlist(ips02i, 98, 99)
replace ips02j = . if inlist(ips02j, 98, 99)

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
export delimited using "argentina_2017_victimization_fear.csv", replace

**# Bookmark 2: disorder

* ============================================================
* disorder (IPS03a to IPS03i)
* yes/no presence of disorder problems in the neighborhood
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more disorder
* sentinel: 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ips03a ips03b ips03c ips03d ips03e ips03f ips03g ips03h ips03i

keep id cov_* `survey_cols'

replace ips03a = . if ips03a == 99
replace ips03b = . if ips03b == 99
replace ips03c = . if ips03c == 99
replace ips03d = . if ips03d == 99
replace ips03e = . if ips03e == 99
replace ips03f = . if ips03f == 99
replace ips03g = . if ips03g == 99
replace ips03h = . if ips03h == 99
replace ips03i = . if ips03i == 99

* reverse so higher resp means more disorder

replace ips03a = 3 - ips03a
replace ips03b = 3 - ips03b
replace ips03c = 3 - ips03c
replace ips03d = 3 - ips03d
replace ips03e = 3 - ips03e
replace ips03f = 3 - ips03f
replace ips03g = 3 - ips03g
replace ips03h = 3 - ips03h
replace ips03i = 3 - ips03i

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
export delimited using "argentina_2017_victimization_disorder.csv", replace

**# Bookmark 3: trend

* ============================================================
* trend (IPS04a to IPS04d)
* 1-3 perceived change in crime by geographic level
* reversed from 1 Aumento 3 Disminuyo so higher means crime increased
* sentinel: 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ips04a ips04b ips04c ips04d

keep id cov_* `survey_cols'

replace ips04a = . if ips04a == 99
replace ips04b = . if ips04b == 99
replace ips04c = . if ips04c == 99
replace ips04d = . if ips04d == 99

* reverse so higher resp means perceived crime increase

replace ips04a = 4 - ips04a
replace ips04b = 4 - ips04b
replace ips04c = 4 - ips04c
replace ips04d = 4 - ips04d

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
export delimited using "argentina_2017_victimization_trend.csv", replace

**# Bookmark 4: precaution

* ============================================================
* precaution (IMS10a to IMS10m)
* yes/no stopped doing activities during 2016 for security reasons
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more precaution
* sentinel: 98 No aplica
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ims10a ims10b ims10c ims10d ims10e ims10f ims10g ims10h ims10i ims10j ims10k ims10l ims10m

keep id cov_* `survey_cols'

replace ims10a = . if ims10a == 98
replace ims10b = . if ims10b == 98
replace ims10c = . if ims10c == 98
replace ims10d = . if ims10d == 98
replace ims10e = . if ims10e == 98
replace ims10f = . if ims10f == 98
replace ims10g = . if ims10g == 98
replace ims10h = . if ims10h == 98
replace ims10i = . if ims10i == 98
replace ims10j = . if ims10j == 98
replace ims10k = . if ims10k == 98
replace ims10l = . if ims10l == 98
replace ims10m = . if ims10m == 98

* reverse so higher resp means more precaution taken

replace ims10a = 3 - ims10a
replace ims10b = 3 - ims10b
replace ims10c = 3 - ims10c
replace ims10d = 3 - ims10d
replace ims10e = 3 - ims10e
replace ims10f = 3 - ims10f
replace ims10g = 3 - ims10g
replace ims10h = 3 - ims10h
replace ims10i = 3 - ims10i
replace ims10j = 3 - ims10j
replace ims10k = 3 - ims10k
replace ims10l = 3 - ims10l
replace ims10m = 3 - ims10m

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
export delimited using "argentina_2017_victimization_precaution.csv", replace

**# Bookmark 5: confidence

* ============================================================
* confidence (IDS02a to IDS02f)
* 1-4 confidence in security and justice institutions
* reversed from 1 Muy confiable 4 Nada confiable so higher means more confidence
* sentinel: 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ids02a ids02b ids02c ids02d ids02e ids02f

keep id cov_* `survey_cols'

replace ids02a = . if ids02a == 99
replace ids02b = . if ids02b == 99
replace ids02c = . if ids02c == 99
replace ids02d = . if ids02d == 99
replace ids02e = . if ids02e == 99
replace ids02f = . if ids02f == 99

* reverse so higher resp means more confidence

replace ids02a = 5 - ids02a
replace ids02b = 5 - ids02b
replace ids02c = 5 - ids02c
replace ids02d = 5 - ids02d
replace ids02e = 5 - ids02e
replace ids02f = 5 - ids02f

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
export delimited using "argentina_2017_victimization_confidence.csv", replace

**# Bookmark 6: fairness

* ============================================================
* fairness (IDS13a to IDS13d)
* 1-4 agreement that police are fair, protective, honest, professional
* reversed from 1 Muy de acuerdo 4 Muy en desacuerdo so higher means more agreement
* sentinel: 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ids13a ids13b ids13c ids13d

keep id cov_* `survey_cols'

replace ids13a = . if ids13a == 99
replace ids13b = . if ids13b == 99
replace ids13c = . if ids13c == 99
replace ids13d = . if ids13d == 99

* reverse so higher resp means more agreement

replace ids13a = 5 - ids13a
replace ids13b = 5 - ids13b
replace ids13c = 5 - ids13c
replace ids13d = 5 - ids13d

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
export delimited using "argentina_2017_victimization_fairness.csv", replace

**# Bookmark 7: performance

* ============================================================
* performance (IDS04, IDS12)
* 1-4 rating of police crime control and police treatment of residents
* reversed from 1 Muy buena 4 Muy mala so higher means better rating
* sentinel: 99 Ns/Nc
* ============================================================

use "argentina_2017_victimization_master.dta", clear

local survey_cols ids04 ids12

keep id cov_* `survey_cols'

replace ids04 = . if ids04 == 99
replace ids12 = . if ids12 == 99

* reverse so higher resp means better rated police performance

replace ids04 = 5 - ids04
replace ids12 = 5 - ids12

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
export delimited using "argentina_2017_victimization_performance.csv", replace
