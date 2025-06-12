*** This Do File creates tables from the Identity Study ***

* clear
clear

* import study 1 dataset and convert to cvs
import spss using "IRS1.sav", clear
export delimited "IRS1.csv", replace

* generate variable to indicate belonging to study 1
gen study = 1

* renames variables in study 1 to creat uniformity between study 1 and study 2, for variables that need to be assigned a zero value in study 2
rename IRSR1 IRS_R5
rename IRSD4 IRS_D5

* renames variables in study 1 to create uniformity between study 1 and study 2
rename IRSR5 IRS_R4
rename IRSR4 IRS_R3
rename IRSR3 IRS_R2
rename IRSR2 IRS_R1
rename IRSD5 IRS_D4
rename IRSD3 IRS_D3
rename IRSD2 IRS_D2
rename IRSD1 IRS_D1

* saves new study 1 dataset
save "IRS1.dta", replace

* creates a new study 2 dataset that matches the study 1 dataset perfectly
clear
import spss using "IRS2.sav", clear
export delimited "IRS2.csv", replace
gen IRS_R5 = .
gen IRS_D5 = .
drop Vrid
destring Income, replace
save "IRS2.dta", replace

* append study 2 to study 1
use "IRS1.dta", clear
append using "IRS2.dta"

* assign study specification to observations from study 2
replace study = 2 if missing(study)

* drops non-response variables from dataset
drop AttentionCheck1 AttentionCheck2 IntergroupAnxiety PerceivedDiscrimination Grit CollectiveSE IdentityDemand IdentityResource InterracialTrust BehavioralAvoidance PerceivedStress GroupIdentification BehAvoidance Stress GroupID Discrimination IntergoupAnxiety Resource Demand

* drops recoded versions of original response variables
drop CSE2R CSE4R CSE5R CSE7R CSE10R CSE12R CSE13R CSE15R Grit1R Grit3R Grit5R Grit6R PSS4R PSS5R PSS7R PSS8R CSE2r CSE4r CSE5r CSE7r CSE10r CSE12r CSE13r CSE15r grit1r grit3r grit5r grit6r pss4r pss5r pss7r pss8r

* drops single-item attributes from the dataset
drop SelfEsteem

* convert column names to lowercase
rename *, lower

* renames covariates and adds id
gen id = _n
rename gender cov_gender
rename age cov_age
rename education cov_education
rename income cov_income
rename identity cov_identity
rename study cov_study

* save combined dataset
save "IRS.dta", replace
export delimited "IRS2.csv", replace

* creates long data from wide data
local question_cols irs_d1 irs_d2 irs_d3	irs_r1	irs_d4	irs_d5 irs_r2	irs_r3	irs_r4	irs_r5 cse1	cse2	cse3	cse4 cse5 cse6	cse7	cse8	cse9	cse10	cse11	cse12	cse13	cse14	cse15	cse16	grit1	grit2	grit3	grit4	grit5	grit6	grit7	grit8	pds1	pds2	pds3	pds4	pds5	pds6	pds7	pds8	pds9	pia1	pia2	pia3	pia4	pit1	pit2	pit3	pit4	pba1	pba2	pba3	pba4	pba5	pba6	pba7	pba8	pba9	pba10	pba11	pss1	pss2	pss3	pss4	pss5	pss6	pss7	pss8	pss9	pss10	gi1	gi2	gi3	gi4

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

drop irs_d1 irs_d2 irs_d3	irs_r1	irs_d4	irs_d5 irs_r2	irs_r3	irs_r4	irs_r5 cse1	cse2	cse3	cse4 cse5 cse6	cse7	cse8	cse9	cse10	cse11	cse12	cse13	cse14	cse15	cse16	grit1	grit2	grit3	grit4	grit5	grit6	grit7	grit8	pds1	pds2	pds3	pds4	pds5	pds6	pds7	pds8	pds9	pia1	pia2	pia3	pia4	pit1	pit2	pit3	pit4	pba1	pba2	pba3	pba4	pba5	pba6	pba7	pba8	pba9	pba10	pba11	pss1	pss2	pss3	pss4	pss5	pss6	pss7	pss8	pss9	pss10	gi1	gi2	gi3	gi4

drop if missing(item) | item == ""

* encode any needed variables
replace cov_age = subinstr(cov_age, "years", "", .)
replace cov_age = trim(cov_age)
destring cov_age, replace
gen resp2 = resp
drop resp
rename resp2 resp

* reorder variables
order id item resp cov_study cov_gender cov_age cov_education cov_income cov_identity, first

* saves final dataset
export delimited using "singh_2025_identity.csv", replace

* creates subset of tables
local base_items irs cse grit pds pia pit pba pss gi
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "singh_2025_identity_`prefix'.csv", replace
    restore
}

* use the files just created
import delimited "singh_2025_identity_irs.csv", clear
import delimited "singh_2025_identity_cse.csv", clear
import delimited "singh_2025_identity_grit.csv", clear
import delimited "singh_2025_identity_pds.csv", clear
import delimited "singh_2025_identity_pia.csv", clear
import delimited "singh_2025_identity_pit.csv", clear
import delimited "singh_2025_identity_pba.csv", clear
import delimited "singh_2025_identity_pss.csv", clear
import delimited "singh_2025_identity_gi.csv", clear

* use the main file
import delimited "singh_2025_identity.csv", clear

* use the uncleaned version of the main file
import delimited "IRS.dta", clear
edit