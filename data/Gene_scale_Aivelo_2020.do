import delimited "gene_likert_aivelo2020.csv", clear 
drop school date course_bi1 course_bi2 course_bi3 course_bi4 course_bi5 course_oth course_tot gender age teacher_app textbook
drop v40
rename form id
foreach i of numlist 1/25 {
    rename X`i' Q`i'
foreach i of numlist 1/25 {
    rename x`i' Q`i'
}
reshape long Q, i(id) j(resp)
rename resp item
rename Q resp
save "Gene_scale_Aivelo_2020.do.dta"
export delimited using Gene_scale_Aivelo_2020.csv