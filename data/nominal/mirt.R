library(mirt)
L<-list()
set.seed(101010)

#########################################################################################################
#### 10 item GGUMs test with 4 categories each
a <- rlnorm(10, .2, .2)
b <- rnorm(10) #passed to d= input, but used as the b parameters
diffs <- t(apply(matrix(runif(10*3, .3, 1), 10), 1, cumsum))
t <- -(diffs - rowMeans(diffs))

dat <- simdata(a, b, 1000, 'ggum', t=t)
apply(dat, 2, table)
# mod <- mirt(dat, 1, 'ggum')
# coef(mod)

### 10 items with the hyperbolic cosine model with differing category lengths
a <- matrix(1, 10)
d <- rnorm(10)
rho <- matrix(1:2, nrow=10, ncol=2, byrow=TRUE)
rho[1:2,2] <- NA   # first two items have K=2 categories

dat <- simdata(a, d, 1000, 'hcm', rho=rho)
itemstats(dat)
# mod <- mirt(dat, 1, 'hcm')
                                        # list(est=coef(mod, simplify=TRUE)$items, pop=cbind(a, d, log(rho)))
L$mirt_ggum<-dat


#########################################################################################################
### An example of a mixed item, bifactor loadings pattern with correlated specific factors

a <- matrix(c(
.8,.4,NA,
.4,.4,NA,
.7,.4,NA,
.8,NA,.4,
.4,NA,.4,
.7,NA,.4),ncol=3,byrow=TRUE)

d <- matrix(c(
-1.0,NA,NA,
 1.5,NA,NA,
 0.0,NA,NA,
0.0,-1.0,1.5,  #the first 0 here is the recommended constraint for nominal
0.0,1.0,-1, #the first 0 here is the recommended constraint for gpcm
2.0,0.0,NA),ncol=3,byrow=TRUE)

nominal <- matrix(NA, nrow(d), ncol(d))
# the first 0 and last (ncat - 1) = 2 values are the recommended constraints
nominal[4, ] <- c(0,1.2,2)

sigma <- diag(3)
sigma[2,3] <- sigma[3,2] <- .25
items <- c('2PL','2PL','2PL','nominal','gpcm','graded')

dataset <- simdata(a,d,2000,items,sigma=sigma,nominal=nominal)
L$mirt_mixed<-dataset

#########################################################################################################
#### Unidimensional nonlinear factor pattern

theta <- rnorm(2000)
Theta <- cbind(theta,theta^2)

a <- matrix(c(
.8,.4,
.4,.4,
.7,.4,
.8,NA,
.4,NA,
.7,NA),ncol=2,byrow=TRUE)
d <- matrix(rnorm(6))
itemtype <- rep('2PL',6)

nonlindata <- simdata(a=a, d=d, itemtype=itemtype, Theta=Theta)
L$mirt_nonlin<-nonlindata


#########################################################################################################
for (i in 1:length(L)) {
    l<-list()
    x<-L[[i]]
    id<-1:nrow(x)
    for (j in 1:ncol(x)) l[[j]]<-data.frame(id=id,item=colnames(x)[j],resp=x[,j])
    df<-data.frame(do.call("rbind",l))
    write.csv(df,file=paste(names(L)[i],".csv",sep=""),quote=FALSE,row.names=FALSE)
}
