import excel "./Assessing psychological flexibility.xlsx", sheet("Sheet 1 - Dataset (2)") firstrow case(lower) allstring
drop pohlavi pohlavi_kod vek va1 oe2r ba3r oe4r va5 oe6r va7 oe8r ba9r va10 oe11r ba12r oe13 va14 oe15r ba16r va17 oe18r ba19r oe20 va21 oe22 va23 s1 a2 d3 a4 d5 s6 a7 s8 a9 d10 s11 s12 d13 s14 a15 d16 d17 s18 a19 a20 d21
drop swl1 swl2 swl3 swl4 swl5

reshape long aaq, i(id) j(resp)
rename resp item
rename aaq resp

label define aaq7 1 "aaq1" 2 "aaq2" 3 "aaq3" 4 "aaq4" 5 "aaq5" 6 "aaq6" 7 "aaq7"
label values item aaq7
destring id, replace
sort id
sort id item
save "/Users/xichen85/Desktop/Ben/CompACT_Ptacek 2024/AAQ_II.dta"
export delimited using "/Users/xichen85/Desktop/new.csv"