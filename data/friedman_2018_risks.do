*** note: we only took the 3 selected response tables, see https://github.com/ben-domingue/irw/issues/1177#issuecomment-3709007325

*** This Do File creates tables from the Replication Data for: Priorities for Preventive Action: Explaining Americans' Divergent Reactions to 100 Public Risks study ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import the main dataset
use "Risk_Data_Base.dta", clear

* compress file so the following codes run faster
compress
save, replace

* convert column names to lowercase
rename *, lower

* renames covariates
rename age cov_age
rename gender cov_gender
rename durationinseconds cov_sduration
rename education cov_education
rename enddate cov_enddate
rename hispanic cov_hispanic
rename income cov_income
rename democrat cov_democrat
rename independent cov_independent
rename party cov_party
rename race cov_race
rename republican cov_republican
rename startdate cov_startdate
rename state cov_state
rename zip cov_zip

* convert start dates of survey response to standard format, which is the time of the data point in UNIX format
generate double cov_startdate_stata = clock(cov_startdate, "MDYhm")
format cov_startdate_stata %tc
generate double cov_startdate_unix = (cov_startdate_stata - tC(01jan1970 00:00:00)) / 1000

* convert end dates of survey response to standard format, which is the time of the data point in UNIX format
generate double cov_enddate_stata = clock(cov_enddate, "MDYhm")
format cov_enddate_stata %tc
generate double cov_enddate_unix = (cov_enddate_stata - tC(01jan1970 00:00:00)) / 1000

* drop irrelevant time covariates
drop cov_enddate_stata cov_startdate_stata cov_enddate cov_startdate

* rename time covariates
rename cov_enddate_unix cov_enddate
rename cov_startdate_unix cov_startdate

* order seconds, start date, and enddate sequentially
order cov_sduration cov_startdate cov_enddate, first

* drop old id
drop responseid

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "friedman_2018_risks.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: likert-scale responses to the role of the government on people's lives and restrictions

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* charm climchoi cprotect iinterests iprivacy iprotect

* set up the code for long-format data from wide data
local question_cols charm climchoi cprotect iinterests iprivacy iprotect

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

drop charm climchoi cprotect iinterests iprivacy iprotect

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "friedman_2018_risks_government.csv", replace

**# Bookmark #2: likert-scale responses to the presence of discrimination, inequality, and justice in society currently

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ediscrim eradeq ewealth hequal hfeminin hrevdis2

* set up the code for long-format data from wide data
local question_cols ediscrim eradeq ewealth hequal hfeminin hrevdis2

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

drop ediscrim eradeq ewealth hequal hfeminin hrevdis2

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "friedman_2018_risks_discrimination.csv", replace

**# Bookmark #3: yes/no responses to general science-related questions such as whether antibiotics kill viruses or whether electrons are smaller than atoms

* recall dataset
use "friedman_2018_risks.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

* set up the code for long-format data from wide data
local question_cols osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

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

drop osc_anti osc_atoms osc_copern osc_gas osc_lasers osc_radio osc_year

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "friedman_2018_risks_science.csv", replace
