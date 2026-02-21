*** This Do File creates tables from the INEGI survey (Mexico) ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import residentes (master)
import delimited "encig2023_02_residentes_sec_2.csv", varnames(1) clear

* save as Stata for easier merging
save "encig2023_02_residentes_sec_2.dta", replace

* import quality (using)
import delimited "encig2023_01_sec1_A_3_4_5_8_9_10.csv", clear

* save as Stata for easier merging
save "encig2023_01_sec1_A_3_4_5_8_9_10.dta", replace

* load master and merge 1:1 on id_per
use "encig2023_02_residentes_sec_2.dta", clear
merge 1:1 id_per using "encig2023_01_sec1_A_3_4_5_8_9_10.dta"

* only keep merged observations
keep if _merge == 3

* drop _merge variable
drop _merge

* save merged dataset
save "mexico_2023_quality.dta", replace

* import third dataset 
import delimited "encig2023_01_sec_11.csv", varnames(1) clear

* save as Stata for easier merging
save "encig2023_01_sec_11.dta", replace

* load new master and merge 1:1 on id_per
use "mexico_2023_quality.dta", clear
merge 1:1 id_per using "encig2023_01_sec_11.dta"

* save merged dataset
save "mexico_2023_quality.dta", replace

* convert column names to lowercase
rename *, lower

* renames covariates
rename p1_1 cov_hhsize
rename sexo cov_sex
rename edad cov_age
rename niv cov_education

* turn all string-related "NA" into proper Stata-format missing values
ds, has(type string)
foreach v of varlist `r(varlist)' {
    quietly replace `v' = "" if `v' == "NA"
}

* drop old id and generate new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "mexico_2023_quality.dta", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: Public Administration

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* a1_1	a1_2 a1_3	a1_4	a1_5	a1_6	a1_7

* set up the code for long-format data from wide data
local question_cols a1_1	a1_2	a1_3	a1_4	a1_5	a1_6	a1_7

tempfile long_data
save `long_data', emptyok replace

* create long-format data from wide data
foreach var of local question_cols {
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

drop a1_1	a1_2	a1_3	a1_4	a1_5	a1_6	a1_7

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* set code 98 and 99 to missing in resp
replace resp = . if resp == 98 | resp == 99

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for public administration
export delimited using "mexico_2023_quality_administration.csv", replace

**# Bookmark #2: Worst Problems

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p3_1_01	p3_1_02	p3_1_03	p3_1_04	p3_1_05	p3_1_06	p3_1_07	p3_1_08	p3_1_09	p3_1_10	p3_1_11	p3_1_99

* set up the code for long-format data from wide data
local question_cols p3_1_01	p3_1_02	p3_1_03	p3_1_04	p3_1_05	p3_1_06	p3_1_07	p3_1_08	p3_1_09	p3_1_10	p3_1_11	p3_1_99

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p3_1_01	p3_1_02	p3_1_03	p3_1_04	p3_1_05	p3_1_06	p3_1_07	p3_1_08	p3_1_09	p3_1_10	p3_1_11	p3_1_99

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_problems.csv", replace

**# Bookmark #3: Perception Corruption

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p3_2 p3_3_01	p3_3_02	p3_3_03	p3_3_04	p3_3_05	p3_3_06	p3_3_07	p3_3_08	p3_3_09	p3_3_10	p3_3_11	p3_3_12	p3_3_13	p3_3_14	p3_3_15	p3_3_16	p3_3_17	p3_3_18	p3_3_19	p3_3_20	p3_3_21	p3_3_22	p3_3_23	p3_3_24

* set up the code for long-format data from wide data
local question_cols p3_2 p3_3_01	p3_3_02	p3_3_03	p3_3_04	p3_3_05	p3_3_06	p3_3_07	p3_3_08	p3_3_09	p3_3_10	p3_3_11	p3_3_12	p3_3_13	p3_3_14	p3_3_15	p3_3_16	p3_3_17	p3_3_18	p3_3_19	p3_3_20	p3_3_21	p3_3_22	p3_3_23	p3_3_24

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p3_2 p3_3_01	p3_3_02	p3_3_03	p3_3_04	p3_3_05	p3_3_06	p3_3_07	p3_3_08	p3_3_09	p3_3_10	p3_3_11	p3_3_12	p3_3_13	p3_3_14	p3_3_15	p3_3_16	p3_3_17	p3_3_18	p3_3_19	p3_3_20	p3_3_21	p3_3_22	p3_3_23	p3_3_24

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_corruptionperception.csv", replace

**# Bookmark #4: Basic Services - Potable Water

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_1a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p4_1_1	p4_1_2	p4_1_3	p4_1_4	p4_1_5	p4_1_6	p4_1_7	p4_1a

* set up the code for long-format data from wide data
local question_cols p4_1_1	p4_1_2	p4_1_3	p4_1_4	p4_1_5	p4_1_6	p4_1_7	p4_1a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_1_1	p4_1_2	p4_1_3	p4_1_4	p4_1_5	p4_1_6	p4_1_7	p4_1a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_water.csv", replace

**# Bookmark #5: Basic Services - Drainage

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_2a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p4_2_1	p4_2_2	p4_2_3	p4_2_4	p4_2a

* set up the code for long-format data from wide data
local question_cols p4_2_1	p4_2_2	p4_2_3	p4_2_4	p4_2a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_2_1	p4_2_2	p4_2_3	p4_2_4	p4_2a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_drainage.csv", replace

**# Bookmark #6: Basic Services - Lightning

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_3a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p4_3_1 p4_3_2 p4_3_3 p4_3a

* set up the code for long-format data from wide data
local question_cols p4_3_1 p4_3_2 p4_3_3 p4_3a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_3_1 p4_3_2 p4_3_3 p4_3a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_lightning.csv", replace

**# Bookmark #7: Basic Services - Parks

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_4a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p4_4_1 p4_4_2 p4_4_3 p4_4_4 p4_4a

* set up the code for long-format data from wide data
local question_cols p4_4_1 p4_4_2 p4_4_3 p4_4_4 p4_4a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_4_1 p4_4_2 p4_4_3 p4_4_4 p4_4a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_parks.csv", replace

**# Bookmark #8: Basic Services - Trash

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_5a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_*  p4_5_1 p4_5_2 p4_5_3 p4_5a

* set up the code for long-format data from wide data
local question_cols p4_5_1 p4_5_2 p4_5_3 p4_5a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_5_1 p4_5_2 p4_5_3 p4_5a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_trash.csv", replace

**# Bookmark #9: Basic Services - Police

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_6a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_*  p4_6_1 p4_6_2 p4_6a

* set up the code for long-format data from wide data
local question_cols p4_6_1 p4_6_2 p4_6a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_6_1 p4_6_2 p4_6a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_police.csv", replace

**# Bookmark #10: Basic Services - Roads

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_7a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_*  p4_7_1 p4_7_2 p4_7_3 p4_7_4 p4_7a

* set up the code for long-format data from wide data
local question_cols p4_7_1 p4_7_2 p4_7_3 p4_7_4 p4_7a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_7_1 p4_7_2 p4_7_3 p4_7_4 p4_7a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_roads.csv", replace

**# Bookmark #11: Basic Services - Streets

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p4_8a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_*  p4_8_1 p4_8_2 p4_8_3 p4_8_4 p4_8a

* set up the code for long-format data from wide data
local question_cols p4_8_1 p4_8_2 p4_8_3 p4_8_4 p4_8a

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p4_8_1 p4_8_2 p4_8_3 p4_8_4 p4_8a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_streets.csv", replace

**# Bookmark #12: Basic Services - Low Demand

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p5_1_09, replace
destring p5_1_10, replace
destring p5_1_11, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_1_01	p5_1_02	p5_1_03	p5_1_04	p5_1_05	p5_1_06	p5_1_07	p5_1_08	p5_1_09	p5_1_10	p5_1_11	p5_1_12

* set up the code for long-format data from wide data
local question_cols p5_1_01	p5_1_02	p5_1_03	p5_1_04	p5_1_05	p5_1_06	p5_1_07	p5_1_08	p5_1_09	p5_1_10	p5_1_11	p5_1_12

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_1_01	p5_1_02	p5_1_03	p5_1_04	p5_1_05	p5_1_06	p5_1_07	p5_1_08	p5_1_09	p5_1_10	p5_1_11	p5_1_12

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_low.csv", replace

**# Bookmark #13: Basic Services - Schooling

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p5_2a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_2_1	p5_2_2	p5_2_3	p5_2_4	p5_2_5	p5_2_6	p5_2_7	p5_2_8	p5_2_9	p5_2a

* set up the code for long-format data from wide data
local question_cols p5_2_1	p5_2_2	p5_2_3	p5_2_4	p5_2_5	p5_2_6	p5_2_7	p5_2_8	p5_2_9	p5_2a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_2_1	p5_2_2	p5_2_3	p5_2_4	p5_2_5	p5_2_6	p5_2_7	p5_2_8	p5_2_9	p5_2a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_schooling.csv", replace

**# Bookmark #14: Basic Services - University

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* destring non-numeric variables
destring p5_3a, replace

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_3_1	p5_3_2	p5_3_3	p5_3_4	p5_3_5	p5_3_6	p5_3_7	p5_3_8	p5_3a

* set up the code for long-format data from wide data
local question_cols p5_3_1	p5_3_2	p5_3_3	p5_3_4	p5_3_5	p5_3_6	p5_3_7	p5_3_8	p5_3a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_3_1	p5_3_2	p5_3_3	p5_3_4	p5_3_5	p5_3_6	p5_3_7	p5_3_8	p5_3a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_university.csv", replace

**# Bookmark #15: Basic Services - Health

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_4_01	p5_4_02	p5_4_03	p5_4_04	p5_4_05	p5_4_06	p5_4_07	p5_4_08	p5_4_09	p5_4_10	p5_4_11	p5_4a

* set up the code for long-format data from wide data
local question_cols p5_4_01	p5_4_02	p5_4_03	p5_4_04	p5_4_05	p5_4_06	p5_4_07	p5_4_08	p5_4_09	p5_4_10	p5_4_11	p5_4a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_4_01	p5_4_02	p5_4_03	p5_4_04	p5_4_05	p5_4_06	p5_4_07	p5_4_08	p5_4_09	p5_4_10	p5_4_11	p5_4a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_health.csv", replace

**# Bookmark #16: Basic Services - Well-Being

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_5_01	p5_5_02	p5_5_03	p5_5_04	p5_5_05	p5_5_06	p5_5_07	p5_5_08	p5_5_09	p5_5_10	p5_5_11	p5_5a

* set up the code for long-format data from wide data
local question_cols p5_5_01	p5_5_02	p5_5_03	p5_5_04	p5_5_05	p5_5_06	p5_5_07	p5_5_08	p5_5_09	p5_5_10	p5_5_11	p5_5a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_5_01	p5_5_02	p5_5_03	p5_5_04	p5_5_05	p5_5_06	p5_5_07	p5_5_08	p5_5_09	p5_5_10	p5_5_11	p5_5a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_wellbeing.csv", replace

**# Bookmark #17: Basic Services - Health Service

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_6_01	p5_6_02	p5_6_03	p5_6_04	p5_6_05	p5_6_06	p5_6_07	p5_6_08	p5_6_09	p5_6_10	p5_6_11	p5_6a

* set up the code for long-format data from wide data
local question_cols p5_6_01	p5_6_02	p5_6_03	p5_6_04	p5_6_05	p5_6_06	p5_6_07	p5_6_08	p5_6_09	p5_6_10	p5_6_11	p5_6a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_6_01	p5_6_02	p5_6_03	p5_6_04	p5_6_05	p5_6_06	p5_6_07	p5_6_08	p5_6_09	p5_6_10	p5_6_11	p5_6a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_healthservice.csv", replace

**# Bookmark #18: Basic Services - Well-Being Service

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_7_01	p5_7_02	p5_7_03	p5_7_04	p5_7_05	p5_7_06	p5_7_07	p5_7_08	p5_7_09	p5_7_10	p5_7_11	p5_7a

* set up the code for long-format data from wide data
local question_cols p5_7_01	p5_7_02	p5_7_03	p5_7_04	p5_7_05	p5_7_06	p5_7_07	p5_7_08	p5_7_09	p5_7_10	p5_7_11	p5_7a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_7_01	p5_7_02	p5_7_03	p5_7_04	p5_7_05	p5_7_06	p5_7_07	p5_7_08	p5_7_09	p5_7_10	p5_7_11	p5_7a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_wellbeingservice.csv", replace

**# Bookmark #19: Basic Services - Home Lightning Services

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_8_1	p5_8_2	p5_8_3	p5_8a

* set up the code for long-format data from wide data
local question_cols p5_8_1	p5_8_2	p5_8_3	p5_8a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_8_1	p5_8_2	p5_8_3	p5_8a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_homelightning.csv", replace

**# Bookmark #20: Basic Services - Transportation

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

* set up the code for long-format data from wide data
local question_cols p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_transportation.csv", replace

**# Bookmark #21: Basic Services - Buses

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

* set up the code for long-format data from wide data
local question_cols p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_9_1	p5_9_2	p5_9_3	p5_9_4	p5_9_5	p5_9_6	p5_9_7	p5_9_8	p5_9a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_buses.csv", replace

**# Bookmark #22: Basic Services - Transportation Stations

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_10_1	p5_10_2	p5_10_3	p5_10_4	p5_10_5	p5_10_6	p5_10_7	p5_10_8	p5_10a

* set up the code for long-format data from wide data
local question_cols p5_10_1	p5_10_2	p5_10_3	p5_10_4	p5_10_5	p5_10_6	p5_10_7	p5_10_8	p5_10a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_10_1	p5_10_2	p5_10_3	p5_10_4	p5_10_5	p5_10_6	p5_10_7	p5_10_8	p5_10a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_transportationstations.csv", replace

**# Bookmark #23: Basic Services - Cable Cars

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_11_1	p5_11_2	p5_11_3	p5_11_4	p5_11_5	p5_11_6	p5_11_7	p5_11_8	p5_11a

* set up the code for long-format data from wide data
local question_cols p5_11_1	p5_11_2	p5_11_3	p5_11_4	p5_11_5	p5_11_6	p5_11_7	p5_11_8	p5_11a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_11_1	p5_11_2	p5_11_3	p5_11_4	p5_11_5	p5_11_6	p5_11_7	p5_11_8	p5_11a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_cablecars.csv", replace

**# Bookmark #24: Basic Services - Trains

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_12_1	p5_12_2	p5_12_3	p5_12_4	p5_12_5	p5_12a

* set up the code for long-format data from wide data
local question_cols p5_12_1	p5_12_2	p5_12_3	p5_12_4	p5_12_5	p5_12a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_12_1	p5_12_2	p5_12_3	p5_12_4	p5_12_5	p5_12a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_trains.csv", replace

**# Bookmark #25: Basic Services - Highways

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p5_13_1	p5_13_2	p5_13_3	p5_13_4	p5_13_5	p5_13a

* set up the code for long-format data from wide data
local question_cols p5_13_1	p5_13_2	p5_13_3	p5_13_4	p5_13_5	p5_13a

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p5_13_1	p5_13_2	p5_13_3	p5_13_4	p5_13_5	p5_13a

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_highways.csv", replace

**# Bookmark #26: Corruption

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p8_1	p8_2	p8_3_1	p8_3_2	p8_3_3

* set up the code for long-format data from wide data
local question_cols p8_1	p8_2	p8_3_1	p8_3_2	p8_3_3

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p8_1	p8_2	p8_3_1	p8_3_2	p8_3_3

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_corruption.csv", replace

**# Bookmark #27: General Corruption

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p9_1 p9_7

* set up the code for long-format data from wide data
local question_cols p9_1 p9_7

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p9_1 p9_7

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_generalcorruption.csv", replace

**# Bookmark #28: Electric Government

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

* set up the code for long-format data from wide data
local question_cols p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_electricgovernment.csv", replace

**# Bookmark #29: Quality of Public Services

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

* set up the code for long-format data from wide data
local question_cols p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p10_1_1	p10_1_2	p10_1_3	p10_1_4	p10_1_5	p10_1_6

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_publicservicesquality.csv", replace

**# Bookmark #30: Institutional Confidence

* recall dataset
use "mexico_2023_quality.dta", clear

* compress data
compress

* keep only relevant variables: id, covariates, and items
keep id cov_* p11_1_01	p11_1_02	p11_1_03	p11_1_04	p11_1_05	p11_1_06	p11_1_07	p11_1_08	p11_1_09	p11_1_10	p11_1_11	p11_1_12	p11_1_13	p11_1_14	p11_1_15	p11_1_16	p11_1_17	p11_1_18	p11_1_19	p11_1_20	p11_1_21	p11_1_22	p11_1_23	p11_1_24	p11_1_25

* set up the code for long-format data from wide data
local question_cols p11_1_01	p11_1_02	p11_1_03	p11_1_04	p11_1_05	p11_1_06	p11_1_07	p11_1_08	p11_1_09	p11_1_10	p11_1_11	p11_1_12	p11_1_13	p11_1_14	p11_1_15	p11_1_16	p11_1_17	p11_1_18	p11_1_19	p11_1_20	p11_1_21	p11_1_22	p11_1_23	p11_1_24	p11_1_25

destring `question_cols', replace force

tempfile long_data
save `long_data', emptyok replace

foreach var of local question_cols {
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

drop p11_1_01	p11_1_02	p11_1_03	p11_1_04	p11_1_05	p11_1_06	p11_1_07	p11_1_08	p11_1_09	p11_1_10	p11_1_11	p11_1_12	p11_1_13	p11_1_14	p11_1_15	p11_1_16	p11_1_17	p11_1_18	p11_1_19	p11_1_20	p11_1_21	p11_1_22	p11_1_23	p11_1_24	p11_1_25

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98 | resp == 99
replace resp = . if resp == 9

order id item resp cov*, first
sort id item

export delimited using "mexico_2023_quality_confidence.csv", replace