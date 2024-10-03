x<-read.csv("data.csv")
L<-list()
L$bae<-c("avo_01", "avo_02", "avo_03", "avo_04", "avo_05", 
"avo_06", "avo_07", "avo_08","esc_01", "esc_02", "esc_03", "esc_04", 
"esc_05", "esc_06", "esc_07", "esc_08", "esc_09")

L$ada<-c("ada_01", "ada_02", 
"ada_03", "ada_04", "ada_05", "ada_06", "ada_07", "ada_08", "ada_09", 
"ada_10")

L$bps<-c("bps_01", "bps_02", "bps_03", "bps_04", "bps_05", "bps_06", 
"bps_07", "bps_08")

L$beh<-c("beh_01", "beh_02", "beh_03", "beh_04", "beh_05", 
"beh_06", "beh_07", "beh_08", "beh_09", "beh_10", "beh_11", "beh_12", 
"beh_13", "beh_14", "beh_15", "beh_16", "beh_17", "beh_18", "beh_19")

id<-1:nrow(x)
for (i in 1:length(L)) {
    nms<-L[[i]]
    z<-list()
    y<-x[,nms]
    for (j in 1:ncol(y)) z[[j]]<-data.frame(id=id,item=nms[j],resp=y[,j])
    df<-data.frame(do.call("rbind",z))
    print(head(df))
    print(table(df$resp))
    print(unique(df$item))
    save(df,file=paste(names(L)[i],"_boredom_bieleke2022.Rdata",sep=""))
}
