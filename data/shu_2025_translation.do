*** This Do File creates tables from the Translation and Cultural adaptation study ***

* clear
clear

* import main dataset
import excel "shu_2025_translation_originaldata.xlsx", firstrow

* encodes gender
gen gender_str = cond(Gender == 1, "Male", "Female")

gen gender_num = .

replace gender_num = 1 if gender_str == "Male"
replace gender_num = 2 if gender_str == "Female"
label define genderlab 1 "Male" 2 "Female"

label values gender_num genderlab

rename gender_num gender

* encodes age
gen age_group = cond(Age==1, "<20", cond(Age==2, "20-24", cond(Age==3, "25-29", cond(Age==4, "30-34", cond(Age==5, "≥35", "")))))

gen age_group_num = .

replace age_group_num = 1 if age_group == "<20"
replace age_group_num = 2 if age_group == "20-24"
replace age_group_num = 3 if age_group == "25-29"
replace age_group_num = 4 if age_group == "30-34"
replace age_group_num = 5 if age_group == "≥35"

label define agegrouplab 1 "<20" 2 "20-24" 3 "25-29" 4 "30-34" 5 "≥35"
label values age_group_num agegrouplab

rename age_group_num age

* drop any unwanted or repeated variables
drop Typeofinstituteandprogramme
drop Studyyear
drop Gender
drop gender_str
drop Age
drop age_group

* convert column names to lowercase
rename *, lower

* renames covariates
rename gender cov_gender
rename age cov_age

* adds an identifier to effectively group items into family groups
rename (pishp11 pishp21 pishp31 pishp41 pishp51 pishp61 pishp71 pishp81 pishp91 pishp101 pishp111 pishp121 pishp131 pishp141 pishp151 pishp161) (pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161)

rename (pishp172	pishp182	pishp192	pishp202	pishp212	pishp222	pishp232) (eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232)

rename (pishp243	pishp253	pishp263	pishp273	pishp283) (pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283)

rename (pishp294	pishp304	pishp314	pishp324	pishp334) (srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334)

rename (reasontochooserehab myviewondevelopmentinrehab competitioninreha) (addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha)

* creates long data from wide data
local question_cols mcpis1	mcpis2	mcpis3	mcpis4	mcpis5	mcpis6	mcpis7	mcpis8	mcpis9 pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161 eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232 pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283 srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334 addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha

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

drop mcpis1	mcpis2	mcpis3	mcpis4	mcpis5	mcpis6	mcpis7	mcpis8	mcpis9 pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161 eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232 pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283 srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334 addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha

drop if missing(item) | item == ""

* reorder variables
order id item resp cov_gender cov_age, first

* saves final dataset
export delimited using "shu_2025_translation.csv", replace

* creates subset of tables
local base_items mcpis pcd eib pgv srt add
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "shu_2025_translation_`prefix'.csv", replace
    restore
}

* use the files just created
import delimited "shu_2025_translation_mcpis.csv", clear
import delimited "shu_2025_translation_pcd.csv", clear
import delimited "shu_2025_translation_eib.csv", clear
import delimited "shu_2025_translation_pgv.csv", clear
import delimited "shu_2025_translation_srt.csv", clear
import delimited "shu_2025_translation_add.csv", clear

* use the main file
import delimited "shu_2025_translation.csv", clear

* use the uncleaned version of the main file
clear
import excel "shu_2025_translation_originaldata.xlsx", firstrow
=======
*** This Do File creates tables from the Translation and Cultural adaptation study ***

* clear
clear

* import main dataset
import excel "shu_2025_translation_originaldata.xlsx", firstrow

* encodes gender
gen gender_str = cond(Gender == 1, "Male", "Female")

gen gender_num = .

replace gender_num = 1 if gender_str == "Male"
replace gender_num = 2 if gender_str == "Female"
label define genderlab 1 "Male" 2 "Female"

label values gender_num genderlab

rename gender_num gender

* encodes age
gen age_group = cond(Age==1, "<20", cond(Age==2, "20-24", cond(Age==3, "25-29", cond(Age==4, "30-34", cond(Age==5, "≥35", "")))))

gen age_group_num = .

replace age_group_num = 1 if age_group == "<20"
replace age_group_num = 2 if age_group == "20-24"
replace age_group_num = 3 if age_group == "25-29"
replace age_group_num = 4 if age_group == "30-34"
replace age_group_num = 5 if age_group == "≥35"

label define agegrouplab 1 "<20" 2 "20-24" 3 "25-29" 4 "30-34" 5 "≥35"
label values age_group_num agegrouplab

rename age_group_num age

* drop any unwanted or repeated variables
drop Typeofinstituteandprogramme
drop Studyyear
drop Gender
drop gender_str
drop Age
drop age_group

* convert column names to lowercase
rename *, lower

* renames covariates
rename gender cov_gender
rename age cov_age

* adds an identifier to effectively group items into family groups
rename (pishp11 pishp21 pishp31 pishp41 pishp51 pishp61 pishp71 pishp81 pishp91 pishp101 pishp111 pishp121 pishp131 pishp141 pishp151 pishp161) (pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161)

rename (pishp172	pishp182	pishp192	pishp202	pishp212	pishp222	pishp232) (eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232)

rename (pishp243	pishp253	pishp263	pishp273	pishp283) (pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283)

rename (pishp294	pishp304	pishp314	pishp324	pishp334) (srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334)

rename (reasontochooserehab myviewondevelopmentinrehab competitioninreha) (addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha)

* creates long data from wide data
local question_cols mcpis1	mcpis2	mcpis3	mcpis4	mcpis5	mcpis6	mcpis7	mcpis8	mcpis9 pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161 eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232 pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283 srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334 addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha

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

drop mcpis1	mcpis2	mcpis3	mcpis4	mcpis5	mcpis6	mcpis7	mcpis8	mcpis9 pcd_pishp11 pcd_pishp21 pcd_pishp31 pcd_pishp41 pcd_pishp51 pcd_pishp61 pcd_pishp71 pcd_pishp81 pcd_pishp91 pcd_pishp101 pcd_pishp111 pcd_pishp121 pcd_pishp131 pcd_pishp141 pcd_pishp151 pcd_pishp161 eib_pishp172	eib_pishp182	eib_pishp192	eib_pishp202	eib_pishp212	eib_pishp222	eib_pishp232 pgv_pishp243	pgv_pishp253	pgv_pishp263	pgv_pishp273	pgv_pishp283 srt_pishp294	srt_pishp304	srt_pishp314	srt_pishp324	srt_pishp334 addreasontochooserehab addmyviewondevelopmentinrehab addcompetitioninreha

drop if missing(item) | item == ""

* reorder variables
order id item resp cov_gender cov_age, first

* saves final dataset
export delimited using "shu_2025_translation.csv", replace

* creates subset of tables
local base_items mcpis pcd eib pgv srt add
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "shu_2025_translation_`prefix'.csv", replace
    restore
}