*** This Do File creates tables from the Personality - Murray and Big five theory study ***

******************************************
***********  Prepare the data ************
******************************************

* clear
clear

* import the main dataset
import delimited "IFP maior planilha do mundo IFP.csv", clear

* convert column names to lowercase
rename *, lower

* renames covariates
rename nascimento cov_dob
rename idade cov_age
rename sexo cov_sex
rename profissão cov_profession
rename escolaridade cov_education
rename instituição cov_institution
rename segmento cov_segment

* keep only the covariates and response variables
keep cov* r*

* drop old id and generate new id
gen id = _n

* reorder variables
order id cov*, first

* save cleaned dataset
save "anunciacao_2025_personality.csv", replace

******************************************
************  Shape the data *************
******************************************

**# Bookmark #1: Achievement

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r3	r15	r20	r54	r56	r63	r126	r131 r134

* set up the code for long-format data from wide data
local question_cols r3	r15	r20	r54	r56	r63	r126	r131 r134

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

drop r3	r15	r20	r54	r56	r63	r126	r131 r134

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
export delimited using "anunciacao_2025_personality_achievement.csv", replace

**# Bookmark #2: Affiliation

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r33	r45	r57	r62	r76	r85	r93	r102	r105

* set up the code for long-format data from wide data
local question_cols r33	r45	r57	r62	r76	r85	r93	r102	r105

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

drop r33	r45	r57	r62	r76	r85	r93	r102	r105

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
export delimited using "anunciacao_2025_personality_affiliation.csv", replace

**# Bookmark #3: Aggresion

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r41	r43	r64	r111	r119

* set up the code for long-format data from wide data
local question_cols r41	r43	r64	r111	r119

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

drop r41	r43	r64	r111	r119

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
export delimited using "anunciacao_2025_personality_aggression.csv", replace

**# Bookmark #4: Autonomy

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r2	r8	r13	r65	r101	r109	r116	r143	r144

* set up the code for long-format data from wide data
local question_cols r2	r8	r13	r65	r101	r109	r116	r143	r144

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

drop r2	r8	r13	r65	r101	r109	r116	r143	r144

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
export delimited using "anunciacao_2025_personality_autonomy.csv", replace

**# Bookmark #5: Change

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r4	r22	r38	r67	r73	r124 r95

* set up the code for long-format data from wide data
local question_cols r4	r22	r38	r67	r73	r124 r95

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

drop r4	r22	r38	r67	r73	r124 r95

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
export delimited using "anunciacao_2025_personality_change.csv", replace

**# Bookmark #6: Deference

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r14	r26	r48	r78	r80	r81	r108	r128	r129

* set up the code for long-format data from wide data
local question_cols r14	r26	r48	r78	r80	r81	r108	r128	r129

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

drop r14	r26	r48	r78	r80	r81	r108	r128	r129

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
export delimited using "anunciacao_2025_personality_deference.csv", replace

**# Bookmark #7: Dominance

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r19	r58	r75	r100	r117	r127 r104

* set up the code for long-format data from wide data
local question_cols r19	r58	r75	r100	r117	r127 r104

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

drop r19	r58	r75	r100	r117	r127 r104

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
export delimited using "anunciacao_2025_personality_dominance.csv", replace

**# Bookmark #8: Exhibition

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r98	r112	r114	r132	r137	r145	r148	r154	r155

* set up the code for long-format data from wide data
local question_cols r98	r112	r114	r132	r137	r145	r148	r154	r155

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

drop r98	r112	r114	r132	r137	r145	r148	r154	r155

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
export delimited using "anunciacao_2025_personality_exhibition.csv", replace

**# Bookmark #9: Intraception

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r31	r39	r44	r97	r106	r135 r141

* set up the code for long-format data from wide data
local question_cols r31	r39	r44	r97	r106	r135 r141

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

drop r31	r39	r44	r97	r106	r135 r141

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
export delimited using "anunciacao_2025_personality_intraception.csv", replace

**# Bookmark #10: Nurturance

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r17	r74	r77	r94	r115	r121	r140	r152

* set up the code for long-format data from wide data
local question_cols r17	r74	r77	r94	r115	r121	r140	r152

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

drop r17	r74	r77	r94	r115	r121	r140	r152

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
export delimited using "anunciacao_2025_personality_nurturance.csv", replace

**# Bookmark #11: Order

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r51	r82	r90	r122	r146	r147

* set up the code for long-format data from wide data
local question_cols r51	r82	r90	r122	r146	r147

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

drop r51	r82	r90	r122	r146	r147

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
export delimited using "anunciacao_2025_personality_order.csv", replace

**# Bookmark #12: Persistence

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r16	r18	r25	r29	r36	r46	r69 r60

* set up the code for long-format data from wide data
local question_cols r16	r18	r25	r29	r36	r46	r69 r60

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

drop r16	r18	r25	r29	r36	r46	r69 r60

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
export delimited using "anunciacao_2025_personality_persistence.csv", replace

**# Bookmark #13: Succorance

* recall dataset
use "anunciacao_2025_personality.csv", clear

* compress data
compress

* keep only relevant variables
keep id cov_* r30	r50	r53	r86	r87	r91	r151

* set up the code for long-format data from wide data
local question_cols r30	r50	r53	r86	r87	r91	r151

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

drop r30	r50	r53	r86	r87	r91	r151

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
export delimited using "anunciacao_2025_personality_succorance.csv", replace


*** note from bd: R code below used to remove responses not 1-7
/* lf<-list.files(pattern="*.csv") */
/* for (fn in lf) { */
/*     df<-read.csv(fn) */
/*     print(fn) */
/*     print(dim(df)) */
/*     print(table(df$resp)) */
/*     df$resp<-ifelse(df$resp %in% 1:7,df$resp,NA) */
/*     print(dim(df)) */
/*     print(table(df$resp)) */
/*     for (i in 1:ncol(df)) df[,i]<-gsub('\\|','',df[,i]) */
/*     write.table(df,fn,quote=FALSE,row.names=FALSE,sep="|") */
/* } */
