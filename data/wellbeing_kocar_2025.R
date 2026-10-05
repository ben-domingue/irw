# wellbeing_kocar_2025_swb, wellbeing_kocar_2025_ls, wellbeing_kocar_2025_wb
#
# Source: Kocar, M. S. (2025). Student Well-Being Scale in Higher Education:
# Validation and Psychometric Evaluation with Turkish Students [dataset].
# Harvard Dataverse, doi:10.7910/DVN/MPIOTX (CC0), file Dataset.omv.
# Ingestion issue: irw#1012.
#
# The deposit holds three instruments for the same 669 students. Until
# irw#2848 they were shipped together as wellbeing_kocar_2025 (retired); they
# are now one table each, named for the deposit's own variable prefixes:
#   _swb  swb1-swb19, 1-7: the Student Well-Being Scale in Higher Education
#         being validated (four subscales in the deposit: academic,
#         financial, psychological, relational; not shipped).
#   _ls   ls1-ls5, 1-5: a 5-item life-satisfaction scale (likely the SWLS;
#         the deposit does not name it).
#   _wb   wb1-wb14, 1-5: a 14-item well-being scale (likely the WEMWBS;
#         unnamed in the deposit).
# The deposit's total and subscale scores are not shipped.
# id = row number, the same in all three tables (as in the retired table).
library(dplyr)
library(tidyr)
library(jmvReadWrite)

df <- read_omv("Dataset.omv")
df <- df |>
  mutate(id = row_number())

blocks <- list(swb = paste0("swb", 1:19), ls = paste0("ls", 1:5), wb = paste0("wb", 1:14))
for (b in names(blocks)) {
  out <- df |>
    select(id, all_of(blocks[[b]])) |>
    pivot_longer(-id, names_to = "item", values_to = "resp") |>
    filter(!is.na(resp)) |>
    as.data.frame()
  cat(b, nrow(out), length(unique(out$id)), length(unique(out$item)), "\n")
  write.csv(out, paste0("wellbeing_kocar_2025_", b, ".csv"), row.names = FALSE)
}
