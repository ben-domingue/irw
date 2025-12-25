*** This Do File creates tables from the The Comprehensive Assessment of Theory of Mind (CAT): A Novel Measure of 3‐ to 8‐Year‐Old Children's Theory of Mind and an Evaluation of Mental‐State Scaling study ***

* clear
clear

* import main dataset
import delimited "CATdata.csv", clear

* convert column names to lowercase
rename *, lower

* drop any average variables
drop divdesavg divbelavg knowavg vptavg falsebelavg falsesignavg

* drop any unwanted covariates
drop ageyrs grasssky_sum updown_sum vocab_sum 

* renames covariates
rename ageyrsround cov_age
rename sex cov_sex

* drop and add new id
drop subno
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "heise_2024_mental.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: Diverse Desires

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* divdes*

* set up the code for long-format data from wide data
local question_cols divdes_a1_pewcontrol	divdes_b12_pewcontrol	divdes_c5_pewcontrol	divdes_a9_pewcontrol	divdes_c1_pewcontrol	divdes_b10_pewcontrol	divdes_a1_pwcontrol	divdes_b12_pwcontrol	divdes_c5_pwcontrol	divdes_a9_pwcontrol	divdes_c1_pwcontrol	divdes_b10_pwcontrol
tempfile long_divdes
save `long_divdes', emptyok replace

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
    append using `long_divdes'
    save `long_divdes', replace
    restore
}

use `long_divdes', clear

drop divdes*

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
export delimited using "heise_2024_mental_divdesires.csv", replace

**# Bookmark #2: Diverse Beliefs

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* divbel*

* set up the code for long-format data from wide data
local question_cols divbel_a3_pewcontrol	divbel_b7_pewcontrol	divbel_a6_pewcontrol	divbel_c8_pewcontrol	divbel_a3_pwcontrol	divbel_b7_pwcontrol	divbel_a6_pwcontrol	divbel_c8_pwcontrol
tempfile long_divbeliefs
save `long_divbeliefs', emptyok replace

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
    append using `long_divbeliefs'
    save `long_divbeliefs', replace
    restore
}

use `long_divbeliefs', clear

drop divbel*

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
export delimited using "heise_2024_mental_divbeliefs.csv", replace

**# Bookmark #3: Knowledge Expertise

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* knowexpert*

* set up the code for long-format data from wide data
local question_cols knowexpert_a4_pewcontrol	knowexpert_b9_pewcontrol	knowexpert_c10_pewcontrol	knowexpert_a4_pwcontrol	knowexpert_b9_pwcontrol	knowexpert_c10_pwcontrol
tempfile long_knowledgeexpert
save `long_knowledgeexpert', emptyok replace

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
    append using `long_knowledgeexpert'
    save `long_knowledgeexpert', replace
    restore
}

use `long_knowledgeexpert', clear

drop knowexpert*

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
export delimited using "heise_2024_mental_knowexpert.csv", replace

**# Bookmark #4: Knowledge Access

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* knowacc*

* set up the code for long-format data from wide data
local question_cols knowacc_a12_pewcontrol	knowacc_b6_pewcontrol	knowacc_c3_pewcontrol	knowacc_a12_pwcontrol	knowacc_b6_pwcontrol	knowacc_c3_pwcontrol
tempfile long_data
save `long_data', emptyok replace

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
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop knowacc*

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
export delimited using "heise_2024_mental_knowaccess.csv", replace

**# Bookmark #5: False Beliefs

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* falsebel*

* set up the code for long-format data from wide data
local question_cols falsebelcontents_a8_pewcontrol	falsebelcontents_b3_pewcontrol	falsebelcontents_c4_pewcontrol	falsebellocation_a10_pewcontrol	falsebellocation_b11_pewcontrol	falsebellocation_c6_pewcontrol	falsebelcontents_a8_pwcontrol	falsebelcontents_b3_pwcontrol	falsebelcontents_c4_pwcontrol	falsebellocation_a10_pwcontrol	falsebellocation_b11_pwcontrol	falsebellocation_c6_pwcontrol
tempfile long_data
save `long_data', emptyok replace

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
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop falsebel*

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
export delimited using "heise_2024_mental_falsebel.csv", replace

**# Bookmark #6: True Beliefs

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* truebel*

* set up the code for long-format data from wide data
local question_cols truebel_a7_pewcontrol	truebel_b1_pewcontrol	truebel_c12_pewcontrol	truebel_a7_pwcontrol	truebel_b1_pwcontrol	truebel_c12_pwcontrol
tempfile long_data
save `long_data', emptyok replace

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
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop truebel*

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
export delimited using "heise_2024_mental_truebel.csv", replace

**# Bookmark #7: Visual Perspective Taking

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* vpt*

* set up the code for long-format data from wide data
local question_cols vpt1_a11_pewcontrol	vpt1_a2_pewcontrol	vpt1_b2_pewcontrol	vpt1_b5_pewcontrol	vpt2_c7_pewcontrol	vpt2_c11_pewcontrol	vpt1_a11_pwcontrol	vpt1_a2_pwcontrol	vpt1_b2_pwcontrol	vpt1_b5_pwcontrol	vpt2_c7_pwcontrol	vpt2_c11_pwcontrol
tempfile long_data
save `long_data', emptyok replace

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
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop vpt*

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
export delimited using "heise_2024_mental_vpt.csv", replace

**# Bookmark #8: False Sign

* recall dataset
use "heise_2024_mental.csv", clear

* keep only id, covariates, and respective variables
keep id cov_* falsesign*

* set up the code for long-format data from wide data
local question_cols falsesign_a5_pewcontrol	falsesign_a13_pewcontrol	falsesign_b4_pewcontrol	falsesign_b8_pewcontrol	falsesign_c2_pewcontrol	falsesign_c9_pewcontrol	falsesign_a5_pwcontrol	falsesign_a13_pwcontrol	falsesign_b4_pwcontrol	falsesign_b8_pwcontrol	falsesign_c2_pwcontrol	falsesign_c9_pwcontrol
tempfile long_data
save `long_data', emptyok replace

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
    append using `long_data'
    save `long_data', replace
    restore
}

use `long_data', clear

drop falsesign*

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
export delimited using "heise_2024_mental_falsesign.csv", replace