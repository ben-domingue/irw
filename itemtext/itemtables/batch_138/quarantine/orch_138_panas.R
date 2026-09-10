library(haven)
d <- read_sav(".cache/pierro_2018_posaffect_s3/s003.sav")
na <- as.data.frame(d[, paste0("negaffect",1:10)])
pa <- as.data.frame(d[, paste0("posaffect",1:10)])
na[] <- lapply(na, function(x) {x[x<1|x>5] <- NA; as.numeric(x)})
pa[] <- lapply(pa, function(x) {x[x<1|x>5] <- NA; as.numeric(x)})

cat("=== NA means ===\n"); print(round(colMeans(na,na.rm=TRUE),3))
cat("=== PA means ===\n"); print(round(colMeans(pa,na.rm=TRUE),3))

Rna <- cor(na, use="pairwise.complete.obs")
cat("\n=== NA: mutual top partners ===\n")
top <- sapply(1:10, function(i){ r<-Rna[i,]; r[i]<-NA; which.max(r) })
for(i in 1:10) if(top[top[i]]==i && i<top[i]) cat(sprintf("  {%d,%d} r=%.3f\n", i, top[i], Rna[i,top[i]]))

cat("\n=== NA: canonical synonym couplets {1,2}{3,7}{4,10}{5,6}{8,9} ===\n")
canon <- list(c(1,2),c(3,7),c(4,10),c(5,6),c(8,9))
for(p in canon) cat(sprintf("  {%d,%d} r=%.3f  (is mutual top? %s)\n", p[1],p[2],Rna[p[1],p[2]],
   ifelse(top[p[1]]==p[2] && top[p[2]]==p[1],"YES","no")))

# facet test under canonical NA ordering
fac <- c(4,4,3,1,2,2,3,1,1,1)  # 1=fear(scared4,nervous8,jittery9,afraid10) 2=hostility(hostile5,irritable6) 3=guilt(guilty3,ashamed7) 4=distress(distressed1,upset2)
w<-c(); b<-c()
for(i in 1:9) for(j in (i+1):10) if(fac[i]==fac[j]) w<-c(w,Rna[i,j]) else b<-c(b,Rna[i,j])
cat(sprintf("\nNA facet test (canonical): within %.3f (n=%d) vs between %.3f (n=%d), diff %+.3f\n",
  mean(w),length(w),mean(b),length(b),mean(w)-mean(b)))

# Does an alternative permutation fit better? Test observed couplets as facets
cat("\n=== PA: mutual top partners ===\n")
Rpa <- cor(pa, use="pairwise.complete.obs")
tp <- sapply(1:10, function(i){ r<-Rpa[i,]; r[i]<-NA; which.max(r) })
for(i in 1:10) if(tp[tp[i]]==i && i<tp[i]) cat(sprintf("  {%d,%d} r=%.3f\n", i, tp[i], Rpa[i,tp[i]]))
