dataset <- redivis::organization("datapages")$
    dataset("Item Response Warehouse")
dataset_tables <- dataset$list_tables()
names(dataset_tables) <- sapply(dataset_tables, function(x) x$name)
f <- function(table) table$list_variables()
nms <- lapply(dataset_tables, f)
f <- function(x) {
    nm <- sapply(x, function(x) x$name)  # Extract names of variables
    "treat" %in% nm 
}
test <- sapply(nms, f)
rct_tables <- dataset_tables[test]

il_hte <- function(tab) {
    nm<-tab$name
    print(nm)
    df <- tab$to_data_frame()
    df$resp<-as.numeric(df$resp)
    ##downsample
    ids<-unique(df$id)
    if (length(ids)>1000) {
        ids<-sample(ids,1000)
        df<-df[df$id %in% ids,]
    }
    ## 1PL IL-HTE model with lme4
    m<-lme4::lmer(resp ~ treat + (1|id) + (treat|item),df) ##LPM for efficiency
    list(nm,lme4::ranef(m)$item[,2])
}

library(parallel)
L<-mclapply(rct_tables[1:15],il_hte,mc.cores=5)

##figure. compare to figure 1 here: https://arxiv.org/pdf/2405.00161
est<-sapply(L,function(x) x[[2]])
par(mgp=c(2,1,0),mar=c(3,10,1,1))
plot(NULL,xlim=range(unlist(est)),ylim=c(1,length(L)),yaxt='n',ylab='',xlab="Item-level treatment effects")
for (i in 1:length(L)) {
    xv<-L[[i]][[2]]
    points(xv,rep(i,length(xv)),pch=19)
    mtext(side=2,line=0,at=i,L[[i]][[1]],cex=.7,las=2)
}
