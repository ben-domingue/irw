##Bean-seed real choice experiment (Nicaragua, 2017) from the deposit
##Maredia, M. K., Posey, S., Reyes, B., Shupp, R., et al. (2020). Farmer willingness to pay for
##quality bean seeds: Data, tools and methods used in the field experiments conducted in
##Nicaragua, 2017. Harvard Dataverse. https://doi.org/10.7910/DVN/HEYPSQ (CC0 1.0, no restricted
##files). Related publication: Posey, S. (2018). Farmer valuation of seed quality: A comparative
##analysis of two preference elicitation methods in Nicaragua (Master's thesis, Michigan State
##University).
##Files read: "RCE and BDM_public.tab" (one row per farmer) and "CHOICE EXPERIMENT DESIGN.tab"
##(the four choice sets). Design facts from "Data Documentation and Meta Data_Nicaragua
##survey_2017.pdf" (Overview pp. 3-4, variable list pp. 13-15).
##Usage: Rscript maredia_2020.R <raw dir> <output dir>
##
##Farmers in 10 villages of north-western Nicaragua, after two field days on double-blind plots
##planted with the same bean variety as Certified seed (plot "circle"), Quality Declared Seed
##(plot "square") and recycled seed (plot "triangle"), made 12 incentivized choices between two
##1-lb bags of seed identified only by plot symbol, at a price, or neither (doc p. 4: "a 12
##choice orthogonal experiment. Each choice varied in seed quality (circle, square and triangle)
##and price (Cordobas 14, 21, 28 and 34) and included an opt out. Farmers broke into 4 groups
##and each saw the choices in a different order"; one choice drawn and enforced, C$40 endowment).
##FIXED blocked design: the same 12 pairs for all; group_id W/X/Y/Z = the design file's Set
##W/X/Y/Z, which gives each set's display order (Set W lists the same order as Set X).
##task = choice situation in the set's order (option_k = k-th choice situation),
##profile 1 = Alt1 = option "a", profile 2 = Alt2 = option "b"; "n" = none (opt-out, choice 0 on
##both). trial_design_row = the design's "Orig" row (the pair's number in Set X).
##attr_seed = the plot symbol on the bag: circle / square / triangle (the design key: blind seed
##for RCE 1 = triangle, 2 = square, 3 = circle; seed quality behind each symbol given above but not
##shown on the bag). attr_price = "C$14", "C$21", "C$28", "C$34" (price per bag, cordobas).
##Wording (enumerator script "ENGLISH Script for Nicaragua Seed Auctions.pdf", Step 5; read to
##farmers in Spanish): "When you are shown each set, we want you to choose which of the two seeds
##you would purchase if you were at the market to buy seed. If you wouldn't buy either then choose
##ninguna." Each set ("Ellecion") showed two seeds with prices and a "ninguna" option; every price
##was below the C$40 endowment and only one set was binding, which the script points out.
##Dropped: farmers with no group_id (2, also no answers); 2 tasks with an invalid answer ("ab",
##"bn"); option_13 (empty in all rows). Covariates: cov_village (village code x1),
##cov_bdm_bid_circle/square/triangle (BDM willingness-to-pay bids, cordobas per lb, from the same
##session). Dropped: UniqueID (re-keyed), date, field-day plot ratings (dy*), seed quantity.
##N: 229 farmers with a choice set (doc: 231 in the file). Not checked against the thesis.
##Mapping check: per-pair choice shares in sets Y and Z correlate with those in X/W at 0.59/0.60
##under the set-order mapping used here, and at -0.29/-0.34 if option_k were read as pair k, so
##option_k follows each set's display order. Price has almost no effect on choice in any set
##(clogit price coefficient -0.02 to 0.00), perhaps because
##every price fit within the C$40 endowment; flagged, not explained.
##The deposit's hypothetical choice experiment (MOD_Z_HCE_public, 179 farmers, groups S-V) is
##NOT built: its groups do not match any set in the design file, so its pairs cannot be decoded.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
ds <- fread(file.path(raw, "CHOICE EXPERIMENT DESIGN.tab"), header = FALSE, fill = TRUE, encoding = "UTF-8")
hdr <- grep("^Design [0-9] \\(Set [WXYZ]\\)$", ds$V1)
stopifnot(length(hdr) == 4L)
sym <- c("∆" = "triangle", "□" = "square", "○" = "circle")
gs <- function(x) { s <- sub("^.*\\| *", "", x); stopifnot(all(s %in% names(sym))); unname(sym[s]) }
des <- rbindlist(lapply(hdr, function(h) {
  b <- ds[(h + 2):(h + 13)]
  data.table(set = sub("^.*Set ([WXYZ]).*$", "\\1", ds$V1[h]), task = as.integer(b$V2), orig = as.integer(b$V1),
             p1 = paste0("C$", b$V3), s1 = gs(b$V4), p2 = paste0("C$", b$V5), s2 = gs(b$V6))
}))
stopifnot(nrow(des) == 48L, des[, all(sort(task) == 1:12) & all(sort(orig) == 1:12), set]$V1)
# every set holds the same 12 pairs
stopifnot(des[, uniqueN(paste(orig, p1, s1, p2, s2))] == 12L)
r <- fread(file.path(raw, "RCE and BDM_public.tab"), encoding = "UTF-8", na.strings = "")
r <- r[group_id %in% c("W", "X", "Y", "Z")]
r[, id := .I]
ch <- melt(r[, c("id", "group_id", paste0("option_", 1:12)), with = FALSE], id.vars = c("id", "group_id"),
           variable.name = "task", value.name = "opt")
ch[, task := as.integer(sub("option_", "", task))]
ch <- ch[opt %in% c("a", "b", "n")]
x <- merge(ch, des, by.x = c("group_id", "task"), by.y = c("set", "task"))
d <- rbind(x[, .(id, task, profile = 1L, choice = as.integer(opt == "a"), attr_seed = s1, attr_price = p1, trial_design_row = orig)],
           x[, .(id, task, profile = 2L, choice = as.integer(opt == "b"), attr_seed = s2, attr_price = p2, trial_design_row = orig)])
cv <- r[, .(id, cov_village = x1, cov_bdm_bid_circle = bid_circle, cov_bdm_bid_square = bid_square, cov_bdm_bid_triangle = bid_trian)]
d <- merge(d, cv, by = "id")
stopifnot(uniqueN(d$id) == 229L, d[, sum(choice), .(id, task)][, all(V1 <= 1)], d[, .N, .(id, task)][, all(N == 2)])
setorder(d, id, task, profile)
fwrite(d, file.path(out, "maredia_2020_bean_seed_choice.csv"))
