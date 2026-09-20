*** This Stata Do File processes the argentina_2012_aging study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\argentina_2012_aging"

import delimited "ENCaViAM2012_Base_usuario.txt", delimiter("|") varnames(1) case(preserve) encoding("UTF-8") clear

rename *, lower

* drop admin ids, weight, household roster, dwelling, income, employment, and derived variables

drop id codusu nro_hogar componente pond_calibrada

drop iv* ii* v* ix_* estrato_hogar itf decifr ipcf deccfr

drop ch* nivel_ed estado cat_ocup cat_inac intensi

drop pp* p21 decocur tot_p12 p47t decindr t_vi

drop def_vis def_aud dep_bas dep_amp nsv

destring _all, replace force

**# Bookmark 0: covariates and master save

* rename covariates
* sexo is sex and edad is age in years per the codebook, no age sentinel (range 60 to 98)

rename sexo cov_sex
rename edad cov_age

* clean covariates

label define sex_lbl 1 "Varón" 2 "Mujer", replace
label values cov_sex sex_lbl

gen long id = _n

compress

save "argentina_2012_aging_master.dta", replace

**# Bookmark 1: health

* ============================================================
* health (AU01, AU03)
* 1-5 self-rated health and self-rated memory
* reversed from 1 excelente 5 mala so higher means better status
* no sentinel codes per the codebook
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols au01 au03

keep id cov_* `survey_cols'

* reverse so higher resp means better self-rated status

replace au01 = 6 - au01
replace au03 = 6 - au03

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
export delimited using "argentina_2012_aging_health.csv", replace

**# Bookmark 2: change

* ============================================================
* change (AU02, AU04)
* 1-3 health and memory compared with last year
* reversed from 1 ha mejorado 3 ha empeorado so higher means improvement
* no sentinel codes per the codebook
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols au02 au04

keep id cov_* `survey_cols'

* reverse so higher resp means perceived improvement

replace au02 = 4 - au02
replace au04 = 4 - au04

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
export delimited using "argentina_2012_aging_change.csv", replace

**# Bookmark 3: dependence

* ============================================================
* dependence (DEP01_01 to DEP01_08)
* yes/no needs help from a person for each basic daily activity
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more dependence
* no sentinel codes per the codebook
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols dep01_01 dep01_02 dep01_03 dep01_04 dep01_05 dep01_06 dep01_07 dep01_08

keep id cov_* `survey_cols'

* reverse so higher resp means needs help

replace dep01_01 = 3 - dep01_01
replace dep01_02 = 3 - dep01_02
replace dep01_03 = 3 - dep01_03
replace dep01_04 = 3 - dep01_04
replace dep01_05 = 3 - dep01_05
replace dep01_06 = 3 - dep01_06
replace dep01_07 = 3 - dep01_07
replace dep01_08 = 3 - dep01_08

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
export delimited using "argentina_2012_aging_dependence.csv", replace

**# Bookmark 4: instrumental

* ============================================================
* instrumental (DEP03_01 to DEP03_07)
* yes/no needs help from a person for each instrumental activity
* reversed from 1 Si 2 No to 1 No 2 Si so higher means more dependence
* no sentinel codes per the codebook
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols dep03_01 dep03_02 dep03_03 dep03_04 dep03_05 dep03_06 dep03_07

keep id cov_* `survey_cols'

* reverse so higher resp means needs help

replace dep03_01 = 3 - dep03_01
replace dep03_02 = 3 - dep03_02
replace dep03_03 = 3 - dep03_03
replace dep03_04 = 3 - dep03_04
replace dep03_05 = 3 - dep03_05
replace dep03_06 = 3 - dep03_06
replace dep03_07 = 3 - dep03_07

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
export delimited using "argentina_2012_aging_instrumental.csv", replace

**# Bookmark 5: ageism

* ============================================================
* ageism (RE01 to RE05)
* yes/no endorsement of statements on treatment of older adults
* re01, re02, re04, re05 reversed so higher means endorsing mistreatment
* re03 (older adults are respected more) kept as coded, higher already means less respect
* sentinel: 9 Ns/Nc
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols re01 re02 re03 re04 re05

keep id cov_* `survey_cols'

replace re01 = . if re01 == 9
replace re02 = . if re02 == 9
replace re03 = . if re03 == 9
replace re04 = . if re04 == 9
replace re05 = . if re05 == 9

* reverse so higher resp means more perceived mistreatment
* re03 is worded in the respect direction and is left as coded

replace re01 = 3 - re01
replace re02 = 3 - re02
replace re04 = 3 - re04
replace re05 = 3 - re05

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
export delimited using "argentina_2012_aging_ageism.csv", replace

**# Bookmark 6: satisfaction

* ============================================================
* satisfaction (SV01 to SV05)
* 1-7 agreement with life satisfaction statements, SWLS items
* higher already means more satisfaction, no reversal
* no sentinel codes per the codebook
* ============================================================

use "argentina_2012_aging_master.dta", clear

local survey_cols sv01 sv02 sv03 sv04 sv05

keep id cov_* `survey_cols'

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
export delimited using "argentina_2012_aging_satisfaction.csv", replace
