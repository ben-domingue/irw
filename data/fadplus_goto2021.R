##https://osf.io/rw7fe
##https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.720601/full

x<-read.csv("FAD_compare_rawdata.csv")
id<-x$id
age<-x$age
gender<-x$gender

##FAD-J (Goto et al., 2015) and FAD+ (Watanabe et al., 2014) are the Japanese translations of the free will and determinism scale, originally developed by Paulhus and Carey (2011). These two scales have the same structure, although the detailed descriptions in the items were different. Each scale consists of 27 items in a five-point Likert format
## The locus of control scale (Hazama et al., 2000) is the Japanese translation of the scale developed by Shewchuk et al. (1992). Hazama et al. (2000, 2001) have confirmed that this scale has the same factor structure as the original scale by conducting multiple surveys on different samples. Although Hazama et al. (2001) reported internal consistency of each subscale was relatively low (Cronbach's alpha ≥0.52), the following research has reported sufficient values (≥0.71) from a wider range of samples (Goto et al., 2015). The following research has also shown that the scores of this scale were correlated with self-efficacy (Tabara et al., 2000); thus, it can be interpreted as a scale that appropriately assesses the locus of control. This scale consists of seven items in a seven-point Likert format with anchors of 1 = 全く違 うと思う (“Strongly disagree”) to 7 = 全くそう思う (“Strongly agree”). There are two subscales, external (four items) and internal (three items).
## The Rosenberg self-esteem scale (Rosenberg, 1965) is widely used to assess trait self-esteem. In this study, we used the Japanese-translated scale developed by Mimura and Griffiths (2007). This scale was back-translated, and the factorial structure and reliability (Cronbach's alpha = 0.81) were tested through a large-scale survey on Japanese-speaking and English-speaking populations. The following research has tested the criterion-related validity of this scale from the viewpoint of correlation with self-scheme, depression (automatic thoughts), and happiness (Uchida and Ueno, 2010). This scale consisted of 10 items in a four-point Likert format with anchors of 1 = 強 くそう思わない (“Strongly disagree”) to 4 = 強 くそう思う (“Strongly agree”).
## The brief self-control scale (Ozaki et al., 2016) is the Japanese translation of the scale developed by Tangney et al. (2004). This scale was back-translated, and the factorial structure and reliability (Cronbach's alpha ≥0.75) were tested through multiple surveys on wide-range samples. The criterion-related validity was also tested from the viewpoint of correlation with other scales about self-regulation and a cognitive task (a stop-signal task). The brief self-control scale is widely used to assess trait self-control. This scale consists of 13 items in a five-point Likert format with anchors of 1 = 全くあてはまらない (“Not at all”) to 5 = とてもあてはまる (“Very much”).
## The global belief in a just world scale (Shirai, 2010) is the Japanese translation of the scale developed by Lipkus (1991). Shirai (2010) has reported this translated scale was sufficiently reliable (Cronbach's alpha = 0.73) and correlated with the locus of control as the previous research has reported. This scale consists of seven items in a six-point Likert format with anchors of 1 = 全くそう思わない (“Strongly disagree”) to 6 = 非常にそう思う (“Strongly agree”).

nms<-c("FAD","LOC","Rosenberg","BSCS","GBJW")
for (nm in nms) {
    ii<-grep(paste("^",nm,sep=''),names(x))
    L<-list()
    for (i in ii) L[[i]]<-data.frame(id=id,age=age,gender=gender,item=names(x)[i],resp=x[,i])
    df<-data.frame(do.call("rbind",L))
    print(nm)
    print(head(df))
    print(table(df$item))
    print(table(df$resp))
    save(df,file=paste(nm,"_fadplus_goto2021.Rdata",sep=''))
}

