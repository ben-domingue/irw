*** This Do File creates tables from the United States National Health Measurement Study, 2005-2006 (ICPSR 23263) study ***

* clear
clear

* import the main dataset and convert to csv
import delimited "23263-0001-Data.tsv", clear

* convert column names to lowercase
rename *, lower

* drop old id
drop caseid

* renames covariates
rename age cov_age
rename sex cov_sex
rename race cov_race
rename married cov_married
rename educ cov_educ

* implement aggressive encoding to N/As
mvdecode _all, mv(-1)
mvdecode _all, mv(-2)

* adds new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "fryback_2009_health.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: Psychological well-being scales - purpose

* recall dataset
use "fryback_2009_health.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* pwbp*

* drop variables
drop pwbp

* create long-format data from wide data
local question_cols pwbp1 pwbp2 pwbp3 pwbp4 pwbp5 pwbp6 pwbp7 pwbp8
tempfile long_pwbp
save `long_pwbp', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_pwbp'
    save `long_pwbp', replace
    restore
}

use `long_pwbp', clear

drop pwbp1 pwbp2 pwbp3 pwbp4 pwbp5 pwbp6 pwbp7 pwbp8

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
export delimited using "fryback_2009_health_pwbp.csv", replace

**# Bookmark #2: Psychological well-being scales - accept

* recall dataset
use "fryback_2009_health.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* pwbs*

* drop variables
drop pwbs

* create long-format data from wide data
local question_cols pwbs1 pwbs2 pwbs3 pwbs4 pwbs5 pwbs6 pwbs7
tempfile long_pwbs
save `long_pwbs', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_pwbs'
    save `long_pwbs', replace
    restore
}

use `long_pwbs', clear

drop pwbs1 pwbs2 pwbs3 pwbs4 pwbs5 pwbs6 pwbs7

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
export delimited using "fryback_2009_health_pwbs.csv", replace

**# Bookmark #3: Self-Perceived Discrimination

* recall dataset
use "fryback_2009_health.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* discrm*

* drop variables
drop discrmtot

* create long-format data from wide data
local question_cols discrm1 discrm2 discrm3 discrm4 discrm5 discrm6 discrm7 discrm8 discrm9
tempfile long_discrm
save `long_discrm', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_discrm'
    save `long_discrm', replace
    restore
}

use `long_discrm', clear

drop discrm1 discrm2 discrm3 discrm4 discrm5 discrm6 discrm7 discrm8 discrm9

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
export delimited using "fryback_2009_health_discrm.csv", replace

**# Bookmark #4: Quality of life questions

* recall dataset
use "fryback_2009_health.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* sf*

* drop variables
drop sf6phy sf6role sf6men sf6soc sf6pain sf6vit sf36a sf6d_12v2 sf36time sf1rev sf6d_36v2 

* create long-format data from wide data
local question_cols sf1 sf2 sf3 sf4 sf5 sf6 sf7 sf8 sf9 sf10 sf11 sf12 sf13 sf14 sf15 sf16 sf17 sf18 sf19 sf20 sf21 sf22 sf23 sf24 sf25 sf26 sf27 sf28 sf29 sf30 sf31 sf32 sf33 sf34 sf35 sf36
tempfile long_sf
save `long_sf', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_sf'
    save `long_sf', replace
    restore
}

use `long_sf', clear

drop sf1 sf2 sf3 sf4 sf5 sf6 sf7 sf8 sf9 sf10 sf11 sf12 sf13 sf14 sf15 sf16 sf17 sf18 sf19 sf20 sf21 sf22 sf23 sf24 sf25 sf26 sf27 sf28 sf29 sf30 sf31 sf32 sf33 sf34 sf35 sf36

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
export delimited using "fryback_2009_health_sf.csv", replace
