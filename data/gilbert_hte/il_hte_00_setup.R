# IL-HTE Econ, Setup: libraries, paths, shared column definitions
# Source: Josh Gilbert's IL-HTE Econ cleaning code, "00 clean_il_hte_econ.qmd"
# (gilbert_share/06 IL-HTE Econ/analysis/), split into one file per dataset (#2765).
# Code is verbatim; the qmd's prose is kept as comments. Dataset N here is IRW
# table gilbert_meta_N.

knitr::opts_chunk$set(echo = TRUE)
knitr::opts_chunk$set(fig.align = "center")
knitr::opts_chunk$set(warning = FALSE)
knitr::opts_chunk$set(message = FALSE)

# First, download the data sets and put them in a folder with the metadata called `data/raw`. Output from this file will go to the `data/clean` folder.

# # R Setup

# Below, I declare the parameters of the computing environment and create a few convenience functions.

# load libraries
library(tidyverse)
library(haven)
library(glue)
library(sjlabelled)
library(readxl)
library(janitor)
library(dtplyr)
library(mirt)

# clear memory
rm(list = ls())

# set seed for reproducibility
set.seed(2024)

# path to raw data
# place the raw data sets in "raw"
raw <- "data/raw"
clean <- "data/clean"

# irt scoring function
rasch_score <- function(data, string){
  data |> 
    select(matches(string)) |> 
    # fit the rasch model
    mirt(1, itemtype = "Rasch", verbose = FALSE)
}

# create the clean folder, if needed
dir.create("data/clean")

# # Load and Clean Data

# We put the data in standard format for analysis. We make the following simplifications for interpretability:

# -   When there are multiple types of treatment, we simplify to compare any treatment to the control condition. Details are noted with each data source.

# -   We consider only treatment assignment to provide ITT effects.

# -   We assume simple randomization at the individual level.

# -   For outcome measures of polytomous responses, we dichotomize. For example, a 1-4 strongly disagree to strongly agree Likert scale is changed to agree/disagree. Details are noted with each data source.

# -   Where item level data is available for the pretest measure, we use Rasch models to score the measure.

# -   Subjects must answer at least one outcome item to be included in the analysis.

# The key variables for each data set are as follows:

# 1.  `score`: 0/1 where 1 = correct answer or endorsing the item

# 2.  `polyscore`: categorical response for polytomous items

# 3.  `treat`: 0/1 where 1 = randomly assigned to treatment

# 4.  `std_baseline`: standardized baseline data score. For datasets with baseline items, this is a Rasch score constructed from those items (created in the subsequent file)

# 5.  `s_id`: subject identifier

# 6.  `item`: item identifier

# 7.  `cluster_id`: clustering variable for randomization, if applicable

# 8.  `block_id`: randomization block, if applicable

# 9.  `time`: time of test administration. 0 = baseline, 1 = endline

# 10. `cov_`: some covariate
