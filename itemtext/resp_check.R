

f<-function(tab) {
    items<-irw::irw_itemtext(tab)
    df<-irw::irw_fetch(tab)
    i1<-unique(items$resp)
    i2<-unique(df$resp)
    test1<-all(i1 %in% i2)
    test2<-all(i2 %in% i1)
    test1 & test2
}

tables<-c("coach_chen_2022_phq9","gilbert_meta_1","coach_chen_2022_hdrs","gilbert_meta_12","gilbert_meta_49","oxfordcovid_xue_2024_gad","gilbert_meta_53","gilbert_meta_54","gilbert_meta_59","gilbert_meta_62","gilbert_meta_7","gilbert_meta_88","gilbert_meta_89","gilbert_meta_90","gilbert_meta_91","gilbert_meta_92")
out<-lapply(tables,f)
z<-data.frame(tables,unlist(out))
z[!z[,2],]

