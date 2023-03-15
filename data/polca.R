#carcinoma.rda  
load("carcinoma.rda")
x<-carcinoma
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-df$resp-1
save(df,file="polca_carcinoma.Rdata")


#cheating.rda
load("cheating.rda")
x<-cheating
x$GPA<-NULL
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-df$resp-1
save(df,file="polca_cheating.Rdata")

#election.rda
load("election.rda")
x<-election
x<-x[,1:12]
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-as.numeric(substr(df$resp,1,1))
save(df,file="polca_election.Rdata")


#values.rda
load("values.rda")
x<-values
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
df$resp<-df$resp-1
save(df,file="polca_values.Rdata")
