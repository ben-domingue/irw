read.csv("HYM_BSI_PROMIS_Dep_dat.csv")->x
ii<-grep("^depression",names(x))
cov_age<-x$actual_age_yr
cov_gender<-x$gender
id<-1:nrow(x)
L<-list()
for (i in ii) L[[as.character(i)]]<-data.frame(id=id,item=names(x)[i],resp=x[,i],
                                               cov_age=cov_age,cov_gender=cov_gender)
df<-data.frame(do.call("rbind",L))

write.csv(df,file="depression_hymcohort_tang2022.csv",quote=FALSE,row.names=FALSE)
