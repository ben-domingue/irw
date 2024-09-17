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
