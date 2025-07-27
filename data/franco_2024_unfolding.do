*** This Do File creates tables from the A Tutorial on Unidimensional Unfolding: From Automatic Item Generation to Insightful Inferences study ***

* clear
clear

* import main dataset
import delimited "CoombsGPT.csv", clear

* drop old id
drop id

* drop unnecessary variables
drop run timestartedutc timefinishedutc minutesspent 

* renames covariates
rename sex cov_sex
rename gender cov_gender
rename age cov_age
rename scholarity cov_education

* adds new id
gen id = _n

* reorder variables
order id cov_*, first

* save cleaned dataset
save "franco_2024_unfolding.csv", replace

* creates long data from wide data
local question_cols  p_1  p_2  p_3  p_4  p_5  p_6

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

drop p_1  p_2  p_3  p_4  p_5  p_6

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov_*

* sort responses
sort item id 

* saves final dataset
export delimited using "franco_2024_unfolding.csv", replace