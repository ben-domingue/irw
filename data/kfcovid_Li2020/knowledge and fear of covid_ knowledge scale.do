 import excel "/Users/xichen85/Desktop/Ben-test- data_ knowledge and fear of covi
> d/Knowledge and Fear of COVID-19 and Perceived Stress.xls", sheet("DataSet") fir
> strow allstring
(30 vars, 115 obs)

. drop Age Gender

. 
. . drop AA Survey1Total Survey2Total Survey3Total

. 
. . drop in 111/115
(5 observations deleted)

. (5 observations deleted)
( is not a valid command name
r(199);

. edit

. drop Q101 Q102 Q103 Q104 Q105 Q106 Q107 Q1001 Q1002 Q1003 Q1004

. reshape long Q, i(ID) j (resp)
(j = 1 2 3 4 5 6 7 8 9 10 11 12)

Data                               Wide   ->   Long
-----------------------------------------------------------------------------
Number of observations              110   ->   1,320       
Number of variables                  13   ->   3           
j variable (12 values)                    ->   resp
xij variables:
                          Q1 Q2 ... Q12   ->   Q
-----------------------------------------------------------------------------

. rename ID id

. 
. . rename resp item

. 
. . rename Q resp

. edit

. sort id

. edit

. destring id, replace
id: all characters numeric; replaced as int

. sort id

. edit

. sort id item

. edit

. 
. save "/Users/xichen85/Desktop/knowledge and fear of covid_knowledge scale.dta"
file /Users/xichen85/Desktop/knowledge and fear of covid_knowledge scale.dta
    saved

. export delimited id item resp using "/Users/xichen85/Desktop/Knowledge and Fear 
> of Covid.csv"
file /Users/xichen85/Desktop/Knowledge and Fear of Covid.csv saved

