## -rw-r--r-- 1 bd bd 2.1K Apr  2  2022 chess.rda
## -rw-r--r-- 1 bd bd  329 Apr 14  2022 DoignonFalmagne7.rda
## -rw-r--r-- 1 bd bd  275 Apr 14  2022 endm.rda
## -rw-r--r-- 1 bd bd  28K Jun  4  2013 probability.rda
## -rw-r--r-- 1 bd bd  483 Apr 14  2022 Taagepera.rda

load("probability.rda")
x<-probability
id<-1:nrow(x)
items1<-paste("b",100+1:12,sep='')
items2<-paste("b",200+1:12,sep='')
items<-c(items1,items2)
L<-list()
for (item in items) {
    after.intervention<-ifelse(item %in% items2,1,0)
    L[[item]]<-data.frame(id=id,item=item,resp=x[,item],after.intervention=after.intervention)
}
df<-data.frame(do.call("rbind",L))
save(df,file="pks_probability.Rdata")

    
