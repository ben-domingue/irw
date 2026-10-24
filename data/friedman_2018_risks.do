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

* ZIP is coarsened to its 3-digit prefix and never published in full.
*
* The source holds full 5-digit ZIPs: 2,634 distinct values over 3,110
* respondents, so ZIP ALONE makes 72.0% of them unique -- published beside age,
* gender, race, party, hispanic, income, education and state, in a survey about
* perceived discrimination. The ZIP3 prefix takes that to 5.6% (median k = 3,
* 675 distinct geographies) and keeps the variable usable regionally. It does
* NOT make the table k-anonymous: zip3 + age + gender + race + party is still
* 89.3% unique, and state + age + gender + race + party is 41.0%, so the
* residual is the seven demographics rather than the ZIP. See
* tools/repairs/friedman_2018_zip3.py, which applied the same change to the
* already-published tables, and ben-domingue/irw#3219.
*
* string(), not a numeric prefix: a ZIP beginning with 0 is a 4-digit number,
* and taking digits off the front of 2139 gives the wrong prefix for every
* New England respondent. The published tables had exactly this defect -- 248
* of 3,110 ZIPs were served 3 or 4 characters long.
tostring zip, replace force
replace zip = substr("00000" + zip, strlen("00000" + zip) - 4, 5)
generate str3 cov_zip3 = substr(zip, 1, 3)
drop zip

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

* modify the format of the resp variable
label define likert 1 "Strongly disagree" 2 "Moderately disagree" 3 "Slightly disagree" 4 "Slightly agree" 5 "Moderately agree" 6 "Strongly agree"
encode resp, gen(resp_num) label(likert)
drop resp
rename resp_num resp

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

* modify the format of the resp variable
label define likert 1 "Strongly disagree" 2 "Moderately disagree" 3 "Slightly disagree" 4 "Slightly agree" 5 "Moderately agree" 6 "Strongly agree"
encode resp, gen(resp_num) label(likert)
drop resp
rename resp_num resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "friedman_2018_risks_discrimination.csv", replace