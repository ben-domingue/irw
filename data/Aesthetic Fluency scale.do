 import excel "/Users/xichen85/Desktop/af_study3_osf.xlsx", sheet("Sheet 1 - a
> f_study3_osf") firstrow allstring
(39 vars, 2,480 obs)

. drop af_mean

. drop gender

 gen id =n
 
  reshape long Q, i(id) j (resp)
(j = 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
>  29 30 31 32 33 34 35 36)

Data                               Wide   ->   Long
-----------------------------------------------------------------------------
Number of observations            2,480   ->   89,280      
Number of variables                  38   ->   4           
j variable (36 values)                    ->   resp
xij variables:
                          Q1 Q2 ... Q36   ->   Q
-----------------------------------------------------------------------------

. rename resp item

. rename Q resp

. save "/Users/xichen85/Desktop/Aethetic Fluency Scale .dta"
file /Users/xichen85/Desktop/Aethetic Fluency Scale .dta saved

. export delimited using "/Users/xichen85/Desktop/Aethetic Fluency.csv"
file /Users/xichen85/Desktop/Aethetic Fluency.csv saved

##bd: aestheticfluency_cotter2023
