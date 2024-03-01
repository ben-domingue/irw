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

https://docs.google.com/document/d/1-w0nlQZWpLqb0jB990NsBF1FucGaYVqJN3qw0-BRetc/edit

##see here: https://psycnet.apa.org/doi/10.1037/dev0001710

## kim2021_a, https://link.springer.com/article/10.1007/s10648-021-09609-6
## kim2021_b, 
## kim2021_c, 

## kim2024_a, https://psycnet.apa.org/doi/10.1037/dev0001710
## kim2024_b,https://psycnet.apa.org/doi/10.1037/dev0001710

##already in irw. i would update to this version (ie delete old version; will also need to manage file names etc.

## kim2023, https://doi.org/10.1037/edu0000751
content_literacy_intervention.Rdata & g1
