not_data<-"metadata"
dataset<-redivis::organization("datapages")$
    dataset("Item Response Warehouse",version="v4.0")
dataset_tables <- dataset$list_tables()
##
print(length(dataset_tables))
names<-sapply(dataset_tables,function(x) x$name)
ii<-grep("metadata",names)
names(dataset_tables)<-names
if (length(ii)>0) dataset_tables<-dataset_tables[-ii]   
##
f<-function(table) table$list_variables()
nms<-lapply(dataset_tables,f)

##
f<-function(x) {
    nm<-sapply(x,function(x) x$name)
    "rt" %in% nm
}
test<-sapply(nms,f)
rt_data<-dataset_tables[test]
    
proc<-function(table) {
    df<- table$to_data_frame()
    df$resp<-ifelse(df$resp=="NA",NA,df$resp)
    df$rt<-ifelse(df$rt=="NA",NA,df$rt)
    df<-df[!is.na(df$resp),]
    df<-df[!is.na(df$rt),]
    #
    z<-as.numeric(df$rt)
    z<-z[z>0 & z<60*30]
    z<-log(z)
    z<-(z-mean(z))/sd(z)
    qq<-qqnorm(z,plot.it=FALSE)
    qq<-cbind(qq$x,qq$y)
    qq<-qq[order(qq[,1]),]
    qq[(seq(1,nrow(qq),length.out=500)),]
}
dens<-lapply(rt_data,proc)

pdf("~/Dropbox/Apps/Overleaf/IRW/rt.pdf",width=3,height=3)
cc<-col2rgb("red")
cc<-rgb(cc[1],cc[2],cc[3],max=255,alpha=75)
par(mgp=c(2,1,0),mar=c(3,3,.1,.1))
plot(NULL,xlim=c(-6,6),ylim=c(-6,6),
     xlab="theoretical quantiles",ylab="sample quantiles")
abline(0,1,lwd=2)
for (i in 1:length(dens)) lines(dens[[i]],col=cc)
dev.off()
