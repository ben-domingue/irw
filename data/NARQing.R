x<-read.csv("narqing_analysis_data_2023-09-19.csv")
id<-x$id_num
ethnic_category<-x$ethnic_cat
x<-x[,c("narq_1", "narq_2", "narq_3", "narq_4", 
"narq_5", "narq_6", "narq_7", "narq_8", "narq_9", "narq_10", 
"narq_11", "narq_12", "narq_13", "narq_14", "narq_15", "narq_16", 
"narq_17", "narq_18", "rse_1", "rse_2", "rse_3", "rse_4", "rse_5", 
"rse_6", "rse_7", "rse_8", "rse_9", "rse_10", "meim_1", "meim_2", 
"meim_3", "meim_4", "meim_5", "meim_6", "meim_7", "meim_8", "meim_9", 
"meim_10", "meim_11", "meim_12")]

L<-list()
for (i in 1:ncol(x)) {
    L[[i]]<-data.frame(id=id,ethnic_category=ethnic_category,
                       item=names(x)[i],
                       resp=as.numeric(x[,i])
    )
}
df<-data.frame(do.call("rbind",L))
save(df,file="NARQing.Rdata")
