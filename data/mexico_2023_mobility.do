*** This Stata Do File processes the mexico_2023_mobility study (ESRU-EMOVI 2023) ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\mexico_2023_mobility"

use "entrevistado_2023.dta", clear

rename *, lower

gen long id = _n

* rename covariates

rename sexo cov_sex
rename edad cov_age

* clean covariates
* cov_age is exact age 25 to 64, no sentinel codes present

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress
save "mexico_2023_master.dta", replace

**# Table 1: utilities

* ============================================================
* utilities (P26a to P26e, dwelling services at age 14)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p26a p26b p26c p26d p26e

keep id cov_* `survey_cols'

replace p26a = . if p26a == 8
replace p26b = . if p26b == 8
replace p26c = . if p26c == 8
replace p26d = . if p26d == 8
replace p26e = . if p26e == 8

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
label values resp .
drop p26a p26b p26c p26d p26e
export delimited using "mexico_2023_mobility_utilities.csv", replace

**# Table 2: rooms

* ============================================================
* rooms (P29a to P29g, dwelling spaces at age 14)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p29a p29b p29c p29d p29e p29f p29g

keep id cov_* `survey_cols'

replace p29a = . if p29a == 8
replace p29b = . if p29b == 8
replace p29c = . if p29c == 8
replace p29d = . if p29d == 8
replace p29e = . if p29e == 8
replace p29f = . if p29f == 8
replace p29g = . if p29g == 8

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
label values resp .
drop p29a p29b p29c p29d p29e p29f p29g
export delimited using "mexico_2023_mobility_rooms.csv", replace

**# Table 3: appliances

* ============================================================
* appliances (P31a to P31o, household articles at age 14)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p31a p31b p31c p31d p31e p31f p31g p31h p31i p31j p31k p31l p31m p31n p31o

keep id cov_* `survey_cols'

replace p31a = . if p31a == 8
replace p31b = . if p31b == 8
replace p31c = . if p31c == 8
replace p31d = . if p31d == 8
replace p31e = . if p31e == 8
replace p31f = . if p31f == 8
replace p31g = . if p31g == 8
replace p31h = . if p31h == 8
replace p31i = . if p31i == 8
replace p31j = . if p31j == 8
replace p31k = . if p31k == 8
replace p31l = . if p31l == 8
replace p31m = . if p31m == 8
replace p31n = . if p31n == 8
replace p31o = . if p31o == 8

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
label values resp .
drop p31a p31b p31c p31d p31e p31f p31g p31h p31i p31j p31k p31l p31m p31n p31o
export delimited using "mexico_2023_mobility_appliances.csv", replace

**# Table 4: assets

* ============================================================
* assets (P32a to P32o, origin household property and financial assets)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p32a p32b p32c p32d p32e p32f p32g p32h p32i p32j p32k p32l p32m p32n p32o

keep id cov_* `survey_cols'

replace p32a = . if p32a == 8
replace p32b = . if p32b == 8
replace p32c = . if p32c == 8
replace p32d = . if p32d == 8
replace p32e = . if p32e == 8
replace p32f = . if p32f == 8
replace p32g = . if p32g == 8
replace p32h = . if p32h == 8
replace p32i = . if p32i == 8
replace p32j = . if p32j == 8
replace p32k = . if p32k == 8
replace p32l = . if p32l == 8
replace p32m = . if p32m == 8
replace p32n = . if p32n == 8
replace p32o = . if p32o == 8

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
label values resp .
drop p32a p32b p32c p32d p32e p32f p32g p32h p32i p32j p32k p32l p32m p32n p32o
export delimited using "mexico_2023_mobility_assets.csv", replace

**# Table 5: neighborhood

* ============================================================
* neighborhood (P33a to P33i, public services in childhood neighborhood)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p33a p33b p33c p33d p33e p33f p33g p33h p33i

keep id cov_* `survey_cols'

replace p33a = . if p33a == 8
replace p33b = . if p33b == 8
replace p33c = . if p33c == 8
replace p33d = . if p33d == 8
replace p33e = . if p33e == 8
replace p33f = . if p33f == 8
replace p33g = . if p33g == 8
replace p33h = . if p33h == 8
replace p33i = . if p33i == 8

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
label values resp .
drop p33a p33b p33c p33d p33e p33f p33g p33h p33i
export delimited using "mexico_2023_mobility_neighborhood.csv", replace

**# Table 6: spaces

* ============================================================
* spaces (P94a to P94g, current dwelling spaces)
* no sentinel codes present, responses are 1/2 only
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p94a p94b p94c p94d p94e p94f p94g

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
label values resp .
drop p94a p94b p94c p94d p94e p94f p94g
export delimited using "mexico_2023_mobility_spaces.csv", replace

**# Table 7: services

* ============================================================
* services (P95a to P95e, current dwelling services)
* no sentinel codes present, responses are 1/2 only
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p95a p95b p95c p95d p95e

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
label values resp .
drop p95a p95b p95c p95d p95e
export delimited using "mexico_2023_mobility_services.csv", replace

**# Table 8: articles

* ============================================================
* articles (P96a to P96r, current household articles)
* no sentinel codes present, responses are 1/2 only
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p96a p96b p96c p96d p96e p96f p96g p96h p96i p96j p96k p96l p96m p96n p96o p96p p96q p96r

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
label values resp .
drop p96a p96b p96c p96d p96e p96f p96g p96h p96i p96j p96k p96l p96m p96n p96o p96p p96q p96r
export delimited using "mexico_2023_mobility_articles.csv", replace

**# Table 9: finances

* ============================================================
* finances (P97a to P97n, current household property and financial products)
* no sentinel codes present, responses are 1/2 only
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p97a p97b p97c p97d p97e p97f p97g p97h p97i p97j p97k p97l p97m p97n

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
label values resp .
drop p97a p97b p97c p97d p97e p97f p97g p97h p97i p97j p97k p97l p97m p97n
export delimited using "mexico_2023_mobility_finances.csv", replace

**# Table 10: community

* ============================================================
* community (P98a to P98i, public services in current neighborhood)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p98a p98b p98c p98d p98e p98f p98g p98h p98i

keep id cov_* `survey_cols'

replace p98a = . if p98a == 8
replace p98b = . if p98b == 8
replace p98c = . if p98c == 8
replace p98d = . if p98d == 8
replace p98e = . if p98e == 8
replace p98f = . if p98f == 8
replace p98g = . if p98g == 8
replace p98h = . if p98h == 8
replace p98i = . if p98i == 8

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
label values resp .
drop p98a p98b p98c p98d p98e p98f p98g p98h p98i
export delimited using "mexico_2023_mobility_community.csv", replace

**# Table 11: necessities

* ============================================================
* necessities (P105a to P105o, items necessary for dignified living)
* items l to o filtered to households with members aged 0 to 17, structural missing already system missing
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p105a p105b p105c p105d p105e p105f p105g p105h p105i p105j p105k p105l p105m p105n p105o

keep id cov_* `survey_cols'

replace p105a = . if p105a == 8
replace p105b = . if p105b == 8
replace p105c = . if p105c == 8
replace p105d = . if p105d == 8
replace p105e = . if p105e == 8
replace p105f = . if p105f == 8
replace p105g = . if p105g == 8
replace p105h = . if p105h == 8
replace p105i = . if p105i == 8
replace p105j = . if p105j == 8
replace p105k = . if p105k == 8
replace p105l = . if p105l == 8
replace p105m = . if p105m == 8
replace p105n = . if p105n == 8
replace p105o = . if p105o == 8

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
label values resp .
drop p105a p105b p105c p105d p105e p105f p105g p105h p105i p105j p105k p105l p105m p105n p105o
export delimited using "mexico_2023_mobility_necessities.csv", replace

**# Table 12: access | dropped, response categories 2 to 4 are unordered reasons

**# Table 13: mood

* ============================================================
* mood (P107a to P107g, depressive mood frequency past week)
* p107g is reverse worded, kept as recorded
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p107a p107b p107c p107d p107e p107f p107g

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
label values resp .
drop p107a p107b p107c p107d p107e p107f p107g
export delimited using "mexico_2023_mobility_mood.csv", replace

**# Table 14: anxiety

* ============================================================
* anxiety (P108a, P108b, anxiety symptom frequency past week)
* ============================================================

use "mexico_2023_master.dta", clear

local survey_cols p108a p108b

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
label values resp .
drop p108a p108b
export delimited using "mexico_2023_mobility_anxiety.csv", replace