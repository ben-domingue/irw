##all tables
lt<-irw::irw_list_itemtext_tables()

##tables with data already
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta:bdxt")
table <- dataset$table("itemtext_metadata:drat")
xxx <- table$to_tibble()

##tables.new will need to be processed
tables.new<-lt[!lt %in% xxx$table]
merge.old<-as.data.frame(xxx)

################################################
##processing tables.new
L<-list()
for (ii in 1:length(tables.new)) {
    print(ii/length(tables.new))
    tab<-tables.new[ii]
    items<-irw::irw_itemtext(tab)
    if ("item_text_translated" %in% names(items)) {
        z<-items$item_text_translated
    } else {
        z<-items$item_text
    }
    l<-strsplit(z,' ')
    nw<-sapply(l,length)
    nc<-sapply(z,nchar)
    nc.option<-sapply(items$option_text,nchar)
    L[[tab]]<-data.frame(table=tab,instrument=items$instrument,item=items$item,nw=nw,nc=nc,nc.option=nc.option)
}
df<-data.frame(do.call("rbind",L))

f<-function(x) {
    mnw<-mean(x$nw)
    mnc<-mean(x$nc)
    data.frame(table=unique(x$table),mean_word=mnw,mean_char=mnc)
}
z<-lapply(L,f)
z<-data.frame(do.call("rbind",z))
merge.new<-z

merge.old$sample<-merge.old$construct<-NULL
df<-data.frame(rbind(merge.new,merge.old[,names(merge.new)]))

save(z,file="descriptives.Rdata")
