# paper. https://link.springer.com/article/10.3758/s13428-023-02130-4
#data. https://osf.io/au6m5/
#study3
library(haven)
library(dplyr)
library(tidyr)

data <- read_spss("MicroPROMS_data_S3.sav")
data <- data %>% 
  mutate(across(everything(), ~`attr<-`(.x, "label", NULL)))

data <- data %>%
  select(id, Age, MMQ_K1:MMQ_N7, GMSI1_AE01:GMSI3_EM06, M2_cod:B12_t2_cod) %>%
  rename(age = Age)

data1 <- data %>%
  pivot_longer(
    -c(id, age), 
    names_to = "item", 
    values_to = "resp"
  )


df<-as.data.frame(data1)
microprom<-c("M2","M11","M12","TU12","TU17","TU18","TB14","TB16","TE5","TE12","R4","R12","R18","P10","P12","A3","A5","A12")
mp<-paste(microprom,"_cod",sep="")

mp[!mp %in% df$item]

df<-df[df$item %in% mp,]
table(df$item,df$resp)

save(df,file="microproms_strauss2023.Rdata")
