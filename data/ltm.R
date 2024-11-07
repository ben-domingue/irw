library(ltm)

#WIRS
#Mobility
#LSAT
#Abortion

##Wirs
x<-WIRS
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="wirs.Rdata")

##Mobility
x<-Mobility
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="mobility.Rdata")

##LSAT
x<-LSAT
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="lsat.Rdata")

##Abortion
x<-Abortion
names(x)<-paste("item_",1:ncol(x),sep='')
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))
save(df,file="abortion.Rdata")


library(ltm)
## Brook, L., Taylor, B. and Prior, G. (1991) British Social Attitudes, 1990, Survey. London: SCPR.
# This data set comes from the Environment section of the 1990 British Social Attitudes Survey
# (Brook et al., 1991). A sample of 291 responded to the questions below:
#   Format
# All of the below items were measured on a three-group scale with response categories "very concerned", "slightly concerned" and "not very concerned":
#   LeadPetrol Lead from petrol.
# RiverSea River and sea pollution.
# RadioWaste Transport and storage of radioactive waste.
# AirPollution Air pollution.
# Chemicals Transport and disposal of poisonous chemicals.
# Nuclear Risks from nuclear power station.

data("Environment")
x = Environment |> tibble()
x.raw = x
x = x |> mutate(across(everything(),as.numeric)) |>
  mutate(id = 1:nrow(x)) |>
  pivot_longer(cols = -id,
               names_to = "item",
               values_to = "resp")
x.raw = x.raw |> mutate(id = 1:nrow(x.raw)) |>
  pivot_longer(cols = -id,
               names_to = "item",
               values_to = "resp_raw")

df = x |> left_join(x.raw, by = c("id","item"))

save(df,file="environment_ltm.Rdata")



# Description
# This data set comes from the Consumer Protection and Perceptions of Science and Technology
# section of the 1992 Euro-Barometer Survey (Karlheinz and Melich, 1992) based on a sample from
# Great Britain. The questions asked are given below:
#   Format
# All of the below items were measured on a four-group scale with response categories "strongly
# disagree", "disagree to some extent", "agree to some extent" and "strongly agree":
#   Comfort Science and technology are making our lives healthier, easier and more comfortable.
# Environment Scientific and technological research cannot play an important role in protecting the
# environment and repairing it.
# Work The application of science and new technology will make work more interesting.
# Future Thanks to science and technology, there will be more opportunities for the future generations.
# Technology New technology does not depend on basic scientific research.
# Industry Scientific and technological research do not play an important role in industrial development.
# Benefit The benefits of science are greater than any harmful effect it may have.
# Karlheinz, R. and Melich, A. (1992) Euro-Barometer 38.1: Consumer Protection and Perceptions of Science and Technology. INRA (Europe), Brussels.

data("Science")
x = Science |> tibble()
x.raw = x
x = x |> mutate(across(everything(),as.numeric)) |>
  mutate(id = 1:nrow(x)) |>
  pivot_longer(cols = -id,
               names_to = "item",
               values_to = "resp")
x.raw = x.raw |> mutate(id = 1:nrow(x.raw)) |>
  pivot_longer(cols = -id,
               names_to = "item",
               values_to = "resp_raw")

df = x |> left_join(x.raw, by = c("id","item"))

save(df,file="science_ltm.Rdata")
