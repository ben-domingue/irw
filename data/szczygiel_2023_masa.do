*** This Do File creates tables from the The psychometric properties of the Mathematics Attitude Scale for Adults study ***

* clear
clear

* import main dataset
import excel "MASA_Validity_Dataset_OSF.xlsx", firstrow clear

* convert column names to lowercase
rename *, lower

* drop old id
drop id

* renames covariates
rename efa_cfa cov_efa_cfa
rename group cov_group
rename gender cov_gender
rename age cov_age

* drop unnecessary variables
drop amas_mean amas_learning amas_testing maqa_mean masa_mean masa_a masa_b	masa_c

* drop any existing recorded variables of original (restests)
drop masa_retest1	masa_retest2	masa_retest3	masa_retest4	masa_retest5	masa_retest6	masa_retest7	masa_retest8	masa_retest9	masa_retest10	masa_retest11	masa_retest12	masa_retest13	masa_retest14	masa_retest15	masa_retest16	masa_retest17	masa_retest18	masa_retest19	masa_retest	masa_a_retest	masa_b_retest	masa_c_retest	maqa_retest1	maqa_retest2	maqa_retest3	maqa_retest4	maqa_retest5	maqa_retest6	maqa_retest7	maqa_retest8	maqa_retest9	maqa_retest10	maqa_retest11	maqa_retest12	maqa_retest13	maqa_retest14	maqa_retest15	maqa_retest16	maqa_retest17	maqa_retest18	maqa_retest19	maqa_retest_mean

* convert grades and test scores to covariates
rename polishelementarygrade cov_polish_elementary_grade
rename polishjuniorhighschoolgrade cov_polish_jhighschool_grade
rename polishhighschoolgrade cov_polish_highschool_grade
rename polishhighschoolexitexam	cov_polish_highschool_exitexam
rename mathelementarygrade cov_math_elementary_grade
rename mathjuniorhighschoolgrade cov_math_jjhighschool_grade
rename mathhighschoolgrade cov_math_highschool_exitexam  

* adds id
gen id = _n

* reorder variables
order id cov_*, first

* save cleaned dataset
export delimited using "szczygiel_2023_masa.csv", replace

******************************************
******************************************
************  Shape the data *************
******************************************
******************************************

**# Bookmark #1: Group MASA

* recall dataset
import delimited "szczygiel_2023_masa.csv", clear

* keep only id, covariates, and respective group variables
keep id cov_* masa*

* creates long data from wide data
local question_cols	masa1	masa2	masa3	masa4	masa5	masa6	masa7	masa8	masa9	masa10	masa11	masa12	masa13	masa14	masa15	masa16	masa17	masa18	masa19

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop masa1	masa2	masa3	masa4	masa5	masa6	masa7	masa8	masa9	masa10	masa11	masa12	masa13	masa14	masa15	masa16	masa17	masa18	masa19

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export the long-format table
export delimited using "szczygiel_2023_masa_masa.csv", replace

**# Bookmark #2: Group AMAS

* recall dataset
import delimited "szczygiel_2023_masa.csv", clear

* keep only id, covariates, and respective group variables
keep id cov_* amas*

* creates long data from wide data
local question_cols	amas1	amas2	amas3	amas4	amas5	amas6	amas7	amas8	amas9

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop amas1	amas2	amas3	amas4	amas5	amas6	amas7	amas8	amas9

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export the long-format table
export delimited using "szczygiel_2023_masa_amas.csv", replace

**# Bookmark #3: Group SIMA

* recall dataset
import delimited "szczygiel_2023_masa.csv", clear

* keep only id, covariates, and respective group variables
keep id cov_* sima

* creates long data from wide data
local question_cols	sima

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop sima

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export the long-format table
export delimited using "szczygiel_2023_masa_sima.csv", replace

**# Bookmark #4: Group MAQA

* recall dataset
import delimited "szczygiel_2023_masa.csv", clear

* keep only id, covariates, and respective group variables
keep id cov_* maqa*

* creates long data from wide data
local question_cols	maqa1	maqa2	maqa3	maqa4	maqa5	maqa6	maqa7	maqa8	maqa9	maqa10	maqa11	maqa12	maqa13	maqa14	maqa15	maqa16	maqa17	maqa18	maqa19

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop maqa1	maqa2	maqa3	maqa4	maqa5	maqa6	maqa7	maqa8	maqa9	maqa10	maqa11	maqa12	maqa13	maqa14	maqa15	maqa16	maqa17	maqa18	maqa19

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export the long-format table
export delimited using "szczygiel_2023_masa_maqa.csv", replace

**# Bookmark #5: Group MSC and PSC (Math and Polish Self-Concept) | MSE and PSE (Math and Polish Self-Efficacy)

* recall dataset
import delimited "szczygiel_2023_masa.csv", clear

* keep only id, covariates, and respective group variables
keep id cov_* psc msc	pse	mse

* creates long data from wide data
local question_cols	psc msc	pse	mse

tempfile longdata
save `longdata', emptyok replace

foreach var of local question_cols {
    preserve
    keep id cov_* `var'
    gen item = "`var'"
    rename `var' resp
    order id item resp
    append using `longdata'
    save `longdata', replace
    restore
}

use `longdata', clear

drop psc msc	pse	mse

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov*, first

* export the long-format table
export delimited using "szczygiel_2023_masa_self-concept.self-efficacy.csv", replace