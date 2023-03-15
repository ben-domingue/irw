## abany
## a binary variable that equals 1 if the respondent thinks abortion should be legal for any reason. 0 indicates no support for abortion for any reason.
## abdefect
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if there is a serious defect in the fetus. 0 indicates no support for abortion in this circumstance.
## abnomore
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if a woman is pregnant but wants no more children. 0 indicates no support for abortion in this circumstance.
## abhlth
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if a pregnant woman's health is in danger. 0 indicates no support for abortion in this circumstance.
## abpoor
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if a pregnant woman is poor and cannot afford more children. 0 indicates no support for abortion in this circumstance.
## abrape
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if the woman became pregnant because of a rape. 0 indicates no support for abortion in this circumstance.
## absingle
## a numeric vector that equals 1 if the respondent thinks abortion should be legal if a pregnant woman is single and does not want to marry the man who impregnated her. 0 indicates no support for abortion in this circumstance.

x<-read.csv("gss_abortion.csv")
year<-x$year
sex<-x$sex
age<-x$age
id<-1:nrow(x)

x<-x[,c("abany","abdefect","abnomore","abhlth","abpoor","abrape","absingle")]
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,year=year,sex=sex,age=age,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

save(df,file="RDatasets_gssabortion.Rdata")



