*** This Stata Do File processes the argentina_2013_reproductive study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\argentina_2013_reproductive"

* ============================================================
* two source bases, women and men, separate questionnaires
* only items asked identically in both questionnaires are kept
* common items are renamed to harmonized names without the m/v prefix
* cov_sex is assigned from the source file, 1 Varon 2 Mujer
* ============================================================

* women base

import delimited "ENSSyR_Mujeres_BaseUsuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

* drop weight, roster, and derived variables

drop pondera cv* ho* cantcomponentes tipo_h rango_ingreso ingreso_agrupado grupedad parentesco nivel_instruccion nivel_instruccion_agrupado cond_act cobertura_salud

destring _all, replace force

keep edad mits01_01 mits01_02 mits01_03 mits01_04 mits01_05 mits01_06 mits01_07 mits01_08 mits01_09 mits01_10 mits03 mits04 mits05 mits06

* harmonize names by stripping the questionnaire prefix

rename mits01_01 its01_01
rename mits01_02 its01_02
rename mits01_03 its01_03
rename mits01_04 its01_04
rename mits01_05 its01_05
rename mits01_06 its01_06
rename mits01_07 its01_07
rename mits01_08 its01_08
rename mits01_09 its01_09
rename mits01_10 its01_10
rename mits03 its03
rename mits04 its04
rename mits05 its05
rename mits06 its06

gen cov_sex = 2

tempfile mujeres
save `mujeres', replace

* men base

import delimited "ENSSyR_Varones_BaseUsuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

* drop weight, roster, and derived variables

drop pondera cv* ho* cantcomponentes tipo_h rango_ingreso ingreso_agrupado grupedad parentesco nivel_instruccion nivel_instruccion_agrupado cond_act cobertura_salud

destring _all, replace force

keep edad vits01_01 vits01_02 vits01_03 vits01_04 vits01_05 vits01_06 vits01_07 vits01_08 vits01_09 vits01_10 vits03 vits04 vits05 vits06

* harmonize names by stripping the questionnaire prefix

rename vits01_01 its01_01
rename vits01_02 its01_02
rename vits01_03 its01_03
rename vits01_04 its01_04
rename vits01_05 its01_05
rename vits01_06 its01_06
rename vits01_07 its01_07
rename vits01_08 its01_08
rename vits01_09 its01_09
rename vits01_10 its01_10
rename vits03 its03
rename vits04 its04
rename vits05 its05
rename vits06 its06

gen cov_sex = 1

* append the two bases

append using `mujeres'

gen long id = _n

**# Bookmark 0: covariates and master save

* rename covariates
* edad is age in completed years in both bases, no sentinel per the codebook

rename edad cov_age

* clean covariates

label define sex_lbl 1 "Varón" 2 "Mujer", replace
label values cov_sex sex_lbl

compress

save "argentina_2013_reproductive_master.dta", replace

**# Bookmark 1: awareness

* ============================================================
* awareness (ITS01_01 to ITS01_10)
* yes/no has heard of each sexually transmitted infection
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more awareness
* sentinel: 9 Ns/Nc
* ============================================================

use "argentina_2013_reproductive_master.dta", clear

local survey_cols its01_01 its01_02 its01_03 its01_04 its01_05 its01_06 its01_07 its01_08 its01_09 its01_10

keep id cov_* `survey_cols'

replace its01_01 = . if its01_01 == 9
replace its01_02 = . if its01_02 == 9
replace its01_03 = . if its01_03 == 9
replace its01_04 = . if its01_04 == 9
replace its01_05 = . if its01_05 == 9
replace its01_06 = . if its01_06 == 9
replace its01_07 = . if its01_07 == 9
replace its01_08 = . if its01_08 == 9
replace its01_09 = . if its01_09 == 9
replace its01_10 = . if its01_10 == 9

* reverse so higher resp means more awareness

replace its01_01 = 3 - its01_01
replace its01_02 = 3 - its01_02
replace its01_03 = 3 - its01_03
replace its01_04 = 3 - its01_04
replace its01_05 = 3 - its01_05
replace its01_06 = 3 - its01_06
replace its01_07 = 3 - its01_07
replace its01_08 = 3 - its01_08
replace its01_09 = 3 - its01_09
replace its01_10 = 3 - its01_10

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
export delimited using "argentina_2013_reproductive_awareness.csv", replace

**# Bookmark 2: transmission

* ============================================================
* transmission (ITS03 to ITS06)
* yes/no believes VIH is transmitted by mosquitoes, saliva, mate, toilet
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more transmission belief
* sentinel: 9 Ns/Nc
* ============================================================

use "argentina_2013_reproductive_master.dta", clear

local survey_cols its03 its04 its05 its06

keep id cov_* `survey_cols'

replace its03 = . if its03 == 9
replace its04 = . if its04 == 9
replace its05 = . if its05 == 9
replace its06 = . if its06 == 9

* reverse so higher resp means more belief in casual transmission

replace its03 = 3 - its03
replace its04 = 3 - its04
replace its05 = 3 - its05
replace its06 = 3 - its06

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
export delimited using "argentina_2013_reproductive_transmission.csv", replace
