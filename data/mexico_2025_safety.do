*** This Do File creates tables from the INEGI survey (Mexico) ***

* clear memory
clear

* 2024 Q1
import delimited "conjunto_de_datos_ensu_cb_0324.csv", clear varnames(1) case(lower)
gen id_quarter = 1
gen id_year = 2024
save "q1_2024_temp.dta", replace

* 2024 Q2
import delimited "conjunto_de_datos_ensu_cb_0624.csv", clear varnames(1) case(lower)
gen id_quarter = 2
gen id_year = 2024
save "q2_2024_temp.dta", replace

* 2024 Q3
import delimited "conjunto_de_datos_ensu_cb_0924.csv", clear varnames(1) case(lower)
gen id_quarter = 3
gen id_year = 2024
save "q3_2024_temp.dta", replace

* 2024 Q4
import delimited "conjunto_de_datos_ensu_cb_1224.csv", clear varnames(1) case(lower)
gen id_quarter = 4
gen id_year = 2024
save "q4_2024_temp.dta", replace

* 2025 Q1
import delimited "conjunto_de_datos_ensu_cb_0325.csv", clear varnames(1) case(lower)
gen id_quarter = 1
gen id_year = 2025
save "q1_2025_temp.dta", replace

* 2025 Q2
import delimited "conjunto_de_datos_ensu_cb_0625.csv", clear varnames(1) case(lower)
gen id_quarter = 2
gen id_year = 2025
save "q2_2025_temp.dta", replace

* 2025 Q3
import delimited "conjunto_de_datos_ensu_cb_0925.csv", clear varnames(1) case(lower)
gen id_quarter = 3
gen id_year = 2025
save "q3_2025_temp.dta", replace

* 2025 Q4
import delimited "conjunto_de_datos_ensu_cb_1225.csv", clear varnames(1) case(lower)
gen id_quarter = 4
gen id_year = 2025
save "q4_2025_temp.dta", replace

* append all quarters and years
use "q1_2024_temp.dta", clear
append using "q2_2024_temp.dta", force
append using "q3_2024_temp.dta", force
append using "q4_2024_temp.dta", force
append using "q1_2025_temp.dta", force
append using "q2_2025_temp.dta", force
append using "q3_2025_temp.dta", force
append using "q4_2025_temp.dta", force

* convert all string "NA" to proper missing
ds, has(type string)
foreach v of varlist `r(varlist)' {
    quietly replace `v' = "" if `v' == "NA"
}

* destring all bp variables (they may come in as string)
quietly destring bp*, replace

* convert column names to lowercase
rename *, lower

* rename covariates
rename sexo cov_sex
rename edad cov_age

* ============================================================
* MISSING VALUE CLEANING — variable by variable, all quarters
* ============================================================

* ----------------------------
* SECTION I — ALL QUARTERS
* ----------------------------

* bp1_1: city security perception (1=seguro, 2=inseguro)
replace bp1_1 = . if bp1_1 == 9

* bp1_2_01 to bp1_2_12: place-level security (1=seguro, 2=inseguro, 3=no aplica)
replace bp1_2_01 = . if bp1_2_01 == 3 | bp1_2_01 == 9
replace bp1_2_02 = . if bp1_2_02 == 3 | bp1_2_02 == 9
replace bp1_2_03 = . if bp1_2_03 == 3 | bp1_2_03 == 9
replace bp1_2_04 = . if bp1_2_04 == 3 | bp1_2_04 == 9
replace bp1_2_05 = . if bp1_2_05 == 3 | bp1_2_05 == 9
replace bp1_2_06 = . if bp1_2_06 == 3 | bp1_2_06 == 9
replace bp1_2_07 = . if bp1_2_07 == 3 | bp1_2_07 == 9
replace bp1_2_08 = . if bp1_2_08 == 3 | bp1_2_08 == 9
replace bp1_2_09 = . if bp1_2_09 == 3 | bp1_2_09 == 9
replace bp1_2_10 = . if bp1_2_10 == 3 | bp1_2_10 == 9
replace bp1_2_11 = . if bp1_2_11 == 3 | bp1_2_11 == 9
replace bp1_2_12 = . if bp1_2_12 == 3 | bp1_2_12 == 9

* bp1_3: 12-month outlook (1-4 scale)
replace bp1_3 = . if bp1_3 == 9

* bp1_4_1 to bp1_4_8: witnessed situations nearby (1=si, 2=no)
replace bp1_4_1 = . if bp1_4_1 == 9
replace bp1_4_2 = . if bp1_4_2 == 9
replace bp1_4_3 = . if bp1_4_3 == 9
replace bp1_4_4 = . if bp1_4_4 == 9
replace bp1_4_5 = . if bp1_4_5 == 9
replace bp1_4_6 = . if bp1_4_6 == 9
replace bp1_4_7 = . if bp1_4_7 == 9
replace bp1_4_8 = . if bp1_4_8 == 9

* bp1_5_1 to bp1_5_5: habit changes due to fear (1=si, 2=no, 3=no aplica)
replace bp1_5_1 = . if bp1_5_1 == 3 | bp1_5_1 == 9
replace bp1_5_2 = . if bp1_5_2 == 3 | bp1_5_2 == 9
replace bp1_5_3 = . if bp1_5_3 == 3 | bp1_5_3 == 9
replace bp1_5_4 = . if bp1_5_4 == 3 | bp1_5_4 == 9
replace bp1_5_5 = . if bp1_5_5 == 3 | bp1_5_5 == 9

* bp1_6_01 to bp1_6_13, bp1_6_99: news sources Q1/Q3 (0/1 binary) — no missing codes
* no action needed

* bp1_6_1 to bp1_6_8: victimization module Q2/Q4 (1=si, 2=no, 9=missing)
* note: 2024 Q2 only has items 1-6; items 7-8 added in 2025
capture replace bp1_6_1 = . if bp1_6_1 == 9
capture replace bp1_6_2 = . if bp1_6_2 == 9
capture replace bp1_6_3 = . if bp1_6_3 == 9
capture replace bp1_6_4 = . if bp1_6_4 == 9
capture replace bp1_6_5 = . if bp1_6_5 == 9
capture replace bp1_6_6 = . if bp1_6_6 == 9
capture replace bp1_6_7 = . if bp1_6_7 == 9
capture replace bp1_6_8 = . if bp1_6_8 == 9

* bp1_7_1 to bp1_7_6: identifies authority (1=si, 2=no, 3=no aplica)
replace bp1_7_1 = . if bp1_7_1 == 3 | bp1_7_1 == 9
replace bp1_7_2 = . if bp1_7_2 == 3 | bp1_7_2 == 9
replace bp1_7_3 = . if bp1_7_3 == 3 | bp1_7_3 == 9
replace bp1_7_4 = . if bp1_7_4 == 3 | bp1_7_4 == 9
replace bp1_7_5 = . if bp1_7_5 == 3 | bp1_7_5 == 9
replace bp1_7_6 = . if bp1_7_6 == 3 | bp1_7_6 == 9

* bp1_8_1 to bp1_8_6: authority effectiveness (1-4 scale)
replace bp1_8_1 = . if bp1_8_1 == 9
replace bp1_8_2 = . if bp1_8_2 == 9
replace bp1_8_3 = . if bp1_8_3 == 9
replace bp1_8_4 = . if bp1_8_4 == 9
replace bp1_8_5 = . if bp1_8_5 == 9
replace bp1_8_6 = . if bp1_8_6 == 9

* bp1_9_1 to bp1_9_6: trust in authority (1-4 scale)
replace bp1_9_1 = . if bp1_9_1 == 9
replace bp1_9_2 = . if bp1_9_2 == 9
replace bp1_9_3 = . if bp1_9_3 == 9
replace bp1_9_4 = . if bp1_9_4 == 9
replace bp1_9_5 = . if bp1_9_5 == 9
replace bp1_9_6 = . if bp1_9_6 == 9

* ----------------------------
* SECTION II — ALL QUARTERS
* ----------------------------

* bp2_1: had any direct conflict (1=si, 2=no)
replace bp2_1 = . if bp2_1 == 9

* bp2_2_01 to bp2_2_18: conflict type (0/1 binary) — no missing codes
* no action needed

* bp2_3_1 to bp2_3_7: with whom conflict (0/1 binary, 9=no especificado)
replace bp2_3_1 = . if bp2_3_1 == 9
replace bp2_3_2 = . if bp2_3_2 == 9
replace bp2_3_3 = . if bp2_3_3 == 9
replace bp2_3_4 = . if bp2_3_4 == 9
replace bp2_3_5 = . if bp2_3_5 == 9
replace bp2_3_6 = . if bp2_3_6 == 9
replace bp2_3_7 = . if bp2_3_7 == 9

* bp2_4_01 to bp2_4_11: conflict consequences (0/1 binary) — no missing codes
* no action needed

* ----------------------------
* SECTION III — ALL QUARTERS
* ----------------------------

* bp3_1_01 to bp3_1_16, bp3_1_99: city problems (0/1 binary) — no missing codes
* no action needed

* bp3_2: government effectiveness (1-4 scale)
replace bp3_2 = . if bp3_2 == 9

* bp3_2a: knows about prevention programs (1=si, 2=no)
replace bp3_2a = . if bp3_2a == 9

* bp3_3: did tramite with public servant — Q2/Q4 only (1=si, 2=no)
capture replace bp3_3 = . if bp3_3 == 9

* bp3_4: public servant solicited bribe — Q2/Q4 only (1=si, 2=no)
capture replace bp3_4 = . if bp3_4 == 9

* bp3_5: contact with security police — Q2/Q4 only (1=si, 2=no)
capture replace bp3_5 = . if bp3_5 == 9

* bp3_6: police solicited bribe — Q2/Q4 only (1=si, 2=no)
capture replace bp3_6 = . if bp3_6 == 9

* ----------------------------
* SECTION IV — VARIES BY QUARTER
* ----------------------------

* bp4_1_1 to bp4_1_3: trust in government levels
* 2024 Q1 special case: scale is 0-10, so 9 is VALID — only 99 = missing
replace bp4_1_1 = . if bp4_1_1 == 99 & id_year == 2024 & id_quarter == 1
replace bp4_1_2 = . if bp4_1_2 == 99 & id_year == 2024 & id_quarter == 1
replace bp4_1_3 = . if bp4_1_3 == 99 & id_year == 2024 & id_quarter == 1
* all other quarters with trust variables: scale is 1-4, only 9 = missing
replace bp4_1_1 = . if bp4_1_1 == 9 & !(id_year == 2024 & id_quarter == 1)
replace bp4_1_2 = . if bp4_1_2 == 9 & !(id_year == 2024 & id_quarter == 1)
replace bp4_1_3 = . if bp4_1_3 == 9 & !(id_year == 2024 & id_quarter == 1)

* Q3 Section V: trust in government levels (1-4 scale)
* applies to 2024 Q3 and 2025 Q3
capture replace bp5_1_1 = . if bp5_1_1 == 9
capture replace bp5_1_2 = . if bp5_1_2 == 9
capture replace bp5_1_3 = . if bp5_1_3 == 9

* Q2/Q4 Section IV: harassment in public spaces (1=si, 2=no)
* applies to 2024 Q2, 2024 Q4, 2025 Q2, 2025 Q4
capture replace bp4_1_4 = . if bp4_1_4 == 9
capture replace bp4_1_5 = . if bp4_1_5 == 9
capture replace bp4_1_6 = . if bp4_1_6 == 9
capture replace bp4_1_7 = . if bp4_1_7 == 9
capture replace bp4_1_8 = . if bp4_1_8 == 9
capture replace bp4_1_9 = . if bp4_1_9 == 9

* Q3 Section IV: domestic/family violence (1=si, 2=no)
* applies to 2024 Q3 and 2025 Q3
capture replace bp4_3_1 = . if bp4_3_1 == 9
capture replace bp4_3_2 = . if bp4_3_2 == 9
capture replace bp4_3_3 = . if bp4_3_3 == 9
capture replace bp4_3_4 = . if bp4_3_4 == 9
capture replace bp4_3_5 = . if bp4_3_5 == 9
capture replace bp4_3_6 = . if bp4_3_6 == 9

* save cleaned wide dataset
save "mexico_safety.dta", replace

* create Q1 2025 dataset
use "mexico_safety.dta", clear
keep if id_year == 2025 & id_quarter == 1
gen id = _n
order id cov*, first
save "mexico_safety_1q2025.dta", replace

* create Q2 2025 dataset
use "mexico_safety.dta", clear
keep if id_year == 2025 & id_quarter == 2
gen id = _n
order id cov*, first
save "mexico_safety_2q2025.dta", replace

* create Q3 2025 dataset
use "mexico_safety.dta", clear
keep if id_year == 2025 & id_quarter == 3
gen id = _n
order id cov*, first
save "mexico_safety_3q2025.dta", replace

* create Q4 2025 dataset
use "mexico_safety.dta", clear
keep if id_year == 2025 & id_quarter == 4
gen id = _n
order id cov*, first
save "mexico_safety_4q2025.dta", replace

* create Q1 2024 dataset
use "mexico_safety.dta", clear
keep if id_year == 2024 & id_quarter == 1
gen id = _n
order id cov*, first
save "mexico_safety_1q2024.dta", replace

* create Q2 2024 dataset
use "mexico_safety.dta", clear
keep if id_year == 2024 & id_quarter == 2
gen id = _n
order id cov*, first
save "mexico_safety_2q2024.dta", replace

* create Q3 2024 dataset
use "mexico_safety.dta", clear
keep if id_year == 2024 & id_quarter == 3
gen id = _n
order id cov*, first
save "mexico_safety_3q2024.dta", replace

* create Q4 2024 dataset
use "mexico_safety.dta", clear
keep if id_year == 2024 & id_quarter == 4
gen id = _n
order id cov*, first
save "mexico_safety_4q2024.dta", replace

**# Bookmark #1: Q1 2025 Public Safety Perception

use "mexico_safety_1q2025.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2025_q1safety_perception.csv", replace

**# Bookmark #2: Q1 2025 Conflicts

use "mexico_safety_1q2025.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2025_q1safety_conflicts.csv", replace

**# Bookmark #3: Q1 2025 Government Performance

use "mexico_safety_1q2025.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

sort id item

export delimited using "mexico_2025_q1safety_govperformance.csv", replace

**# Bookmark #4: Q1 2025 Trust in Government

use "mexico_safety_1q2025.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3

sort id item

export delimited using "mexico_2025_q1safety_govtrust.csv", replace

**# Bookmark #5: Q2 2025 Public Safety Perception

use "mexico_safety_2q2025.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2025_q2safety_perception.csv", replace

**# Bookmark #6: Q2 2025 Conflicts

use "mexico_safety_2q2025.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2025_q2conflicts.csv", replace

**# Bookmark #7: Q2 2025 Government Performance

use "mexico_safety_2q2025.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

sort id item

export delimited using "mexico_2025_q2safety_govperformance.csv", replace

**# Bookmark #8: Q2 2025 Harassment

use "mexico_safety_2q2025.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

sort id item

export delimited using "mexico_2025_q2harassment.csv", replace

**# Bookmark #9: Q3 2025 Public Safety Perception

use "mexico_safety_3q2025.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2025_q3safety_perception.csv", replace

**# Bookmark #10: Q3 2025 Conflicts

use "mexico_safety_3q2025.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2025_q3safety_conflicts.csv", replace

**# Bookmark #11: Q3 2025 Government Performance

use "mexico_safety_3q2025.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

sort id item

export delimited using "mexico_2025_q3safety_govperformance.csv", replace

**# Bookmark #12: Q3 2025 Family Violence

use "mexico_safety_3q2025.dta", clear

keep id cov* bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

compress

local question_cols bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

sort id item

export delimited using "mexico_2025_q3safety_violence.csv", replace

**# Bookmark #13: Q3 2025 Trust in Government

use "mexico_safety_3q2025.dta", clear

keep id cov* bp5_1_1 bp5_1_2 bp5_1_3

compress

local question_cols bp5_1_1 bp5_1_2 bp5_1_3

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp5_1_1 bp5_1_2 bp5_1_3

sort id item

export delimited using "mexico_2025_q3safety_govtrust.csv", replace

**# Bookmark #14: Q4 2025 Public Safety Perception

use "mexico_safety_4q2025.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2025_q4safety_perception.csv", replace

**# Bookmark #15: Q4 2025 Conflicts

use "mexico_safety_4q2025.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2025_q4safety_conflicts.csv", replace

**# Bookmark #16: Q4 2025 Government Performance

use "mexico_safety_4q2025.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

sort id item

export delimited using "mexico_2025_q4safety_govperformance.csv", replace

**# Bookmark #17: Q4 2025 Harassment

use "mexico_safety_4q2025.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

sort id item

export delimited using "mexico_2025_q4safety_harassment.csv", replace

**# Bookmark #18: Q1 2024 Public Safety Perception

use "mexico_safety_1q2024.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2024_q1safety_perception.csv", replace

**# Bookmark #19: Q1 2024 Conflicts

use "mexico_safety_1q2024.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2024_q1safety_conflicts.csv", replace

**# Bookmark #20: Q1 2024 Government Performance

use "mexico_safety_1q2024.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

sort id item

export delimited using "mexico_2024_q1safety_govperformance.csv", replace

**# Bookmark #21: Q1 2024 Trust in Government

use "mexico_safety_1q2024.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3

sort id item

export delimited using "mexico_2024_q1safety_govtrust.csv", replace

**# Bookmark #22: Q2 2024 Public Safety Perception

use "mexico_safety_2q2024.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2024_q2safety_perception.csv", replace

**# Bookmark #23: Q2 2024 Conflicts

use "mexico_safety_2q2024.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2024_q2safety_conflicts.csv", replace

**# Bookmark #24: Q2 2024 Government Performance

use "mexico_safety_2q2024.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

sort id item

export delimited using "mexico_2024_q2safety_govperformance.csv", replace

**# Bookmark #25: Q2 2024 Harassment

use "mexico_safety_2q2024.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

sort id item

export delimited using "mexico_2024_q2safety_harassment.csv", replace

**# Bookmark #26: Q3 2024 Public Safety Perception

use "mexico_safety_3q2024.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_01 bp1_6_02 bp1_6_03 bp1_6_04 bp1_6_05 bp1_6_06 bp1_6_07 bp1_6_08 bp1_6_09 bp1_6_10 bp1_6_11 bp1_6_12 bp1_6_13 bp1_6_99 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2024_q3safety_perception.csv", replace

**# Bookmark #27: Q3 2024 Conflicts

use "mexico_safety_3q2024.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2024_q3safety_conflicts.csv", replace

**# Bookmark #28: Q3 2024 Government Performance

use "mexico_safety_3q2024.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a

sort id item

export delimited using "mexico_2024_q3safety_govperformance.csv", replace

**# Bookmark #29: Q3 2024 Family Violence

use "mexico_safety_3q2024.dta", clear

keep id cov* bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

compress

local question_cols bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_3_1 bp4_3_2 bp4_3_3 bp4_3_4 bp4_3_5 bp4_3_6

sort id item

export delimited using "mexico_2024_q3safety_violence.csv", replace

**# Bookmark #30: Q3 2024 Trust in Government

use "mexico_safety_3q2024.dta", clear

keep id cov* bp5_1_1 bp5_1_2 bp5_1_3

compress

local question_cols bp5_1_1 bp5_1_2 bp5_1_3

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp5_1_1 bp5_1_2 bp5_1_3

sort id item

export delimited using "mexico_2024_q3safety_govtrust.csv", replace

**# Bookmark #31: Q4 2024 Public Safety Perception

use "mexico_safety_4q2024.dta", clear

keep id cov* bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

compress

local question_cols bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp1_1 bp1_2_01 bp1_2_02 bp1_2_03 bp1_2_04 bp1_2_05 bp1_2_06 bp1_2_07 bp1_2_08 bp1_2_09 bp1_2_10 bp1_2_11 bp1_2_12 bp1_3 bp1_4_1 bp1_4_2 bp1_4_3 bp1_4_4 bp1_4_5 bp1_4_6 bp1_4_7 bp1_4_8 bp1_5_1 bp1_5_2 bp1_5_3 bp1_5_4 bp1_5_5 bp1_6_1 bp1_6_2 bp1_6_3 bp1_6_4 bp1_6_5 bp1_6_6 bp1_6_7 bp1_6_8 bp1_7_1 bp1_7_2 bp1_7_3 bp1_7_4 bp1_7_5 bp1_7_6 bp1_8_1 bp1_8_2 bp1_8_3 bp1_8_4 bp1_8_5 bp1_8_6 bp1_9_1 bp1_9_2 bp1_9_3 bp1_9_4 bp1_9_5 bp1_9_6

sort id item

export delimited using "mexico_2024_q4safety_perception.csv", replace

**# Bookmark #32: Q4 2024 Conflicts

use "mexico_safety_4q2024.dta", clear

keep id cov* bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

compress

local question_cols bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp2_1 bp2_2_01 bp2_2_02 bp2_2_03 bp2_2_04 bp2_2_05 bp2_2_06 bp2_2_07 bp2_2_08 bp2_2_09 bp2_2_10 bp2_2_11 bp2_2_12 bp2_2_13 bp2_2_14 bp2_2_15 bp2_2_16 bp2_2_17 bp2_2_18 bp2_3_1 bp2_3_2 bp2_3_3 bp2_3_4 bp2_3_5 bp2_3_6 bp2_3_7 bp2_4_01 bp2_4_02 bp2_4_03 bp2_4_04 bp2_4_05 bp2_4_06 bp2_4_07 bp2_4_08 bp2_4_09 bp2_4_10 bp2_4_11

sort id item

export delimited using "mexico_2024_q4safety_conflicts.csv", replace

**# Bookmark #33: Q4 2024 Government Performance

use "mexico_safety_4q2024.dta", clear

keep id cov* bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

compress

local question_cols bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp3_1_01 bp3_1_02 bp3_1_03 bp3_1_04 bp3_1_05 bp3_1_06 bp3_1_07 bp3_1_08 bp3_1_09 bp3_1_10 bp3_1_11 bp3_1_12 bp3_1_13 bp3_1_14 bp3_1_15 bp3_1_16 bp3_1_99 bp3_2 bp3_2a bp3_3 bp3_4 bp3_5 bp3_6

sort id item

export delimited using "mexico_2024_q4safety_govperformance.csv", replace

**# Bookmark #34: Q4 2024 Harassment

use "mexico_safety_4q2024.dta", clear

keep id cov* bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

compress

local question_cols bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

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

drop if missing(item) | item == ""

drop if missing(resp)

drop bp4_1_1 bp4_1_2 bp4_1_3 bp4_1_4 bp4_1_5 bp4_1_6 bp4_1_7 bp4_1_8 bp4_1_9

sort id item

export delimited using "mexico_2024_q4safety_harassment.csv", replace