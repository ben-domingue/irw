library(EstCRM)
set.seed(101301)

  ## Not run: 
  
  #####################################################
  #                      Example 1:                   #
  #   Basic data generation and parameter recovery    #
  #####################################################
  
  #Generate true person ability parameters for 1000 examinees from 
  #a standard normal distribution
  
  true.thetas <- rnorm(1000,0,1)
  
  #Generate the true item parameter matrix for the hypothetical items
  
  true.par <- matrix(c(.5,1,1.5,2,2.5,
  -1,-.5,0,.5,1,1,.8,1.5,.9,1.2),
  nrow=5,ncol=3)
  true.par
  
  #Generate the vector maximum possible scores that students can 
  #get for the items
  
  max.item <- c(30,30,30,30,30)
  
  #Generate the response matrix
  
simulated.data <- simCRM(true.thetas,true.par,max.item)


x<-simulated.data
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

write.csv(df,file="estcrm.csv",quote=FALSE,row.names=FALSE)
