library(NHLData)

tables<-c("Sch0001","Sch0102","Sch0203","Sch0304","Sch0506","Sch0607","Sch0708","Sch0809","Sch0910","Sch1011","Sch1112","Sch1213","Sch1314","Sch1415","Sch1516","Sch1718","Sch1819","Sch1920","Sch2021","Sch2122","Sch2223","Sch2324","Sch2425","Sch2526","Sch2627","Sch2728","Sch2829","Sch2930","Sch3031","Sch3132","Sch3233","Sch3334","Sch3435","Sch3536","Sch3637","Sch3738","Sch3839","Sch3940","Sch4041","Sch4142","Sch4243","Sch4344","Sch4445","Sch4546","Sch4647","Sch4748","Sch4849","Sch4950","Sch5051","Sch5152","Sch5253","Sch5354","Sch5455","Sch5556","Sch5657","Sch5758","Sch5859","Sch5960","Sch6061","Sch6162","Sch6263","Sch6364","Sch6465","Sch6566","Sch6667","Sch6768","Sch6869","Sch6970","Sch7071","Sch7172","Sch7273","Sch7374","Sch7475","Sch7576","Sch7677","Sch7778","Sch7879","Sch7980","Sch8081","Sch8182","Sch8283","Sch8384","Sch8485","Sch8586","Sch8687","Sch8788","Sch8889","Sch8990","Sch9091","Sch9192","Sch9293","Sch9394","Sch9495","Sch9596","Sch9697","Sch9798","Sch9899","Sch9900")

L<-list()
for (table in tables) {
    x<-get(table)
    ##
    df<-data.frame(agent_a=x$Home,agent_b=x$Away)
    df$date<-as.numeric(strptime(x$Date,format='%Y-%m-%d %H:%M:%S'))
    df$score_a<-x$GF
    df$score_b<-x$GA
    df$homefield<-'agent_a'
    df$winner<-ifelse(df$score_a>df$score_b,'agent_a','agent_b')
    df$winner<-ifelse(df$score_a==df$score_b,'draw',df$winner)
    L[[table]]<-df
}

df<-data.frame(do.call("rbind",L))
write.csv(df,file="nhl_post1917.csv",quote=FALSE,row.names=FALSE)
