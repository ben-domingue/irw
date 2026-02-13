*** This Do File creates tables from the An Initial Evaluation of a Measure of Social-Emotional Skills Among Brazilian Children and Adolescents study ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import the main dataset
import excel "Base t1.xlsx", firstrow clear

* convert column names to lowercase
rename *, lower

* renames covariates
rename sexo cov_sex
rename pessoas_por_moradia cov_hhsize
rename etnia cov_ethnicity
rename age cov_age

* drop old id and generate new id
gen id = _n

* keep only the newly defined relevant variables
keep cov* id c_*

* reorder variables
order id cov*, first

* save cleaned dataset
save "anunciacao_2025_emotional.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: Relationship skills

* recall dataset
use "anunciacao_2025_emotional.csv", clear

* keep only the relevant variables
keep id cov* c_relac_1 c_relac_10 c_relac_2 c_relac_3 c_relac_4 c_relac_5 c_relac_6 c_relac_7 c_relac_8 c_relac_9

* set up the code for long-format data from wide data
local question_cols c_relac_1 c_relac_10 c_relac_2 c_relac_3 c_relac_4 c_relac_5 c_relac_6 c_relac_7 c_relac_8 c_relac_9

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

drop c_relac_1 c_relac_10 c_relac_2 c_relac_3 c_relac_4 c_relac_5 c_relac_6 c_relac_7 c_relac_8 c_relac_9

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* turn non-integer responses to missing values
replace resp = . if resp != floor(resp)

* export the long-format table for group the group
export delimited using "anunciacao_2025_emotional_relationships.csv", replace

**# Bookmark #2: Responsible decision-making

* recall dataset
use "anunciacao_2025_emotional.csv", clear

* keep only the relevant variables
keep id cov* c_tomada_1 c_tomada_2 c_tomada_3 c_tomada_4 c_tomada_5 c_tomada_6 c_tomada_7 c_tomada_8

* set up the code for long-format data from wide data
local question_cols c_tomada_1 c_tomada_2 c_tomada_3 c_tomada_4 c_tomada_5 c_tomada_6 c_tomada_7 c_tomada_8

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

drop c_tomada_1 c_tomada_2 c_tomada_3 c_tomada_4 c_tomada_5 c_tomada_6 c_tomada_7 c_tomada_8

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
export delimited using "anunciacao_2025_emotional_responsibility.csv", replace

**# Bookmark #3: Self-Awareness

* recall dataset
use "anunciacao_2025_emotional.csv", clear

* keep only the relevant variables
keep id cov* c_aut_1 c_aut_2 c_aut_3 c_aut_4

* set up the code for long-format data from wide data
local question_cols c_aut_1 c_aut_2 c_aut_3 c_aut_4

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

drop c_aut_1 c_aut_2 c_aut_3 c_aut_4

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
export delimited using "anunciacao_2025_emotional_self-awareness.csv", replace

**# Bookmark #4: Self-management

* recall dataset
use "anunciacao_2025_emotional.csv", clear

* keep only the relevant variables
keep id cov* c_autoger_1 c_autoger_2 c_autoger_3 c_autoger_4 c_autoger_5 c_autoger_6 c_autoger_7 c_autoger_8 c_autoger_9

* set up the code for long-format data from wide data
local question_cols c_autoger_1 c_autoger_2 c_autoger_3 c_autoger_4 c_autoger_5 c_autoger_6 c_autoger_7 c_autoger_8 c_autoger_9

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

drop c_autoger_1 c_autoger_2 c_autoger_3 c_autoger_4 c_autoger_5 c_autoger_6 c_autoger_7 c_autoger_8 c_autoger_9

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* sort
sort id item

* turn non-integer responses to missing values
replace resp = . if resp != floor(resp)

* export the long-format table for group the group
export delimited using "anunciacao_2025_emotional_management.csv", replace

**# Bookmark #5: Social-Awareness

* recall dataset
use "anunciacao_2025_emotional.csv", clear

* keep only the relevant variables
keep id cov* c_consc_1 c_consc_2 c_consc_3 c_consc_4 c_consc_5 c_consc_6 c_consc_7 c_consc_8

* set up the code for long-format data from wide data
local question_cols c_consc_1 c_consc_2 c_consc_3 c_consc_4 c_consc_5 c_consc_6 c_consc_7 c_consc_8

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

drop c_consc_1 c_consc_2 c_consc_3 c_consc_4 c_consc_5 c_consc_6 c_consc_7 c_consc_8

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
export delimited using "anunciacao_2025_emotional_social-awareness.csv", replace