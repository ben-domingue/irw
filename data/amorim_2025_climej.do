*** This Do File creates tables from the Replication Data for: CLIMEJ — Organizational Climate Scale for Junior Enterprises: A Validation Study published by RAC-Revista de Administração Contemporânea study ***

* clear
clear

* import main dataset
import excel "DadosPublicizados.xlsx", sheet("Dados") firstrow clear

* drop old id
drop  Númerodoparticipante

* convert column names to lowercase
rename *, lower

* drop unnecessary variables
drop nomedaempresajunior quantidadedemembrosdaej quantidadedemembrosdarespond instituiçãodeensino

* renames covariates
rename idade1 cov_age
rename idade2 cov_age_category
rename gênero cov_gender
rename regiãodopaís cov_region
rename cursodegraduação cov_field_study
rename areadocnpq cov_field_cnpq
rename cargonaej cov_position_work
rename cargodeliderança cov_position_leadership
rename tempodeexperiêncianomej cov_position_experience

* adds new id
gen id = _n

* reorder variables
order id cov_*, first

* save cleaned dataset
save "amorim_2025_climej.csv", replace

* creates long data from wide data
local question_cols	climej1	climej2	climej3	climej4	climej5	climej6	climej7	climej8	climej9	climej10	climej11	climej12	climej13	climej14	climej15	climej16	climej17	climej18	climej19	climej20	climej21	climej22	climej23	climej24	climej25	climej26	climej27	climej28	climej29	climej30	climej31	climej32	climej33	climej34	climej35	climej36	climej37	climej38	climej39	climej40	climej41	climej42	climej43	climej44	climej45	climej46	climej47	climej48	climej49	climej50	climej51	climej52	climej53	climej54	climej55	climej56	climej57	climej58	climej59	climej60	climej61	climej62	climej63	climej64	climej65	climej66	climej67	climej68	climej69	climej70	climej71	climej72	climej73	climej74	climej75	climej76	climej77	climej78	climej79	climej80	climej81	climej82	climej83	climej84	climej85	climej86	climej87	climej88	climej89	climej90	climej91	climej92	climej93	climej94	climej95	climej96	climej97	climej98	climej99	climej100	climej101	climej102	climej103	climej104	climej105	climej106	climej107	climej108	climej109	climej110	climej111	climej112	climej113	climej114	climej115	climej116	climej117	climej118	climej119	climej120	climej121	climej122	climej123	climej124	climej125	climej126	climej127	climej128 desenhonotrabalho1	desenhonotrabalho2	desenhonotrabalho3	desenhonotrabalho4	desenhonotrabalho5	desenhonotrabalho6	desenhonotrabalho7	desenhonotrabalho8	desenhonotrabalho9	desenhonotrabalho10	desenhonotrabalho11	desenhonotrabalho12	desenhonotrabalho13	desenhonotrabalho14	desenhonotrabalho15	desenhonotrabalho16	desenhonotrabalho17 suporteorganizacional1	suporteorganizacional2	suporteorganizacional3	suporteorganizacional4	suporteorganizacional5	suporteorganizacional6	suporteorganizacional7	suporteorganizacional8	suporteorganizacional9 florescimentonotrabalho1	florescimentonotrabalho2	florescimentonotrabalho3	florescimentonotrabalho4	florescimentonotrabalho5	florescimentonotrabalho6	florescimentonotrabalho7	florescimentonotrabalho8

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

drop climej1	climej2	climej3	climej4	climej5	climej6	climej7	climej8	climej9	climej10	climej11	climej12	climej13	climej14	climej15	climej16	climej17	climej18	climej19	climej20	climej21	climej22	climej23	climej24	climej25	climej26	climej27	climej28	climej29	climej30	climej31	climej32	climej33	climej34	climej35	climej36	climej37	climej38	climej39	climej40	climej41	climej42	climej43	climej44	climej45	climej46	climej47	climej48	climej49	climej50	climej51	climej52	climej53	climej54	climej55	climej56	climej57	climej58	climej59	climej60	climej61	climej62	climej63	climej64	climej65	climej66	climej67	climej68	climej69	climej70	climej71	climej72	climej73	climej74	climej75	climej76	climej77	climej78	climej79	climej80	climej81	climej82	climej83	climej84	climej85	climej86	climej87	climej88	climej89	climej90	climej91	climej92	climej93	climej94	climej95	climej96	climej97	climej98	climej99	climej100	climej101	climej102	climej103	climej104	climej105	climej106	climej107	climej108	climej109	climej110	climej111	climej112	climej113	climej114	climej115	climej116	climej117	climej118	climej119	climej120	climej121	climej122	climej123	climej124	climej125	climej126	climej127	climej128 desenhonotrabalho1	desenhonotrabalho2	desenhonotrabalho3	desenhonotrabalho4	desenhonotrabalho5	desenhonotrabalho6	desenhonotrabalho7	desenhonotrabalho8	desenhonotrabalho9	desenhonotrabalho10	desenhonotrabalho11	desenhonotrabalho12	desenhonotrabalho13	desenhonotrabalho14	desenhonotrabalho15	desenhonotrabalho16	desenhonotrabalho17 suporteorganizacional1	suporteorganizacional2	suporteorganizacional3	suporteorganizacional4	suporteorganizacional5	suporteorganizacional6	suporteorganizacional7	suporteorganizacional8	suporteorganizacional9 florescimentonotrabalho1	florescimentonotrabalho2	florescimentonotrabalho3	florescimentonotrabalho4	florescimentonotrabalho5	florescimentonotrabalho6	florescimentonotrabalho7	florescimentonotrabalho8

drop if missing(item) | item == ""

* encode any needed variables
gen resp2 = resp
drop resp
rename resp2 resp
replace cov_field_study = "" if cov_field_study == "n"
destring cov_field_study, replace ignore(",") force

* reorder variables
order id item resp cov_*

* sort responses
sort item id 

* saves final dataset
export delimited using "amorim_2025_climej.csv", replace

* creates subset of tables
local base_items climej desenhonotrabalho suporteorganizacional florescimentonotrabalho
foreach prefix of local base_items {
    preserve
        keep if strpos(item, "`prefix'") == 1
        export delimited using "amorim_2025_climej_`prefix'.csv", replace
    restore
}