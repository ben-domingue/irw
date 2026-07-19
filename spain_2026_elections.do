*** This Stata Do File processes the spain_2026_elections study ***

clear all
set more off

cd "H:\My Drive\Ben Domingue\Stata Do Files\spain_2026_elections"

* read raw data (semicolon-delimited; headers are "NAME: description")
import delimited "3566_num.csv", delimiter(";") varnames(1) case(preserve) encoding("UTF-8") clear

* recover clean CIS variable names from the imported headers
foreach v of varlist _all {
    local lbl : variable label `v'
    if strpos("`lbl'", ":") > 0 {
        local newname = trim(substr("`lbl'", 1, strpos("`lbl'", ":") - 1))
        capture rename `v' `newname'
    }
}

rename *, lower
destring _all, replace force

gen long id = _n

* rename covariates (kept in every table, never counted as items)
rename sexo cov_sex
rename edad cov_age

* clean covariate sentinels (per-variable)
replace cov_age = . if inlist(cov_age, 99)

label define sex_lbl 1 "Hombre" 2 "Mujer"
label values cov_sex sex_lbl

compress
save "spain_2026_elections_master.dta", replace

******************************************
***********  Process the data ************
******************************************

**# Bookmark 1: campaign  (5 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* p2 p3_1 p3_2 p3_3 p3_4

* per-item sentinel recode
replace p2 = . if inlist(p2, 8, 9)
replace p3_1 = . if inlist(p3_1, 9)
replace p3_2 = . if inlist(p3_2, 9)
replace p3_3 = . if inlist(p3_3, 9)
replace p3_4 = . if inlist(p3_4, 9)

local question_cols p2 p3_1 p3_2 p3_3 p3_4
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
drop p2 p3_1 p3_2 p3_3 p3_4
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_campaign.csv", replace

**# Bookmark 2: leaders_campaign  (5 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* campa_lideres_1 campa_lideres_2 campa_lideres_3 campa_lideres_4 campa_lideres_5

* 1-10 scale: sentinels are 97 (no conoce), 98, 99; legitimate 8 and 9 are kept
replace campa_lideres_1 = . if inlist(campa_lideres_1, 97, 98, 99)
replace campa_lideres_2 = . if inlist(campa_lideres_2, 97, 98, 99)
replace campa_lideres_3 = . if inlist(campa_lideres_3, 97, 98, 99)
replace campa_lideres_4 = . if inlist(campa_lideres_4, 97, 98, 99)
replace campa_lideres_5 = . if inlist(campa_lideres_5, 97, 98, 99)

local question_cols campa_lideres_1 campa_lideres_2 campa_lideres_3 campa_lideres_4 campa_lideres_5
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
drop campa_lideres_1 campa_lideres_2 campa_lideres_3 campa_lideres_4 campa_lideres_5
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_leaderscampaign.csv", replace

**# Bookmark 3: moreno  (6 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* jmmoreno_1 jmmoreno_2 jmmoreno_3 jmmoreno_4 jmmoreno_5 jmmoreno_6

* 1-10 scale: sentinels are 0 (no conoce filter), 98, 99
replace jmmoreno_1 = . if inlist(jmmoreno_1, 0, 98, 99)
replace jmmoreno_2 = . if inlist(jmmoreno_2, 0, 98, 99)
replace jmmoreno_3 = . if inlist(jmmoreno_3, 0, 98, 99)
replace jmmoreno_4 = . if inlist(jmmoreno_4, 0, 98, 99)
replace jmmoreno_5 = . if inlist(jmmoreno_5, 0, 98, 99)
replace jmmoreno_6 = . if inlist(jmmoreno_6, 0, 98, 99)

local question_cols jmmoreno_1 jmmoreno_2 jmmoreno_3 jmmoreno_4 jmmoreno_5 jmmoreno_6
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
drop jmmoreno_1 jmmoreno_2 jmmoreno_3 jmmoreno_4 jmmoreno_5 jmmoreno_6
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_moreno.csv", replace

**# Bookmark 4: montero  (6 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* mjmontero_1 mjmontero_2 mjmontero_3 mjmontero_4 mjmontero_5 mjmontero_6

replace mjmontero_1 = . if inlist(mjmontero_1, 0, 98, 99)
replace mjmontero_2 = . if inlist(mjmontero_2, 0, 98, 99)
replace mjmontero_3 = . if inlist(mjmontero_3, 0, 98, 99)
replace mjmontero_4 = . if inlist(mjmontero_4, 0, 98, 99)
replace mjmontero_5 = . if inlist(mjmontero_5, 0, 98, 99)
replace mjmontero_6 = . if inlist(mjmontero_6, 0, 98, 99)

local question_cols mjmontero_1 mjmontero_2 mjmontero_3 mjmontero_4 mjmontero_5 mjmontero_6
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
drop mjmontero_1 mjmontero_2 mjmontero_3 mjmontero_4 mjmontero_5 mjmontero_6
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_montero.csv", replace

**# Bookmark 5: gavira  (6 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* mgavira_1 mgavira_2 mgavira_3 mgavira_4 mgavira_5 mgavira_6

replace mgavira_1 = . if inlist(mgavira_1, 0, 98, 99)
replace mgavira_2 = . if inlist(mgavira_2, 0, 98, 99)
replace mgavira_3 = . if inlist(mgavira_3, 0, 98, 99)
replace mgavira_4 = . if inlist(mgavira_4, 0, 98, 99)
replace mgavira_5 = . if inlist(mgavira_5, 0, 98, 99)
replace mgavira_6 = . if inlist(mgavira_6, 0, 98, 99)

local question_cols mgavira_1 mgavira_2 mgavira_3 mgavira_4 mgavira_5 mgavira_6
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
drop mgavira_1 mgavira_2 mgavira_3 mgavira_4 mgavira_5 mgavira_6
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_gavira.csv", replace

**# Bookmark 6: garcia  (6 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* jigarcia_1 jigarcia_2 jigarcia_3 jigarcia_4 jigarcia_5 jigarcia_6

replace jigarcia_1 = . if inlist(jigarcia_1, 0, 98, 99)
replace jigarcia_2 = . if inlist(jigarcia_2, 0, 98, 99)
replace jigarcia_3 = . if inlist(jigarcia_3, 0, 98, 99)
replace jigarcia_4 = . if inlist(jigarcia_4, 0, 98, 99)
replace jigarcia_5 = . if inlist(jigarcia_5, 0, 98, 99)
replace jigarcia_6 = . if inlist(jigarcia_6, 0, 98, 99)

local question_cols jigarcia_1 jigarcia_2 jigarcia_3 jigarcia_4 jigarcia_5 jigarcia_6
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
drop jigarcia_1 jigarcia_2 jigarcia_3 jigarcia_4 jigarcia_5 jigarcia_6
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_garcia.csv", replace

**# Bookmark 7: maillo  (6 items)
use "spain_2026_elections_master.dta", clear
keep id cov_* amaillo_1 amaillo_2 amaillo_3 amaillo_4 amaillo_5 amaillo_6

replace amaillo_1 = . if inlist(amaillo_1, 0, 98, 99)
replace amaillo_2 = . if inlist(amaillo_2, 0, 98, 99)
replace amaillo_3 = . if inlist(amaillo_3, 0, 98, 99)
replace amaillo_4 = . if inlist(amaillo_4, 0, 98, 99)
replace amaillo_5 = . if inlist(amaillo_5, 0, 98, 99)
replace amaillo_6 = . if inlist(amaillo_6, 0, 98, 99)

local question_cols amaillo_1 amaillo_2 amaillo_3 amaillo_4 amaillo_5 amaillo_6
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
drop amaillo_1 amaillo_2 amaillo_3 amaillo_4 amaillo_5 amaillo_6
drop if missing(item) | item == ""
drop if missing(resp)
order id item resp cov_*, first
sort id item
export delimited using "spain_2026_elections_maillo.csv", replace