##full formatting done in: gilbert_share/06 IL-HTE Econ/analysis/

##goto 06 IL-HTE Econ/analysis/data/clean

load("il_hte_data.Rdata")
vars<-ls()
L<-list()
for (nm in vars) L[[nm]]<-get(nm)
f<-function(x) {
    id<-x$s_id
    pretest<-x$std_baseline
    resp<-x$score
    treat<-x$treat
    item<-x$item
    data.frame(id=id,item=item,resp=resp,treatment=treat,pretest=pretest)
}
L<-lapply(L,f)

lapply(L,function(x) table(x$resp))

for (i in 1:length(L)) {
    fn<-paste("/home/bdomingu/Dropbox/projects/irw/data/queue/",names(L)[i],".Rdata",sep='')
    df<-L[[i]]
    save(df,file=fn)
}


write.table(names(L),quote=FALSE,row.names=FALSE) #so that you can map data to paper

