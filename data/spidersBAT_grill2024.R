x<-read.csv("Daten_rl_v_DIPS_komplett.csv",sep="|")
ii<-grep("^SP",names(x))
sp<-x[,ii]
dim(sp) #The SPQ is a 31-item self-report scale measuring spider phobia symptom severity via a dichotomous response format (“Yes” vs. “No”; German Version by Hamm, 2006; original by Klorman et al., 1974). It is widely used and has been shown to be reliable and valid (Hamm, 2006). The internal consistency in our sample was α = .95.
ii<-grep("^FA",names(x))
fs<-x[,ii]
dim(fs) #FSQ is an 18-item self-report scale also measuring spider phobia symptom severity (German version by Rinck et al., 2002; original by Szymanski & O’Donohue, 1995). Items are rated on a 7-point Likert scale ranging from 0 = not at all to 6 = very much. It is frequently used to corroborate findings from the SPQ (e.g., Haberkamp et al., 2019) and has shown good psychometric qualities (Rinck et al., 2002). The internal consistency in our sample was α = .97.

id<-1:nrow(x)
L1<-L2<-list()
for (i in 1:ncol(sp)) L1[[i]]<-data.frame(id=id,item=names(sp)[i],resp=sp[,i])
for (i in 1:ncol(fs)) L1[[i]]<-data.frame(id=id,item=names(fs)[i],resp=fs[,i])
L<-c(L1,L2)
df<-data.frame(do.call("rbind",L))

save(df,file="spidersBAT_grill2024.Rdata")
