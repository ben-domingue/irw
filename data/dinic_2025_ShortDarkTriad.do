*** This Do File creates tables from the The Short Dark Triad across 14 cultures: A novel network-based invariance approach study ***

* clear
clear

* import main dataset and convert to cvs
import spss using "SD3-rec.sav", clear
export delimited "SD3.csv", replace

* convert column names to lowercase
rename *, lower

* renames covariates
rename country_language cov_country_language
rename gender cov_gender
rename age cov_age

* rename responses as needed; cov_gender
label define genderlbl 1 "Male" 2 "Female"
label values cov_gender genderlbl

* remain certain variables just for standardization purposes
rename sd3_11r sd3_11
rename sd3_15r sd3_15
rename sd3_17r sd3_17
rename sd3_20r sd3_20
rename sd3_25r sd3_25

* adds id
gen id = _n

* reorder variables
order id cov_*, first

* save cleaned dataset
save "SD3.csv", replace

* creates long data from wide data
local question_cols sd3_1 sd3_2 sd3_3 sd3_4 sd3_5 sd3_6 sd3_7 sd3_8 sd3_9 sd3_10 sd3_11 sd3_12 sd3_13 sd3_14 sd3_15 sd3_16 sd3_17 sd3_18 sd3_19 sd3_20 sd3_21 sd3_22 sd3_23 sd3_24 sd3_25 sd3_26 sd3_27

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

drop sd3_1 sd3_2 sd3_3 sd3_4 sd3_5 sd3_6 sd3_7 sd3_8 sd3_9 sd3_10 sd3_11 sd3_12 sd3_13 sd3_14 sd3_15 sd3_16 sd3_17 sd3_18 sd3_19 sd3_20 sd3_21 sd3_22 sd3_23 sd3_24 sd3_25 sd3_26 sd3_27

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
export delimited using "dinic_2025_shortdarktriad.csv", replace