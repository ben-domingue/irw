library(irwpkg)
df<-irw_fetch("promis1wave1_cesd")

#################################################################################################
##BLOCK A

##CESD-D (emotional distress – depression) – higher score, more distress (CESD4, CESD8, CESD12, CESD16 need to be recoded), https://dataverse.harvard.edu/file.xhtml?fileId=6300426&version=3.0
M<-max(df$resp)
df$resp<-ifelse(df$item %in% c("CESD4","CESD8","CESD12","CESD16"),M-df$resp,df$resp)
       
pvalue<-by(df$resp,df$item,mean)
sumscore<-by(df$resp,df$id,sum)
par(mfrow=c(2,1),mgp=c(2,1,0),mar=c(3,3,1,1))
hist(pvalue,main='',xlab='item p value')
legend("topright",bty='n',paste(length(pvalue),' items',sep=''))
hist(sumscore,main='',xlab='person sum score')
legend("topright",bty='n',paste(length(sumscore),' persons',sep=''))

resp<-irwpkg::irw_long2resp(df) ##bd. note the importance of this function
dim(df)
dim(resp)
head(df)
head(resp) ##note first column is the `id`

psych::alpha(resp[,-1])

#################################################################################################
##BLOCK B
library(mirt)
m<-mirt(resp[,-1],1,'Rasch')
plot(m,type='trace')
co<-coef(m,IRTpars=TRUE,simplify=TRUE)
d1<-co$items[,3]-co$items[,2]
d2<-co$items[,4]-co$items[,3]

par(mfrow=c(1,2),mgp=c(2,1,0))
hist(d1,main='',xlab='difference in first two thresholds')
hist(d2,main='',xlab='difference in last two thresholds')

#################################################################################################
##BLOCK C
m2<-mirt(resp[,-1],1,'rsm')
coef(m2,IRTpars=TRUE,simplify=TRUE)
plot(m2,type='trace')
## E.g., for a K = 4 category response model,
##               P(x = 0 | theta, psi) = exp(0) / G              
##       P(x = 1 | theta, psi) = exp(a(theta - b1) + c) / G      
##   P(x = 2 | theta, psi) = exp(a(2theta - b1 - b2) + 2c) / G   
## P(x = 3 | theta, psi) = exp(a(3theta - b1 - b2 - b3) + 3c) / G
## where
## G = exp(0) + exp(a(theta - b1) + c) + exp(a(2theta - b1 - b2) + 2c) +
##        exp(a(3theta - b1 - b2 - b3) + 3c)

#################################################################################################
##BLOCK D

##oos testing
nfold<-5
df$fold<-sample(1:nfold,nrow(df),replace=TRUE)
rms<-function(x) sqrt(mean(x^2))
error<-list()
for (i in 1:nfold) {
    test<-df[df$fold==i,]
    train<-df[df$fold!=i,]
    resp0<-irwpkg::irw_long2resp(train)
    m<-mirt(resp0[,-1],1,'Rasch')
    m2<-mirt(resp0[,-1],1,'rsm')
    th<-fscores(m)
    th2<-fscores(m2)
    L<-list()
    for (j in 2:ncol(resp0)) {
        jj<-extract.item(m,names(resp0)[j],)
        p<-expected.item(jj,th)
        jj<-extract.item(m2,names(resp0)[j],)
        p2<-expected.item(jj,th2)
        L[[as.character(j)]]<-data.frame(id=resp0$id,item=names(resp0)[j],p=p,p2=p2)
    }
    p<-data.frame(do.call("rbind",L))
    test$item<-paste("item_",test$item,sep='')
    test<-merge(test,p)
    error[[i]]<-c(rms(test$resp-test$p),rms(test$resp-test$p2))
}
error<-do.call("rbind",error)
error*10000

##oos testing
nfold<-5
df$fold<-sample(1:nfold,nrow(df),replace=TRUE)
rms<-function(x) sqrt(mean(x^2))
error<-list()
for (i in 1:nfold) {
    test<-df[df$fold==i,]
    train<-df[df$fold!=i,]
    resp0<-irwpkg::irw_long2resp(train)
    m<-mirt(resp0[,-1],1,'Rasch')
    m2<-mirt(resp0[,-1]/3,1,'Rasch')
    th<-fscores(m)
    th2<-fscores(m2)
    L<-list()
    for (j in 2:ncol(resp0)) {
        jj<-extract.item(m,names(resp0)[j],)
        p<-expected.item(jj,th)
        jj<-extract.item(m2,names(resp0)[j],)
        p2<-expected.item(jj,th2)
        L[[as.character(j)]]<-data.frame(id=resp0$id,item=names(resp0)[j],p=p,p2=p2)
    }
    p<-data.frame(do.call("rbind",L))
    test$item<-paste("item_",test$item,sep='')
    test<-merge(test,p)
    error[[i]]<-c(rms(test$resp-test$p),rms(test$resp-test$p2))
}
error<-do.call("rbind",error)
error*10000
