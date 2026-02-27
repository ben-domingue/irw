##see https://cran.r-project.org/web/packages/tirt/refman/tirt.html#sim_trt
library(tirt)
set.seed(10101)

## =========================================================================
  # Example 1: Complex Testlet Design
  # =========================================================================
  # Define the Testlet Blueprint
  trt_design <- list(
    # Testlet 1: Rasch Testlet Model (High dependence: var=0.8)
    list(model = "RaschT", n_items = 5, testlet_id = "Read_A",
         testlet_var = 0.8, b = c(-1, 1)),

    # Testlet 2: 2PL Testlet Model (Default dependence: var=0.5)
    list(model = "2PLT", n_items = 5, testlet_id = "Read_B",
         a = c(0.7, 1.3)),

    # Testlet 3: Graded Response Testlet (Polytomous, 4 categories)
    list(model = "GRT", n_items = 4, testlet_id = "Survey",
         categories = 4, testlet_var = 0.2)
  )

  # Run Simulation
trt_data <- sim_trt(n_people = 500, item_structure = trt_design)

x<-trt_data$resp


x<-trt_data$resp
id<-1:nrow(x)
L<-list()
for (i in 1:ncol(x)) L[[i]]<-data.frame(id=id,item=names(x)[i],resp=x[,i])
df<-data.frame(do.call("rbind",L))

write.csv(df,file="tirt_sim_trt.csv",quote=FALSE,row.names=FALSE)
