import excel "./Assessing psychological flexibility.xlsx", sheet("Sheet 1 - Dataset (2)") firstrow case(lower) allstring
drop pohlavi pohlavi_kod vek va1 oe2r ba3r oe4r va5 oe6r va7 oe8r ba9r va10 oe11r ba12r oe13 va14 oe15r ba16r va17 oe18r ba19r oe20 va21 oe22 va23 s1 a2 d3 a4 d5 s6 a7 s8 a9 d10 s11 s12 d13 s14 a15 d16 d17 s18 a19 a20 d21 aaq1 aaq2 aaq3 aaq4 aaq5 aaq6 aaq7
reshape long swl, i(id) j(resp)
rename resp item
rename swl resp
label define swl5 1 "swl1" 2 "swl2" 3 "swl3" 4 "swl4" 5 "swl5"
label values item swl5
destring id, replace
sort id item
save "/Users/xichen85/Desktop/Ben/CompACT_Ptacek 2024/SWLS.dta"
export delimited using /Users/xichen85/Desktop/new.csv