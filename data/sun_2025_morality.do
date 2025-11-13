*** This Do File creates tables from the Are Moral People Happier? study ***

************************************************************************************
************************************************************************************
************************************* Study 1 **************************************
************************************************************************************
************************************************************************************

* clear
clear

* import main dataset
import delimited "study1-maindat.csv", clear

* drop any unwanted or repeated variables
drop numinformants
drop itlike
drop ittrust
drop itrespect
drop itcloseness

* convert column names to lowercase
rename *, lower

* renames covariates
rename sample cov_sample

* drop single-item attributes
drop tsswl 

* drop and add new id
drop tid
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "sun_2025_morality_1.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: General Morality

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqgm1 itmcqgm2 itmcqgm3 itmcqgm4 itmcqgm5 itmcqgm6

* set up the code for long-format data from wide data
local question_cols itmcqgm1 itmcqgm2 itmcqgm3 itmcqgm4 itmcqgm5 itmcqgm6
tempfile long_morality
save `long_morality', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_morality'
    save `long_morality', replace
    restore
}

use `long_morality', clear

drop itmcqgm1 itmcqgm2 itmcqgm3 itmcqgm4 itmcqgm5 itmcqgm6

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_morality.csv", replace

**# Bookmark #2: Compassion

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi22 itbfi217 itbfi232 itbfi247

* set up the code for long-format data from wide data
local question_cols itbfi22 itbfi217 itbfi232 itbfi247
tempfile long_compassion
save `long_compassion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_compassion'
    save `long_compassion', replace
    restore
}

use `long_compassion', clear

drop itbfi22 itbfi217 itbfi232 itbfi247

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_compassion.csv", replace

**# Bookmark #3: Respectfulness

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi27 itbfi222 itbfi237 itbfi252

* set up the code for long-format data from wide data
local question_cols itbfi27 itbfi222 itbfi237 itbfi252
tempfile long_respectfulness
save `long_respectfulness', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_respectfulness'
    save `long_respectfulness', replace
    restore
}

use `long_respectfulness', clear

drop itbfi27 itbfi222 itbfi237 itbfi252

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_respectfulness.csv", replace

**# Bookmark #4: Honesty

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqh1 itmcqh2 itmcqh3 itmcqh4

* set up the code for long-format data from wide data
local question_cols itmcqh1 itmcqh2 itmcqh3 itmcqh4
tempfile long_honesty
save `long_honesty', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_honesty'
    save `long_honesty', replace
    restore
}

use `long_honesty', clear

drop itmcqh1 itmcqh2 itmcqh3 itmcqh4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_honesty.csv", replace

**# Bookmark #5: Loyalty

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcql1 itmcql2 itmcql3 itmcql4

* set up the code for long-format data from wide data
local question_cols itmcql1 itmcql2 itmcql3 itmcql4
tempfile long_loyalty
save `long_loyalty', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_loyalty'
    save `long_loyalty', replace
    restore
}

use `long_loyalty', clear

drop itmcql1 itmcql2 itmcql3 itmcql4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_loyalty.csv", replace

**# Bookmark #6: Fairness MCQ

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqf1 itmcqf2 itmcqf3 itmcqf4

* set up the code for long-format data from wide data
local question_cols itmcqf1 itmcqf2 itmcqf3 itmcqf4
tempfile long_fairnessMCQ
save `long_fairnessMCQ', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_fairnessMCQ'
    save `long_fairnessMCQ', replace
    restore
}

use `long_fairnessMCQ', clear

drop itmcqf1 itmcqf2 itmcqf3 itmcqf4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_fairnessMCQ.csv", replace

**# Bookmark #7: Fairness HEXACO

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ithhf1 ithhf2 ithhf3 ithhf4

* set up the code for long-format data from wide data
local question_cols ithhf1 ithhf2 ithhf3 ithhf4
tempfile long_fairnessHEXACO
save `long_fairnessHEXACO', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_fairnessHEXACO'
    save `long_fairnessHEXACO', replace
    restore
}

use `long_fairnessHEXACO', clear

drop ithhf1 ithhf2 ithhf3 ithhf4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_fairnessHEXACO.csv", replace

**# Bookmark #8: Dependability

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi213 itbfi243

* set up the code for long-format data from wide data
local question_cols itbfi213 itbfi243
tempfile long_dependability
save `long_dependability', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_dependability'
    save `long_dependability', replace
    restore
}

use `long_dependability', clear

drop itbfi213 itbfi243

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_dependability.csv", replace

**# Bookmark #9: Positive Emotion

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tspermap1 tspermap2 tspermap3

* set up the code for long-format data from wide data
local question_cols tspermap1 tspermap2 tspermap3
tempfile long_pemotion
save `long_pemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_pemotion'
    save `long_pemotion', replace
    restore
}

use `long_pemotion', clear

drop tspermap1 tspermap2 tspermap3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_pemotion.csv", replace

**# Bookmark #10: Negative Emotion

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tsperman1 tsperman2 tsperman3

* set up the code for long-format data from wide data
local question_cols tsperman1 tsperman2 tsperman3
tempfile long_nemotion
save `long_nemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_nemotion'
    save `long_nemotion', replace
    restore
}

use `long_nemotion', clear

drop tsperman1 tsperman2 tsperman3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_nemotion.csv", replace

**# Bookmark #11: Meaning

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tspermam1 tspermam2 tspermam3

* set up the code for long-format data from wide data
local question_cols tspermam1 tspermam2 tspermam3
tempfile long_meaning
save `long_meaning', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_meaning'
    save `long_meaning', replace
    restore
}

use `long_meaning', clear

drop tspermam1 tspermam2 tspermam3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_meaning.csv", replace

**# Bookmark #12: Positive Relationships

* recall dataset
use "sun_2025_morality_1.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tspermar1 tspermar2 tspermar3

* set up the code for long-format data from wide data
local question_cols tspermar1 tspermar2 tspermar3
tempfile long_prelationships
save `long_prelationships', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_prelationships'
    save `long_prelationships', replace
    restore
}

use `long_prelationships', clear

drop tspermar1 tspermar2 tspermar3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study1_prelationships.csv", replace

************************************************************************************
************************************************************************************
************************************* Study 2 **************************************
************************************************************************************
************************************************************************************

* clear
clear

* import main dataset
import delimited "study2-maindat.csv", clear

* filter out observations that were not included in main analysis
drop if exploratory == 1

* drop any unwanted or repeated variables
drop exploratory

* convert column names to lowercase
rename *, lower

* renames covariates
rename teamid cov_teamid
rename teamsize cov_teamsize
rename location cov_location

* drop single-item attributes
drop tsswl
drop tsmlq5r

* drop and add new id
drop pid
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "sun_2025_morality_2.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #14: Self-Reported Moral Character

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tsmt1 tsmt2 tsmt3 tsmt4 tsmt5 tsmt6 tsmt7 tsmt8 tsmt9 tsmt10

* set up the code for long-format data from wide data
local question_cols tsmt1 tsmt2 tsmt3 tsmt4 tsmt5 tsmt6 tsmt7 tsmt8 tsmt9 tsmt10
tempfile long_srmcharacter
save `long_srmcharacter', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_srmcharacter'
    save `long_srmcharacter', replace
    restore
}

use `long_srmcharacter', clear

drop tsmt1 tsmt2 tsmt3 tsmt4 tsmt5 tsmt6 tsmt7 tsmt8 tsmt9 tsmt10

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_self-moral-character.csv", replace

**# Bookmark #15: Informant-Reported Moral Character

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmt*_*

* set up the code for long-format data from wide data
local question_cols itmt*_*
tempfile long_irmcharacter
save `long_irmcharacter', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itmt*_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_irmcharacter'
    save `long_irmcharacter', replace
    restore
}

use `long_irmcharacter', clear

drop itmt*_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_informant-moral-character.csv", replace

**# Bookmark #16: How well do you LIKE this colleague?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itlike_*

* set up the code for long-format data from wide data
local question_cols itlike_*
tempfile long_like
save `long_like', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itlike_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_like'
    save `long_like', replace
    restore
}

use `long_like', clear

drop itlike_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_colleaguelike.csv", replace

**# Bookmark #17: How well do you RESPECT this colleague?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itrespect_*

* set up the code for long-format data from wide data
local question_cols itrespect_*
tempfile long_respect
save `long_respect', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itrespect_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_respect'
    save `long_respect', replace
    restore
}

use `long_respect', clear

drop itrespect_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_colleaguerespect.csv", replace

**# Bookmark #18: How well do you TRUST this colleague?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ittrust_*

* set up the code for long-format data from wide data
local question_cols ittrust_*
tempfile long_trust
save `long_trust', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist ittrust_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_trust'
    save `long_trust', replace
    restore
}

use `long_trust', clear

drop ittrust_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_colleaguetrust.csv", replace

**# Bookmark #18: How well do you KNOW this colleague?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itknow_*

* set up the code for long-format data from wide data
local question_cols itknow_*
tempfile long_know
save `long_know', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itknow_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_know'
    save `long_know', replace
    restore
}

use `long_know', clear

drop itknow_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_colleagueknow.csv", replace

**# Bookmark #19: How CLOSE are you with this colleague?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itclose_*

* set up the code for long-format data from wide data
local question_cols itclose_*
tempfile long_close
save `long_close', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itclose_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_close'
    save `long_close', replace
    restore
}

use `long_close', clear

drop itclose_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_colleagueclose.csv", replace

**# Bookmark #20: Positive Emotion

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tspermap1 tspermap2 tspermap3

* set up the code for long-format data from wide data
local question_cols tspermap1 tspermap2 tspermap3
tempfile long_pemotion
save `long_pemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_pemotion'
    save `long_pemotion', replace
    restore
}

use `long_pemotion', clear

drop tspermap1 tspermap2 tspermap3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_pemotion.csv", replace

**# Bookmark #21: Negative Emotion

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tsperman1 tsperman2 tsperman3

* set up the code for long-format data from wide data
local question_cols tsperman1 tsperman2 tsperman3
tempfile long_nemotion
save `long_nemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_nemotion'
    save `long_nemotion', replace
    restore
}

use `long_nemotion', clear

drop tsperman1 tsperman2 tsperman3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_nemotion.csv", replace

**# Bookmark #22: Meaning

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tsmlq1 tsmlq2 tsmlq3 tsmlq4 tsmlq5

* set up the code for long-format data from wide data
local question_cols tsmlq1 tsmlq2 tsmlq3 tsmlq4 tsmlq5
tempfile long_meaning
save `long_meaning', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_meaning'
    save `long_meaning', replace
    restore
}

use `long_meaning', clear

drop tsmlq1 tsmlq2 tsmlq3 tsmlq4 tsmlq5

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_meaning.csv", replace

**# Bookmark #23: Positive Relationships

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tspermar1 tspermar2 tspermar3

* set up the code for long-format data from wide data
local question_cols tspermar1 tspermar2 tspermar3
tempfile long_prelationships
save `long_prelationships', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_prelationships'
    save `long_prelationships', replace
    restore
}

use `long_prelationships', clear

drop tspermar1 tspermar2 tspermar3

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_prelationships.csv", replace

**# Bookmark #24: How much do you think people around you LIKE you?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tmlike_*

* set up the code for long-format data from wide data
local question_cols tmlike_*
tempfile long_like
save `long_like', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist tmlike_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_like'
    save `long_like', replace
    restore
}

use `long_like', clear

drop tmlike_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_peoplelike.csv", replace

**# Bookmark #25: How much do you think people around you RESPECT you?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tmrespect_*

* set up the code for long-format data from wide data
local question_cols tmrespect_*
tempfile long_respect
save `long_respect', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist tmrespect_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_respect'
    save `long_respect', replace
    restore
}

use `long_respect', clear

drop tmrespect_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_peoplerespect.csv", replace

**# Bookmark #26: How much do you think people around you TRUST you?

* recall dataset
use "sun_2025_morality_2.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* tmtrust_*

* set up the code for long-format data from wide data
local question_cols tmtrust_*
tempfile long_trust
save `long_trust', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist tmtrust_* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_trust'
    save `long_trust', replace
    restore
}

use `long_trust', clear

drop tmtrust_*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study2_peopletrust.csv", replace

************************************************************************************
************************************************************************************
************************************* Study 3 **************************************
************************************************************************************
************************************************************************************

* clear
clear

* import main dataset
import delimited "study3-maindat.csv", clear

* convert column names to lowercase
rename *, lower

* renames covariates
rename nid cov_nid
rename tid cov_tid
rename ntgroup cov_moralgroup

* add new id
gen id = _n

* drop single-item attributes
drop tsswl tsswb ntswl ntswb nsswl nsswb itswl tspermar tsmsr

* drop recoded items
drop itmcqh1r itmcql2r itbfas37r itbfas67r itbfas17r itbfas97r itbfas77r itbfi216r itbfi251r itbfi226r itbfi247r itbfi24r itbfi224r itbfi229r itbfi255r itbfi25r itbfi230r ithhf1r ithhf2r ithhf4r itmcqf3r nsnegemor tsnegemor

*drop index variables
drop tsmoralindex itmoralindex

* drop any unwanted or repeated variables
drop itlike ittrust itrespect itcloseness

* drop additional uncessesary variables
drop tswarmglow itreputation tmreputation

* reorder variables
order id cov*, first

* save cleaned dataset
save "sun_2025_morality_3.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #27: Fairness MCQ

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqf1 itmcqf2 itmcqf3 itmcqf4

* set up the code for long-format data from wide data
local question_cols itmcqf1 itmcqf2 itmcqf3 itmcqf4
tempfile long_fairnessMCQ
save `long_fairnessMCQ', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_fairnessMCQ'
    save `long_fairnessMCQ', replace
    restore
}

use `long_fairnessMCQ', clear

drop itmcqf1 itmcqf2 itmcqf3 itmcqf4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_fairnessMCQ.csv", replace

**# Bookmark #28: Fairness HEXACO

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ithhf1 ithhf2 ithhf3 ithhf4

* set up the code for long-format data from wide data
local question_cols ithhf1 ithhf2 ithhf3 ithhf4
tempfile long_fairnessHEXACO
save `long_fairnessHEXACO', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_fairnessHEXACO'
    save `long_fairnessHEXACO', replace
    restore
}

use `long_fairnessHEXACO', clear

drop ithhf1 ithhf2 ithhf3 ithhf4

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_fairnessHEXACO.csv", replace

**# Bookmark #29: General Morality

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqgm*

* set up the code for long-format data from wide data
local question_cols itmcqgm*
tempfile long_gmorality
save `long_gmorality', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itmcqgm* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_gmorality'
    save `long_gmorality', replace
    restore
}

use `long_gmorality', clear

drop itmcqgm*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_generalmorality.csv", replace

**# Bookmark #30: Compassion

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi22 itbfi232 itbfi247

* set up the code for long-format data from wide data
local question_cols itbfi22 itbfi232 itbfi247
tempfile long_compassion
save `long_compassion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi22 itbfi232 itbfi247 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_compassion'
    save `long_compassion', replace
    restore
}

use `long_compassion', clear

drop itbfi22 itbfi232 itbfi247

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_compassion.csv", replace

**# Bookmark #31: Dependability

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi213 itbfi243 itipipx146 itipipv163

* set up the code for long-format data from wide data
local question_cols itbfi213 itbfi243 itipipx146 itipipv163
tempfile long_dependability
save `long_dependability', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi213 itbfi243 itipipx146 itipipv163 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_dependability'
    save `long_dependability', replace
    restore
}

use `long_dependability', clear

drop itbfi213 itbfi243 itipipx146 itipipv163

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_dependability.csv", replace

**# Bookmark #32: Benevolence

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi227 itbfas42 itbfas92

* set up the code for long-format data from wide data
local question_cols itbfi227 itbfas42 itbfas92
tempfile long_benevolence
save `long_benevolence', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi227 itbfas42 itbfas92 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_benevolence'
    save `long_benevolence', replace
    restore
}

use `long_benevolence', clear

drop itbfi227 itbfas42 itbfas92

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_benevolence.csv", replace

**# Bookmark #33: Honesty

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcqh*

* set up the code for long-format data from wide data
local question_cols itmcqh*
tempfile long_honesty
save `long_honesty', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itmcqh* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_honesty'
    save `long_honesty', replace
    restore
}

use `long_honesty', clear

drop itmcqh*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_honesty.csv", replace

**# Bookmark #34: Loyalty

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itmcql*

* set up the code for long-format data from wide data
local question_cols itmcql*
tempfile long_loyalty
save `long_loyalty', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itmcql* {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_loyalty'
    save `long_loyalty', replace
    restore
}

use `long_loyalty', clear

drop itmcql*

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_loyalty.csv", replace

**# Bookmark #35: Respectfulness

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfas37 itbfas67 itbfas17 itbfas97 itbfas77 itbfi27

* set up the code for long-format data from wide data
local question_cols itbfas37 itbfas67 itbfas17 itbfas97 itbfas77 itbfi27
tempfile long_respectfulness
save `long_respectfulness', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfas37 itbfas67 itbfas17 itbfas97 itbfas77 itbfi27 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_respectfulness'
    save `long_respectfulness', replace
    restore
}

use `long_respectfulness', clear

drop itbfas37 itbfas67 itbfas17 itbfas97 itbfas77 itbfi27

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_respectfulness.csv", replace

**# Bookmark #36: Meaning

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* nsmeaning ntmeaning itmeaning tsmeaning

* set up the code for long-format data from wide data
local question_cols nsmeaning ntmeaning itmeaning tsmeaning
tempfile long_meaning
save `long_meaning', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist nsmeaning ntmeaning itmeaning tsmeaning {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_meaning'
    save `long_meaning', replace
    restore
}

use `long_meaning', clear

drop nsmeaning ntmeaning itmeaning tsmeaning

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_meaning.csv", replace

**# Bookmark #37: Neuroticism

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi259 itbfi229 itbfi224 itbfi254 itbfi234 itbfi24

* set up the code for long-format data from wide data
local question_cols itbfi259 itbfi229 itbfi224 itbfi254 itbfi234 itbfi24
tempfile long_neuroticism
save `long_neuroticism', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi259 itbfi229 itbfi224 itbfi254 itbfi234 itbfi24 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_neuroticism'
    save `long_neuroticism', replace
    restore
}

use `long_neuroticism', clear

drop itbfi259 itbfi229 itbfi224 itbfi254 itbfi234 itbfi24

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_neuroticism.csv", replace

**# Bookmark #38: Extraversion

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi241 itbfi226 itbfi251 itbfi221 itbfi216 itbfi21

* set up the code for long-format data from wide data
local question_cols itbfi241 itbfi226 itbfi251 itbfi221 itbfi216 itbfi21
tempfile long_extraversion
save `long_extraversion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi241 itbfi226 itbfi251 itbfi221 itbfi216 itbfi21 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_extraversion'
    save `long_extraversion', replace
    restore
}

use `long_extraversion', clear

drop itbfi241 itbfi226 itbfi251 itbfi221 itbfi216 itbfi21

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_extraversion.csv", replace

**# Bookmark #39: Openness

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itbfi240 itbfi255 itbfi25 itbfi220 itbfi230 itbfi260

* set up the code for long-format data from wide data
local question_cols itbfi240 itbfi255 itbfi25 itbfi220 itbfi230 itbfi260
tempfile long_openness
save `long_openness', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itbfi240 itbfi255 itbfi25 itbfi220 itbfi230 itbfi260 {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_openness'
    save `long_openness', replace
    restore
}

use `long_openness', clear

drop itbfi240 itbfi255 itbfi25 itbfi220 itbfi230 itbfi260

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_openness.csv", replace

**# Bookmark #40: Moral Ratings

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itcruel ithonest itkind ittrustworthy ithelpful itfair itgenerous itmeanspirited itconsiderate itforgiving itprejudiced itmanipulative itselfish itsincere ithumble itprincipled itgrateful itloyal itresponsible itsocconscious ithardworking itcourageous itselfcontrol itaggressive ithappy itreligious itintelligent itfunny itattractive itathletic itkindness itintegrity

* set up the code for long-format data from wide data
local question_cols itcruel ithonest itkind ittrustworthy ithelpful itfair itgenerous itmeanspirited itconsiderate itforgiving itprejudiced itmanipulative itselfish itsincere ithumble itprincipled itgrateful itloyal itresponsible itsocconscious ithardworking itcourageous itselfcontrol itaggressive ithappy itreligious itintelligent itfunny itattractive itathletic itkindness itintegrity
tempfile long_moralratings
save `long_moralratings', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itcruel ithonest itkind ittrustworthy ithelpful itfair itgenerous itmeanspirited itconsiderate itforgiving itprejudiced itmanipulative itselfish itsincere ithumble itprincipled itgrateful itloyal itresponsible itsocconscious ithardworking itcourageous itselfcontrol itaggressive ithappy itreligious itintelligent itfunny itattractive itathletic itkindness itintegrity {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_moralratings'
    save `long_moralratings', replace
    restore
}

use `long_moralratings', clear

drop itcruel ithonest itkind ittrustworthy ithelpful itfair itgenerous itmeanspirited itconsiderate itforgiving itprejudiced itmanipulative itselfish itsincere ithumble itprincipled itgrateful itloyal itresponsible itsocconscious ithardworking itcourageous itselfcontrol itaggressive ithappy itreligious itintelligent itfunny itattractive itathletic itkindness itintegrity

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_moralratings.csv", replace

**# Bookmark #41: Cost of Being Moral

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* itreproach itboasts tsunconstrained tsdis tsstruggles tsselfsac tssuffer

* set up the code for long-format data from wide data
local question_cols itreproach itboasts tsunconstrained tsdis tsstruggles tsselfsac tssuffer
tempfile long_costofmorality
save `long_costofmorality', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist itreproach itboasts tsunconstrained tsdis tsstruggles tsselfsac tssuffer {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_costofmorality'
    save `long_costofmorality', replace
    restore
}

use `long_costofmorality', clear

drop itreproach itboasts tsunconstrained tsdis tsstruggles tsselfsac tssuffer

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_costofmorality.csv", replace

**# Bookmark #42: Positive Emotions

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* nsposemo ntposemo itposemo tsposemo

* set up the code for long-format data from wide data
local question_cols nsposemo ntposemo itposemo tsposemo
tempfile long_pemotion
save `long_pemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist nsposemo ntposemo itposemo tsposemo {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_pemotion'
    save `long_pemotion', replace
    restore
}

use `long_pemotion', clear

drop nsposemo ntposemo itposemo tsposemo

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_pemotion.csv", replace

**# Bookmark #43: Negative Emotions

* recall dataset
use "sun_2025_morality_3.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* ntnegemo itnegemo

* set up the code for long-format data from wide data
local question_cols ntnegemo itnegemo
tempfile long_nemotion
save `long_nemotion', emptyok replace

* format all variables as numeric to standardize the data
foreach var of local question_cols {
    capture confirm numeric variable `var'
    if _rc {
        destring `var', replace force
    }
}

* create long-format data from wide data
foreach var of varlist ntnegemo itnegemo {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp cov_*
    append using `long_nemotion'
    save `long_nemotion', replace
    restore
}

use `long_nemotion', clear

drop ntnegemo itnegemo

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* round to the nearest decimal to standardize the data
replace resp = round(resp)

* reorder variables
order id item resp cov*, first

* sort
sort id item

* export the long-format table for group the group
export delimited using "sun_2025_morality_study3_nemotion.csv", replace