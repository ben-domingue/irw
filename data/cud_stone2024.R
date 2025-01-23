##https://osf.io/nswbk/?view_only=
##https://link.springer.com/article/10.1007/s11469-023-01231-7

##time 1
## get file "T1 CUD Severity.sav"
## *Gender:
##    Men = 1
##    Women = 2
## RELIABILITY
##   /VARIABLES=OCTKTIME OCTKFREQ OCTKSOCL OCDISTRS OCRESIST OCDIVERT OCURGEOF OCURGETM OCURGESC 
##     OCUPSET OCEFFORT OCSTRONG OCCONTRL
##   /SCALE('ALL VARIABLES') ALL
##   /MODEL=ALPHA
##   /STATISTICS=DESCRIPTIVE SCALE
##   /SUMMARY=TOTAL.
library(haven)
x <- read_sav("T1 CUD Severity.sav")
items<-c("OCTKTIME","OCTKFREQ","OCTKSOCL","OCDISTRS","OCRESIST","OCDIVERT","OCURGEOF","OCURGETM","OCURGESC","OCUPSET","OCEFFORT","OCSTRONG","OCCONTRL")
id<-x$PATID
z<-as.character(x$OCMASMDT)
date<-as.numeric(strptime(z,format="%Y-%m-%d"))
L<-list()
for (item in items) L[[as.character(item)]]<-data.frame(id=id,item=item,date=date,resp=x[[item]])
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(ifelse(df$resp=="",NA,df$resp))
df1<-df
                                        #write.csv(df,file="cud_t1severity_stone2024.csv",quote=FALSE,row.names=FALSE)


##MCPLEAS MCLIMIT MCPLANS MCCONTRL MCSLEEP MCTENSE MCNOCTRL MCGREAT MCANXOUS MCNEED MCNERVUS MCCONTNT
x <- read_sav("T2 Cravings.sav")
items<-c("MCPLEAS","MCLIMIT","MCPLANS","MCCONTRL","MCSLEEP","MCTENSE","MCNOCTRL","MCGREAT","MCANXOUS","MCNEED","MCNERVUS","MCCONTNT")
id<-x$PATID
z<-as.character(x$MCQASMDT)
date<-as.numeric(strptime(z,format="%Y-%m-%d"))
L<-list()
for (item in items) L[[as.character(item)]]<-data.frame(id=id,item=item,date=date,resp=x[[item]])
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(ifelse(df$resp=="",NA,df$resp))
df2<-df
                                        #write.csv(df,file="cud_t2cravings_stone2024.csv",quote=FALSE,row.names=FALSE)

##mps1_yn mps2_yn mps3_yn mps4_yn mps5_yn mps6_yn mps7_yn mps8_yn mps9_yn mps10_yn mps11_yn mps12_yn mps13_yn mps14_yn mps15_yn mps16_yn mps17_yn mps18_yn mps19_yn
x <- read_sav("T3 Problems.sav")
items<-c("mps1_yn","mps2_yn","mps3_yn","mps4_yn","mps5_yn","mps6_yn","mps7_yn","mps8_yn","mps9_yn","mps10_yn","mps11_yn","mps12_yn","mps13_yn","mps14_yn","mps15_yn","mps16_yn","mps17_yn","mps18_yn","mps19_yn")
id<-x$PATID
z<-as.character(x$MPSASMDT)
date<-as.numeric(strptime(z,format="%Y-%m-%d"))
L<-list()
for (item in items) L[[as.character(item)]]<-data.frame(id=id,item=item,date=date,resp=x[[item]])
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(ifelse(df$resp=="",NA,df$resp))
df3<-df
                                        #write.csv(df,file="cud_t3problems_stone2024.csv",quote=FALSE,row.names=FALSE)


df<-data.frame(rbind(df1,df2,df3))
write.csv(df,file="cud_stone2024.csv",quote=FALSE,row.names=FALSE)



