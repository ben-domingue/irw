remove<-NULL #c('')

##all tables
lt<-irw::irw_list_itemtext_tables()
lt<-lt[!lt %in% remove]

##tables with data already
library(redivis)
user <- redivis$user("bdomingu")
dataset <- user$dataset("irw_meta")
table <- dataset$table("itemtext_metadata")
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
    nc.option<-rep(NA,length(nc))
    if ("option_text" %in% names(items)) nc.option<-sapply(items$option_text,nchar)
    instrument<-rep(NA,length(nc))
    if ("instrument" %in% names(items)) instrument<-items$instrument
    L[[tab]]<-data.frame(table=tab,instrument=instrument,item=items$item,item_text=z,nw=nw,nc=nc,nc.option=nc.option)
}

save(L,file="items_alltext.Rdata")

f<-function(x) {
    mnw<-mean(x$nw)
    mnc<-mean(x$nc)
    if ('instrument' %in% names(x)) instrument<-unique(x$instrument) else instrument<-NA
    if ('nc.option' %in% names(x)) nco<-mean(x$nc.option) else nco<-NA
    data.frame(table=unique(x$table),instrument=unique(x$instrument),mean_word=mnw,mean_character=mnc,mean_character_responses=nco)
}
z<-lapply(L,f)
z<-data.frame(do.call("rbind",z))


#############################################
merge.new<-z
df<-data.frame(rbind(merge.new,merge.old[,names(merge.new)]))

write.csv(df,file="itemtext_metadata.csv",quote=TRUE,row.names=FALSE)


######################### This is broken. doesn't run correctly at present.
##get flesch-kincaid
load("items_alltext.Rdata")
library(koRpus)
library(koRpus.lang.en)
rdb<-list()
for (i in 1:length(L)) {
    df<-L[[i]]
    write.table(df$item_text,file="/tmp/text.txt",row.names=FALSE,quote=FALSE)
    zz<-tokenize(
        "/tmp/text.txt",
        lang="en",
        doc_id="sample")
    hy<-hyphen(zz)
    rdb[[names(L)[i] ]]<-readability(zz, hyphen=hy,index="Flesch.Kincaid")
}
fk<-sapply(rdb,function(x) x@Flesch.Kincaid$age)
fk<-data.frame(table=names(fk),FleschKincaid.age=fk)
z<-merge(z,fk)




