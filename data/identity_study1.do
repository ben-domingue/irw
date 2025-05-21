*** This Do File creates tables from the Identity Study 1 ***

* clear
clear

* change working directory
cd "C:\Users\lossa\OneDrive\Escritorio\Stata Do Files"

* import main dataset
import spss using "IRS1.sav", clear

* convert main dataset to cvs
export delimited "IRS1.csv", replace

* convert column names to lowercase
rename *, lower

* renames covariates and adds id
gen id = _n
rename gender cov_gender
rename age cov_age
rename education cov_education
rename income cov_income
rename identity cov_identity

* drops non-response variables from dataset
drop attentioncheck1 attentioncheck2 intergroupanxiety perceiveddiscrimination grit collectivese identitydemand identityresource interracialtrust behavioralavoidance perceivedstress groupidentification

* drops recoded versions of original response variables
drop cse2r cse4r cse5r cse7r cse10r cse12r cse13r cse15r grit1r grit3r grit5r grit6r pss4r pss5r pss7r pss8r

* drops single-item attributes from the dataset
drop selfesteem

* creates long data from wide data
local question_cols irsr1 irsd1 irsd2 irsd3 irsd4 irsr2 irsd5 irsr3 irsr4 irsr5 cse1 cse2 cse3 cse4 cse5 cse6 cse7 cse8 cse9 cse10 cse11 cse12 cse13 cse14 cse15 cse16 grit1 grit2 grit3 grit4 grit5 grit6 grit7 grit8 pds1 pds2 pds3 pds4 pds5 pds6 pds7 pds8 pds9 pia1 pia2 pia3 pia4 pit1 pit2 pit3 pit4 pba1 pba2 pba3 pba4 pba5 pba6 pba7 pba8 pba9 pba10 pba11 pss1 pss2 pss3 pss4 pss5 pss6 pss7 pss8 pss9 pss10 gi1 gi2 gi3 gi4

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

drop irsr1 irsd1 irsd2 irsd3 irsd4 irsr2 irsd5 irsr3 irsr4 irsr5 cse1 cse2 cse3 cse4 cse5 cse6 cse7 cse8 cse9 cse10 cse11 cse12 cse13 cse14 cse15 cse16 grit1 grit2 grit3 grit4 grit5 grit6 grit7 grit8 pds1 pds2 pds3 pds4 pds5 pds6 pds7 pds8 pds9 pia1 pia2 pia3 pia4 pit1 pit2 pit3 pit4 pba1 pba2 pba3 pba4 pba5 pba6 pba7 pba8 pba9 pba10 pba11 pss1 pss2 pss3 pss4 pss5 pss6 pss7 pss8 pss9 pss10 gi1 gi2 gi3 gi4

drop if missing(item) | item == ""

* encode any needed variables
destring cov_age, replace
destring resp, replace

* saves final dataset
export delimited using "identity_study1.csv", replace

* creates subset of tables
local base_items irs cse grit pds pia pit pba pss gi
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "identity_study1_`prefix'.csv", replace
    restore
}

* use the files just created
import delimited "identity_study1_irs.csv", clear
import delimited "identity_study1_cse.csv", clear
import delimited "identity_study1_grit.csv", clear
import delimited "identity_study1_pds.csv", clear
import delimited "identity_study1_pia.csv", clear
import delimited "identity_study1_pit.csv", clear
import delimited "identity_study1_pba.csv", clear
import delimited "identity_study1_pss.csv", clear
import delimited "identity_study1_gi.csv", clear

* use the main file
import delimited "identity_study1.csv", clear

* use the uncleaned version of the main file
import delimited "IRS1.csv", clear
edit