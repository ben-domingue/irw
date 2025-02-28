##data from here. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260621#sec002

library(foreign)
x<-read.spss("journal.pone.0260621.s002.sav",to.data.frame=TRUE,use.value.labels=FALSE)
names(x)<-tolower(names(x))
id<-1:nrow(x)
sex<-x$sex
age<-x$age

## Dickman Impulsivity Inventory (DII) [5]. This is a 23-item self-report measure of impulsivity that consists of two scales: f
## Basic Empathy Scale (BES) [25]. This is a 20-item self-report measure of empathy that consists of two scales
## Reactive-Proactive Aggression Questionnaire (RPQ) [27]. This is a 23-item self-report measure of aggression that consists of two scales
## Youth Psychopathic Traits Inventory–Triarchic–Short (YPI-Tri-S) [29]. This is a 21-item brief measure of the Triarchic model of psychopathy that consists of three scales
nms<-c("iid","bes","rpq","ypitris")
for (nm in nms) {
    ii<-grep(paste("^",nm,sep=''),names(x))
    z<-x[,ii]
    if (nm=='rpq') z<-z[,1:23]
    print(dim(z))
    L<-list()
    for (i in 1:ncol(z)) L[[i]]<-data.frame(id=id,cov_sex=sex,cov_age=age,item=names(z)[i],resp=z[,i])
    df<-data.frame(do.call("rbind",L))
    if (nm=='iid') df<-df[df$resp!=4,] #we adopted a four-point format 
    if (nm=='rpq') df<-df[df$resp!=3,] #Each item is scored on an ordinal 3-point Likert scale 
    write.csv(df,paste("pechorro_impulsivity_2021_",nm,".csv",sep=''),quote=FALSE,row.names=FALSE)
}
