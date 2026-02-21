*** This Do File creates tables from the Instituto Nacional de Estadistica survey (Guatemala) ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import household covariates dataset
import excel "ENCASBA.2024_Personas.xlsx", firstrow clear

* remove repeated ID values for non-head household members
keep if P02A05 == 1

* save cleaned household covariate dataset
save "guatemala_2024_homes.dta", replace

* clear
clear

* import the main dataset
import excel "ENCASBA.2024_Hogares.xlsx", firstrow clear

* merge household covariates dataset with survey responses dataset
merge 1:1 ID using "guatemala_2024_homes.dta"

* convert column names to lowercase
rename *, lower

* renames covariates
rename p02a03 cov_age
rename p02a02 cov_sex
rename p02a08 cov_lang
rename p02a11a cov_educ
rename total_pers cov_hhsize

* classify water survey responses
rename p04a01a1 w_p04a01a1
rename p04a01a2 w_p04a01a2
rename p04a01a3 w_p04a01a3
rename p04a01a4 w_p04a01a4
rename p04a01a5 w_p04a01a5
rename p04a01b w_p04a01b

* classify drainage survey responses
rename p04a02 d_p04a02
rename p04a02a1 d_p04a02a1
rename p04a02a2 d_p04a02a2
rename p04a02a3 d_p04a02a3
rename p04a02a4 d_p04a02a4
rename p04a02a5 d_p04a02a5
rename p04a02b d_p04a02b

* classify public lightning survey responses
rename p04a03 l_p04a03
rename p04a03a1 l_p04a03a1
rename p04a03a2 l_p04a03a2
rename p04a03a3 l_p04a03a3
rename p04a03a4 l_p04a03a4
rename p04a03b l_p04a03b

* classify parks survey responses
rename p04a04 p_p04a04
rename p04a04a1 p_p04a04a1
rename p04a04a2 p_p04a04a2
rename p04a04a3 p_p04a04a3
rename p04a04a4 p_p04a04a4
rename p04a04a5 p_p04a04a5
rename p04a04a6 p_p04a04a6
rename p04a04b p_p04a04b

* classify trash survey responses
rename p04a05a1 t_p04a05a1
rename p04a05a2 t_p04a05a2
rename p04a05a3 t_p04a05a3
rename p04a05a4 t_p04a05a4
rename p04a05b t_p04a05b

* classify avenues survey responses
rename p04a06a1 a_p04a06a1
rename p04a06a2 a_p04a06a2
rename p04a06a3 a_p04a06a3
rename p04a06a4 a_p04a06a4
rename p04a06a5 a_p04a06a5
rename p04a06a6 a_p04a06a6
rename p04a06a7 a_p04a06a7
rename p04a06a8 a_p04a06a8
rename p04a06b a_p04a06b

* classify road survey responses
rename p04a07a1 r_p04a07a1
rename p04a07a2 r_p04a07a2
rename p04a07a3 r_p04a07a3
rename p04a07a4 r_p04a07a4
rename p04a07b r_p04a07b

* classify electric energy survey responses
rename p04a08 e_p04a08
rename p04a08a1 e_p04a08a1
rename p04a08a2 e_p04a08a2
rename p04a08a3 e_p04a08a3
rename p04a08a4 e_p04a08a4
rename p04a08b e_p04a08b

* classify safety survey responses
rename p04a09a1 s_p04a09a1
rename p04a09a2 s_p04a09a2
rename p04a09a3 s_p04a09a3
rename p04a09a4 s_p04a09a4
rename p04a09a5 s_p04a09a5
rename p04a09a6 s_p04a09a6
rename p04a09a7 s_p04a09a7
rename p04a09b s_p04a09b

* classify urgencies survey responses
rename p04a10a1 u_p04a10a1
rename p04a10a2 u_p04a10a2
rename p04a10a3 u_p04a10a3
rename p04a10a4 u_p04a10a4
rename p04a10a5 u_p04a10a5
rename p04a10a6 u_p04a10a6
rename p04a10a7 u_p04a10a7
rename p04a10b u_p04a10b

* classify public education survey responses
rename p05a01 pe_p05a01
rename p05a01a1 pe_p05a01a1
rename p05a01a2 pe_p05a01a2
rename p05a01a3 pe_p05a01a3
rename p05a01a4 pe_p05a01a4
rename p05a01a5 pe_p05a01a5
rename p05a01a6 pe_p05a01a6
rename p05a01a7 pe_p05a01a7
rename p05a01a8 pe_p05a01a8
rename p05a01a9 pe_p05a01a9
rename p05a01a10 pe_p05a01a10
rename p05a01a11 pe_p05a01a11
rename p05a01b pe_p05a01b

* classify school nutrition survey responses
rename p05a01c1 sn_p05a01c1
rename p05a01c2 sn_p05a01c2
rename p05a01c3 sn_p05a01c3
rename p05a01c4 sn_p05a01c4
rename p05a01d sn_p05a01d

* classify public health survey responses
rename p05a02 ph_p05a02
rename p05a02a1 ph_p05a02a1
rename p05a02a2 ph_p05a02a2
rename p05a02a3 ph_p05a02a3
rename p05a02a4 ph_p05a02a4
rename p05a02a5 ph_p05a02a5
rename p05a02a6 ph_p05a02a6
rename p05a02a7 ph_p05a02a7
rename p05a02a8 ph_p05a02a8
rename p05a02a9 ph_p05a02a9
rename p05a02a10 ph_p05a02a10
rename p05a02a11 ph_p05a02a11
rename p05a02a12 ph_p05a02a12
rename p05a02b ph_p05a02b

* classify public clinic survey responses
rename p05a03 pc_p05a03
rename p05a03a1 pc_p05a03a1
rename p05a03a2 pc_p05a03a2
rename p05a03a3 pc_p05a03a3
rename p05a03a4 pc_p05a03a4
rename p05a03a5 pc_p05a03a5
rename p05a03a6 pc_p05a03a6
rename p05a03a7 pc_p05a03a7
rename p05a03a8 pc_p05a03a8
rename p05a03a9 pc_p05a03a9
rename p05a03a10 pc_p05a03a10
rename p05a03a11 pc_p05a03a11
rename p05a03a12 pc_p05a03a12
rename p05a03a13 pc_p05a03a13
rename p05a03b pc_p05a03b

* classify public transportation survey responses
rename p05a04a1 pt_p05a04a1
rename p05a04a2 pt_p05a04a2
rename p05a04a3 pt_p05a04a3
rename p05a04a4 pt_p05a04a4
rename p05a04a5 pt_p05a04a5
rename p05a04a6 pt_p05a04a6
rename p05a04a7 pt_p05a04a7
rename p05a04a8 pt_p05a04a8
rename p05a04a9 pt_p05a04a9
rename p05a04b pt_p05a04b

* classify country perspectives survey responses
rename p09a01 cp_p09a01
rename p09a02 cp_p09a02
rename p09a03 cp_p09a03
rename p09a04 cp_p09a04
rename p9a05a1 cp_p9a05a1
rename p9a05a2 cp_p9a05a2
rename p9a05a3 cp_p9a05a3
rename p9a05a4 cp_p9a05a4
rename p9a05a5 cp_p9a05a5
rename p9a05a6 cp_p9a05a6
rename p9a05a7 cp_p9a05a7
rename p9a05a8 cp_p9a05a8
rename p9a05a9 cp_p9a05a9
rename p9a05a10 cp_p9a05a10

* classify transparency and corruption survey responses
rename p10a01a1 tc_p10a01a1
rename p10a01a2 tc_p10a01a2
rename p10a01a3 tc_p10a01a3
rename p10a01a4 tc_p10a01a4
rename p10a01a5 tc_p10a01a5
rename p10a01a6 tc_p10a01a6
rename p10a01a7 tc_p10a01a7
rename p10a01a8 tc_p10a01a8
rename p10a01a9 tc_p10a01a9
rename p10a01a10 tc_p10a01a10
rename p10a01a11 tc_p10a01a11
rename p10a01a12a tc_p10a01a12a
rename p10a02 tc_p10a02
rename p10a03 tc_p10a03
rename p10b01 tc_p10b01
rename p10b01a tc_p10b01a
rename p10b02 tc_p10b02
rename p10b02a tc_p10b02a
rename p10b04 tc_p10b04
rename p10b05 tc_p10b05

* keep only the covariates and all response blocks
keep cov_* w_* d_* l_* p_* t_* a_* r_* e_* s_* u_* pe_* sn_* ph_* pc_* pt_* cp_* tc_*

* drop old id and generate new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "guatemala_2024_homes.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: Water

* recall dataset
use "guatemala_2024_homes.csv", clear

* compress data
compress

* keep only relevant variables: id, covariates, and water items
keep id cov_* w_p04a01a1 w_p04a01a2 w_p04a01a3 w_p04a01a4 w_p04a01a5 w_p04a01b

* set up the code for long-format data from wide data
local question_cols w_p04a01a1 w_p04a01a2 w_p04a01a3 w_p04a01a4 w_p04a01a5 w_p04a01b

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

drop w_p04a01a1 w_p04a01a2 w_p04a01a3 w_p04a01a4 w_p04a01a5 w_p04a01b

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* set code 98 to missing in resp
replace resp = . if resp == 98

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for water
export delimited using "guatemala_2024_homes_water.csv", replace

**# Bookmark #2: Drainage

* recall dataset
use "guatemala_2024_homes.csv", clear

* compress data
compress

* keep only relevant variables: id, covariates, and drainage items
keep id cov_* d_p04a02 d_p04a02a1 d_p04a02a2 d_p04a02a3 d_p04a02a4 d_p04a02a5 d_p04a02b

* set up the code for long-format data from wide data
local question_cols d_p04a02 d_p04a02a1 d_p04a02a2 d_p04a02a3 d_p04a02a4 d_p04a02a5 d_p04a02b

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

drop d_p04a02 d_p04a02a1 d_p04a02a2 d_p04a02a3 d_p04a02a4 d_p04a02a5 d_p04a02b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_drainage.csv", replace

**# Bookmark #3: Public lighting

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* l_p04a03 l_p04a03a1 l_p04a03a2 l_p04a03a3 l_p04a03a4 l_p04a03b

local question_cols l_p04a03 l_p04a03a1 l_p04a03a2 l_p04a03a3 l_p04a03a4 l_p04a03b

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

drop l_p04a03 l_p04a03a1 l_p04a03a2 l_p04a03a3 l_p04a03a4 l_p04a03b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_lighting.csv", replace

**# Bookmark #4: Parks

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* p_p04a04 p_p04a04a1 p_p04a04a2 p_p04a04a3 p_p04a04a4 p_p04a04a5 p_p04a04a6 p_p04a04b

local question_cols p_p04a04 p_p04a04a1 p_p04a04a2 p_p04a04a3 p_p04a04a4 p_p04a04a5 p_p04a04a6 p_p04a04b

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

drop p_p04a04 p_p04a04a1 p_p04a04a2 p_p04a04a3 p_p04a04a4 p_p04a04a5 p_p04a04a6 p_p04a04b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_parks.csv", replace

**# Bookmark #5: Trash collection

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* t_p04a05a1 t_p04a05a2 t_p04a05a3 t_p04a05a4 t_p04a05b

local question_cols t_p04a05a1 t_p04a05a2 t_p04a05a3 t_p04a05a4 t_p04a05b

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

drop t_p04a05a1 t_p04a05a2 t_p04a05a3 t_p04a05a4 t_p04a05b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_trash.csv", replace

**# Bookmark #6: Avenues/streets (local)

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* a_p04a06a1 a_p04a06a2 a_p04a06a3 a_p04a06a4 a_p04a06a5 a_p04a06a6 a_p04a06a7 a_p04a06a8 a_p04a06b

local question_cols a_p04a06a1 a_p04a06a2 a_p04a06a3 a_p04a06a4 a_p04a06a5 a_p04a06a6 a_p04a06a7 a_p04a06a8 a_p04a06b

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

drop a_p04a06a1 a_p04a06a2 a_p04a06a3 a_p04a06a4 a_p04a06a5 a_p04a06a6 a_p04a06a7 a_p04a06a8 a_p04a06b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_avenues.csv", replace

**# Bookmark #7: Roads / highways

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* r_p04a07a1 r_p04a07a2 r_p04a07a3 r_p04a07a4 r_p04a07b

local question_cols r_p04a07a1 r_p04a07a2 r_p04a07a3 r_p04a07a4 r_p04a07b

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

drop r_p04a07a1 r_p04a07a2 r_p04a07a3 r_p04a07a4 r_p04a07b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_roads.csv", replace

**# Bookmark #8: Electric energy

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* e_p04a08 e_p04a08a1 e_p04a08a2 e_p04a08a3 e_p04a08a4 e_p04a08b

local question_cols e_p04a08 e_p04a08a1 e_p04a08a2 e_p04a08a3 e_p04a08a4 e_p04a08b

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

drop e_p04a08 e_p04a08a1 e_p04a08a2 e_p04a08a3 e_p04a08a4 e_p04a08b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_energy.csv", replace

**# Bookmark #9: Public safety

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* s_p04a09a1 s_p04a09a2 s_p04a09a3 s_p04a09a4 s_p04a09a5 s_p04a09a6 s_p04a09a7 s_p04a09b

local question_cols s_p04a09a1 s_p04a09a2 s_p04a09a3 s_p04a09a4 s_p04a09a5 s_p04a09a6 s_p04a09a7 s_p04a09b

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

drop s_p04a09a1 s_p04a09a2 s_p04a09a3 s_p04a09a4 s_p04a09a5 s_p04a09a6 s_p04a09a7 s_p04a09b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_safety.csv", replace

**# Bookmark #10: Emergencies (firefighters / paramedics)

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* u_p04a10a1 u_p04a10a2 u_p04a10a3 u_p04a10a4 u_p04a10a5 u_p04a10a6 u_p04a10a7 u_p04a10b

local question_cols u_p04a10a1 u_p04a10a2 u_p04a10a3 u_p04a10a4 u_p04a10a5 u_p04a10a6 u_p04a10a7 u_p04a10b

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

drop u_p04a10a1 u_p04a10a2 u_p04a10a3 u_p04a10a4 u_p04a10a5 u_p04a10a6 u_p04a10a7 u_p04a10b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_emergencies.csv", replace

**# Bookmark #11: Public education

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* pe_p05a01 pe_p05a01a1 pe_p05a01a2 pe_p05a01a3 pe_p05a01a4 pe_p05a01a5 pe_p05a01a6 pe_p05a01a7 pe_p05a01a8 pe_p05a01a9 pe_p05a01a10 pe_p05a01a11 pe_p05a01b

local question_cols pe_p05a01 pe_p05a01a1 pe_p05a01a2 pe_p05a01a3 pe_p05a01a4 pe_p05a01a5 pe_p05a01a6 pe_p05a01a7 pe_p05a01a8 pe_p05a01a9 pe_p05a01a10 pe_p05a01a11 pe_p05a01b

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

drop pe_p05a01 pe_p05a01a1 pe_p05a01a2 pe_p05a01a3 pe_p05a01a4 pe_p05a01a5 pe_p05a01a6 pe_p05a01a7 pe_p05a01a8 pe_p05a01a9 pe_p05a01a10 pe_p05a01a11 pe_p05a01b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_publiceducation.csv", replace

**# Bookmark #12: School nutrition

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* sn_p05a01c1 sn_p05a01c2 sn_p05a01c3 sn_p05a01c4 sn_p05a01d

local question_cols sn_p05a01c1 sn_p05a01c2 sn_p05a01c3 sn_p05a01c4 sn_p05a01d

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

drop sn_p05a01c1 sn_p05a01c2 sn_p05a01c3 sn_p05a01c4 sn_p05a01d

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_nutrition.csv", replace

**# Bookmark #13: Public health center

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* ph_p05a02 ph_p05a02a1 ph_p05a02a2 ph_p05a02a3 ph_p05a02a4 ph_p05a02a5 ph_p05a02a6 ph_p05a02a7 ph_p05a02a8 ph_p05a02a9 ph_p05a02a10 ph_p05a02a11 ph_p05a02a12 ph_p05a02b

local question_cols ph_p05a02 ph_p05a02a1 ph_p05a02a2 ph_p05a02a3 ph_p05a02a4 ph_p05a02a5 ph_p05a02a6 ph_p05a02a7 ph_p05a02a8 ph_p05a02a9 ph_p05a02a10 ph_p05a02a11 ph_p05a02a12 ph_p05a02b

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

drop ph_p05a02 ph_p05a02a1 ph_p05a02a2 ph_p05a02a3 ph_p05a02a4 ph_p05a02a5 ph_p05a02a6 ph_p05a02a7 ph_p05a02a8 ph_p05a02a9 ph_p05a02a10 ph_p05a02a11 ph_p05a02a12 ph_p05a02b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_publichealth.csv", replace

**# Bookmark #14: Public clinic / hospital

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* pc_p05a03 pc_p05a03a1 pc_p05a03a2 pc_p05a03a3 pc_p05a03a4 pc_p05a03a5 pc_p05a03a6 pc_p05a03a7 pc_p05a03a8 pc_p05a03a9 pc_p05a03a10 pc_p05a03a11 pc_p05a03a12 pc_p05a03a13 pc_p05a03b

local question_cols pc_p05a03 pc_p05a03a1 pc_p05a03a2 pc_p05a03a3 pc_p05a03a4 pc_p05a03a5 pc_p05a03a6 pc_p05a03a7 pc_p05a03a8 pc_p05a03a9 pc_p05a03a10 pc_p05a03a11 pc_p05a03a12 pc_p05a03a13 pc_p05a03b

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

drop pc_p05a03 pc_p05a03a1 pc_p05a03a2 pc_p05a03a3 pc_p05a03a4 pc_p05a03a5 pc_p05a03a6 pc_p05a03a7 pc_p05a03a8 pc_p05a03a9 pc_p05a03a10 pc_p05a03a11 pc_p05a03a12 pc_p05a03a13 pc_p05a03b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_publicclinic.csv", replace

**# Bookmark #15: Public transportation

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* pt_p05a04a1 pt_p05a04a2 pt_p05a04a3 pt_p05a04a4 pt_p05a04a5 pt_p05a04a6 pt_p05a04a7 pt_p05a04a8 pt_p05a04a9 pt_p05a04b

local question_cols pt_p05a04a1 pt_p05a04a2 pt_p05a04a3 pt_p05a04a4 pt_p05a04a5 pt_p05a04a6 pt_p05a04a7 pt_p05a04a8 pt_p05a04a9 pt_p05a04b

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

drop pt_p05a04a1 pt_p05a04a2 pt_p05a04a3 pt_p05a04a4 pt_p05a04a5 pt_p05a04a6 pt_p05a04a7 pt_p05a04a8 pt_p05a04a9 pt_p05a04b

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_transport.csv", replace

**# Bookmark #16: Country perspectives

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* cp_p09a01 cp_p09a02 cp_p09a03 cp_p09a04 cp_p9a05a1 cp_p9a05a2 cp_p9a05a3 cp_p9a05a4 cp_p9a05a5 cp_p9a05a6 cp_p9a05a7 cp_p9a05a8 cp_p9a05a9 cp_p9a05a10

local question_cols cp_p09a01 cp_p09a02 cp_p09a03 cp_p09a04 cp_p9a05a1 cp_p9a05a2 cp_p9a05a3 cp_p9a05a4 cp_p9a05a5 cp_p9a05a6 cp_p9a05a7 cp_p9a05a8 cp_p9a05a9 cp_p9a05a10

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

drop cp_p09a01 cp_p09a02 cp_p09a03 cp_p09a04 cp_p9a05a1 cp_p9a05a2 cp_p9a05a3 cp_p9a05a4 cp_p9a05a5 cp_p9a05a6 cp_p9a05a7 cp_p9a05a8 cp_p9a05a9 cp_p9a05a10

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98
replace resp = . if resp == 97
replace resp = . if resp == 99

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_country.csv", replace

**# Bookmark #17: Transparency and corruption

* recall dataset
use "guatemala_2024_homes.csv", clear

compress

keep id cov_* tc_p10a01a1 tc_p10a01a2 tc_p10a01a3 tc_p10a01a4 tc_p10a01a5 tc_p10a01a6 tc_p10a01a7 tc_p10a01a8 tc_p10a01a9 tc_p10a01a10 tc_p10a01a11 tc_p10a01a12a tc_p10a02 tc_p10a03 tc_p10b01 tc_p10b01a tc_p10b02 tc_p10b02a tc_p10b04 tc_p10b05

local question_cols tc_p10a01a1 tc_p10a01a2 tc_p10a01a3 tc_p10a01a4 tc_p10a01a5 tc_p10a01a6 tc_p10a01a7 tc_p10a01a8 tc_p10a01a9 tc_p10a01a10 tc_p10a01a11 tc_p10a01a12a tc_p10a02 tc_p10a03 tc_p10b01 tc_p10b01a tc_p10b02 tc_p10b02a tc_p10b04 tc_p10b05

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

drop tc_p10a01a1 tc_p10a01a2 tc_p10a01a3 tc_p10a01a4 tc_p10a01a5 tc_p10a01a6 tc_p10a01a7 tc_p10a01a8 tc_p10a01a9 tc_p10a01a10 tc_p10a01a11 tc_p10a01a12a tc_p10a02 tc_p10a03 tc_p10b01 tc_p10b01a tc_p10b02 tc_p10b02a tc_p10b04 tc_p10b05

drop if missing(item) | item == ""

gen resp2 = resp
drop resp
rename resp2 resp

replace resp = . if resp == 98
replace resp = . if resp == 97
replace resp = . if resp == 99

order id item resp cov*, first
sort id item

export delimited using "guatemala_2024_homes_transparency.csv", replace