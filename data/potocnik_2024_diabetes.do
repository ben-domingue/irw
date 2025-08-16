*** This Do File creates tables from the Psychometric Properties of the Slovenian Version of the Diabetes Empowerment Scale study ***

* clear
clear

* import main dataset
import excel "validacija DES.xlsx", firstrow clear

* convert column names to lowercase
rename *, lower

* drop old id
drop id

* renames and translates covariates
rename spol cov_gender
rename starost cov_age
rename postna cov_postal_code
rename izobrazba cov_education
rename stan	cov_residence
rename zaposlitev cov_employment
rename peroralnath	cov_therapy_oral
rename inzulinskath	cov_therapy_insulin
rename prisotnaah	cov_present_ah
rename visina cov_height
rename teza	cov_weight
rename bmi cov_bmi
rename bmiktg cov_bmiktg
rename izobrazbadih	cov_education_dih
rename ljokolicavsostali cov_surroundings_vs_others
rename hba1c cov_hba1c

* drop similar, transformer, repeated, or recoded versions of the same variable
drop des_q19rev

* drop unrecognized or otherwise unnecessary variables
drop stletzdravljenjasb

* drop unnecessary measurement variables
drop des desi desii desiii

* implement aggressive recoding to NA (standard Stata format) for values of coded as "NA" in string or some other format
foreach var of varlist _all {
    replace `var' = "" if `var' == "NA"
}

* encode needed variables
foreach var of varlist _all {
    if "`var'" != "cov_surroundings_vs_others" {
        capture confirm string variable `var'
        if _rc == 0 {
            destring `var', replace ignore("") force
        }
    }
}

* adjust the decimal points of selected numeric variables to one decimal
replace cov_bmi = round(cov_bmi, 0.1)
replace cov_hba1c = round(cov_hba1c, 0.1)

* adds new id
gen id = _n

* reorder variables
order id cov_*, first

* save cleaned dataset
save "potocnik_2024_diabetes.csv", replace

* creates long data from wide data
local question_cols des_q1 des_q2 des_q3 des_q4 des_q5 des_q6 des_q7 des_q8 des_q9 des_q10 des_q11 des_q12 des_q13 des_q14 des_q15 des_q16 des_q17 des_q18 des_q19 des_q20 des_q21 des_q22 des_q23 des_q24 des_q25 des_q26 des_q27 des_q28

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

drop des_q1 des_q2 des_q3 des_q4 des_q5 des_q6 des_q7 des_q8 des_q9 des_q10 des_q11 des_q12 des_q13 des_q14 des_q15 des_q16 des_q17 des_q18 des_q19 des_q20 des_q21 des_q22 des_q23 des_q24 des_q25 des_q26 des_q27 des_q28

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
export delimited using "potocnik_2024_diabetes.csv", replace