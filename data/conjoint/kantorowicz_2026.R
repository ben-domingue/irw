##Consumer-rights product conjoints (computers; laundry machines) from
##Kantorowicz-Reznichenko, E., van Heusden, A., & Kantorowicz, J. (2026). Consumers' rights in
##the shadow of the brand: A conjoint experiment on the valuation and trade-offs of contractual
##rights. Journal of Law & Empirical Analysis, 3(1), 105-126. https://doi.org/10.1177/2755323X261438858
##Replication data: Harvard Dataverse doi:10.7910/DVN/EWOHKJ, CC0 1.0. Files read:
##computers.RDS, laundry_machines.RDS; script_final.R read as text (not run). The article was
##not accessible (publisher 403); the deposit has no codebook or questionnaire.
##Usage: Rscript kantorowicz_2026.R <raw dir> <output dir>
##
##US sample (article abstract: representative US sample), 2,238 respondents. Two experiments on
##the same respondents, with different attribute sets, so two tables:
##  kantorowicz_2026_rights_computers: brand (Medion, Apple MacBook, Lenovo, HP), price,
##    processor, storage, RAM + four contract terms (warranty, conflict resolution, liability,
##    privacy).
##  kantorowicz_2026_rights_laundry: brand (Haier, Hoover, General Electric, Whirlpool), price,
##    depth, noise, load capacity + the same four contract terms.
##Each task showed 2 products; choice = `selected` (one of the two chosen in every task; the
##question wording is not deposited). Up to 6 tasks per experiment.
##Task / profile reconstruction (INFERRED, no id columns in the RDS): each RDS is the output of
##reshape(direction = "long", timevar = "profile", times = 1:2) (its "reshapeLong" attribute):
##rows 1..N/2 are profile 1 and rows N/2+1..N are profile 2 of the same task, in the same order.
##Checked here: row i and row i + N/2 always have the same respondent and exactly one chosen.
##Within the first half the rows come in stacked task blocks (all respondents' task 1, then
##task 2, ...), each block listing respondents in one fixed order; task = block number, a new
##block starting where that respondent order jumps back by more than 500 positions. Checked: 6
##blocks, no respondent twice in a block. Block number is taken as the task's position in the
##experiment's sequence; whether computer and laundry tasks were interleaved is not documented.
##Levels are the RDS factor labels with surrounding spaces trimmed. Privacy levels ("No
##privacy", "No privacy: marketing", "No privacy: sustainability", "Full privacy") look like the
##authors' short labels; the displayed sentences are not deposited. Attribute names as shown
##(from the reshapeLong attribute): "Conflict resolution: who decides in which jurisdiction a
##lawsuit will be heard, and whether it will be in-front of a court or arbitration", "Liability:
##who bears the costs in case of a loss arising out of the use of the product", "Privacy: what
##will be done with your personal data which you provide in the process of purchase?".
##Attribute row positions (*.rowpos) existed in the wide data, so attribute order was
##randomized, but they are not in the RDS; no attrpos_ columns.
##Dropped: the authors' derived dichotomies (Brand_Familiarity, age/gender/education/income/
##risk/analytical/trust dummies, consistent_switch). Response.ID re-keyed to integers (the same
##integer for a respondent in both tables). No weight in the deposit.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
x1 <- readRDS(file.path(raw, "computers.RDS")); x2 <- readRDS(file.path(raw, "laundry_machines.RDS"))
ids <- data.table(rid = sort(unique(c(x1$Response.ID, x2$Response.ID)), method = "radix"))[, id := .I]
build <- function(x, attrs, nm) {
  stopifnot(identical(attr(x, "reshapeLong")$timevar, "profile"))
  h <- nrow(x) / 2; i <- seq_len(h)
  stopifnot(h == round(h), all(x$Response.ID[i] == x$Response.ID[i + h]), all(x$selected[i] + x$selected[i + h] == 1))
  b <- data.table(rid = x$Response.ID[i])
  u <- unique(b$rid); b[, rk := match(rid, u)]
  b[, task := 1L + cumsum(c(0L, diff(rk) < -500L))]
  stopifnot(max(b$task) == 6, b[, .N, .(rid, task)]$N == 1)
  d <- rbind(cbind(b[, .(rid, task)], profile = 1L, x[i, c("selected", attrs)]),
             cbind(b[, .(rid, task)], profile = 2L, x[i + h, c("selected", attrs)]))
  setnames(d, "selected", "choice")
  for (v in attrs) {
    d[[v]] <- trimws(as.character(d[[v]])); stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
    setnames(d, v, paste0("attr_", tolower(gsub("\\.", "_", v))))
  }
  d <- merge(d, ids, by = "rid")[, rid := NULL]
  setcolorder(d, c("id", "task", "profile", "choice"))
  d[, choice := as.integer(choice)]
  setorder(d, id, task, profile)
  cat(nm, ": respondents", uniqueN(d$id), " tasks", nrow(d) / 2, "\n")
  fwrite(d, file.path(out, paste0(nm, ".csv")))
}
build(x1, c("Brand", "Price", "Processor", "Storage.Capacity", "RAM", "Warranty", "Conflict.Resolution", "Liability", "Privacy"),
      "kantorowicz_2026_rights_computers")
build(x2, c("Brand", "Price", "Depth", "Noise", "Load.Capacity", "Warranty", "Conflict.Resolution", "Liability", "Privacy"),
      "kantorowicz_2026_rights_laundry")
