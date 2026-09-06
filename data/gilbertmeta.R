##Code for post-processing of data described in https://arxiv.org/abs/2405.00161

# load libraries
library(tidyverse)
library(sjlabelled)
library(glue)

# set ggplot themes
theme_set(theme_bw())
theme_update(legend.position = "bottom", legend.box = "vertical")

# clear memory
rm(list = ls())

# set seed for reproducibility
set.seed(2024)

# load the data
load("/Users/jog1638/Library/CloudStorage/Dropbox-Personal/HGSE/Active Papers/04 IL-HTE Econ/analysis/data/clean/datasets_list.Rdata")

# total numbers
map_dbl(datasets, nrow) |> sum()
map_dbl(datasets, ~ distinct(., s_id) |> nrow()) |> sum()
map_dbl(datasets, ~ distinct(., item) |> nrow()) |> sum()

# create a function
irw_clean <- function(data, num){
  
  out <- data
  
  # is the outcome polytomous?
  dichotomous <- is.null(data$polyscore)
  
  # get total time points
  # if only 1, don't need the time var
  n_time <- unique(data$time) |> length()
  
  # if polytomous, remove dichotomized score
  if(dichotomous == FALSE){
    out <- out |> 
      select(-score) |> 
      rename(resp = polyscore)
  } else {
    out <- out |> 
      rename(resp = score)
  }
  
  # Dataset 31's `cov_age` is baseline age in **months**, not years, and a
  # recorded 0 means missing -- both confirmed by Josh Gilbert on 2026-09-05
  # (irw#1856). Untouched it shipped a median age of 108 and a maximum of 219
  # on an ASER primary-school sample, and `irw_filter()` read every one of
  # those as a year. `datastandard.md` requires `cov_age` in years.
  #
  # Handled here rather than at source so a re-run cannot reintroduce it. If the
  # upstream `datasets_list.Rdata` is ever changed to years, delete this block
  # -- the guard below will fail loudly rather than halve the ages twice.
  if(num == 31 && "cov_age" %in% names(out)){
    stopifnot(max(out$cov_age, na.rm = TRUE) > 120)   # still months?
    out <- out |>
      mutate(cov_age = ifelse(cov_age == 0, NA_real_, cov_age / 12))
  }

  # get the output file
  out <- out |> 
    remove_all_labels() |> 
    mutate(item = factor(item),
           across(contains("_id"), ~ factor(.))) |> 
    arrange(s_id, item, time, resp) |> 
    relocate(contains("_id"), item, time, resp) |> 
    # rename for IRW standard
    rename(id = s_id) |> 
    select(-contains("outcome"))

  if(n_time == 1){
    out <- out |> 
      select(-time)
  }
  
  # write csv
  write_csv(out, glue("data/irw_data_{num}.csv"))
  
}

# export the csvs in the IRW format
num <- length(datasets)

walk2(datasets, 1:num, irw_clean, 
      .progress = TRUE)


##bd addendum
lf<-list.files(pattern="*.csv")
for (fn in lf) {
    print(fn)
    x<-read.csv(fn)
    i<-grep("time",names(x))
    if (length(i)>0) {
        names(x)[i]<-'wave'
    }
    i<-strsplit(fn,'_')[[1]]
    i<-sub(".csv","",i[3])
    i<-as.numeric(i)
    fn0<-paste("gilbert_meta_",i,sep="")
    df<-x
    save(df,file=paste("/tmp/proc/",fn0,".Rdata",sep=""))
    write.csv(df,quote=FALSE,row.names=FALSE,file=paste("/tmp/proc/",fn0,".csv",sep=""))
}

##rm
##remove study 3 though, that’s simulated based on the models in our SSRI paper

