##prepring data for analysis
df$item<-paste("item_",df$item,sep="")
##reformatting to typical response matrix format
library(irw)
resp<-irw::long2resp(df)
resp$id<-NULL

##cronbach's alpha
psych::alpha(resp)
##dimensionality analysis
paran::paran(resp)
##basic factor analysis
psych::fa(cov(resp),nfactors=3)
##basic unidimensional irt analysis
mirt::mirt(resp,1,"Rasch")

