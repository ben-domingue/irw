## https://onlinelibrary.wiley.com/doi/epdf/10.1111/ajps.12400?saml_referrer
## https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZSJA25&version=1.1

load("Risk_Data_Base.RData")

chars<-c(appropriate='a',
         priority='p',
         disaster='d',
         fairness='f',
         harm='h',
         incidence='i',
         longterm='l',
         worry='w'
         )

id<-1:nrow(table)
txt<-character()
for (ii in 1:length(chars)) {
    for (i in 1:4) for (j in 1:15) txt[paste(i,j)]<-paste(paste(rep(chars[ii],i),collapse='',sep=''),j,sep='')
    L<-list()
    for (i in 1:length(txt)) {
        z<-table[,c(txt[i],paste(txt[i],"n",sep=''))]
        for (j in 1:2) z[,j]<-ifelse(z[,j]=="",NA,z[,j])
        z$rater<-id
        z<-z[rowSums(is.na(z[,1:2]))<2,]
        names(z)[1:2]<-c("agent_a","agent_b")
        z$winner<-"agent_a"
        L[[i]]<-z
    }
    df<-data.frame(do.call("rbind",L))
    print(head(df))
    write.csv(df,file=paste("friedman2019_risk_",names(chars)[ii],".csv",sep=''),quote=FALSE,row.names=FALSE)
}
