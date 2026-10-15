##Electricity-service choice experiment (US states and Japan) from
##Murakami, K., Ida, T., Tanaka, M., & Friedman, L. (2015). Consumers' willingness to pay for renewable and nuclear
##energy: A comparative analysis between the US and Japan. Energy Economics, 50, 178-189.
##https://doi.org/10.1016/j.eneco.2015.05.002
##Data: Mendeley Data doi:10.17632/8f7g9gkxp4.1, CC BY-NC 3.0 (Mendeley public API, data_licence). File read:
##"code and data.zip": 1_california_us2012.txt, 2_Michigan_us2012.txt, 3_NewYork_us2012.txt, 4_Texas_us2012.txt,
##5_jp2013.txt (tab-separated NLOGIT files, one row per respondent x question x alternative). The zip's docx
##(NLOGIT commands and output) was read as text. Level wording from the authors' working paper (Berkeley GSPP Working
##Paper 3, Aug 2014, Tables 2 and 4), which has the same design and N as the article.
##Usage: Rscript murakami_2015.R <dir holding the five .txt files> <output dir>
##
##Online surveys of household samples: California 1,022, Michigan 1,070, New York 1,021, Texas 1,089 (Feb 2012,
##Fukushima +1 year) and Japan 4,000 (Feb 2013); the counts match the working paper's Table 5 and its observation counts
##(8,168 etc. = respondents x 8). Each respondent answered the same 8 choice questions (fixed design, all
##respondents saw the same 8 tasks, 16 distinct alternatives), each a choice between "Electricity 1" and "Electricity 2"
##(two hypothetical electricity services), no opt-out; exactly one chosen per task (checked). Exact wording not in the
##deposit (working paper: respondents "were asked to choose their preferred option from two alternatives").
##Attributes (working paper Table 2): monthly bill ($90/$100/$110/$120 US; 7000/8000/9000/10000 JPY Japan; "for a
##consumer using 1,000 kWh per month"); air emissions (NOx, SO2, CO2) as fraction of the regional average ("No
##reduction", "20% lower", "40% lower", "60% lower"); nuclear share of generation (0-30%, steps of 10); renewable share
##(0-30%). Not stored as attributes: fossil-fuel share (displayed as the remaining percentage, 90 - nuclear -
##renewable) and hydroelectric (fixed at 10%).
##Tables: two. US (four states pooled; same questionnaire, design and USD levels; the authors refer to "the US result";
##cov_state records the file) and Japan (JPY levels, separate fielding a year later).
##Restrictions: none documented (the fuel mix is constrained to sum to 100% by construction). Level weights: fixed
##design with 16 alternatives, not a probability design -> unknown. Attribute order fixed (Table 4 order, assumed).
##task = Q 1-8 (the same fixed order for all, assumed order shown), profile = A 1/2 (Electricity 1 / 2).
##State codes in the files' state column do not follow the file names (Texas = 2, Michigan = 3, New York = 4);
##the file name is used. IDs re-keyed to integers. No respondent covariates are in the deposit apart from derived
##dummies (dropped: ND1, ND2, RD1, GD1, MDL, MDH, GN, GR, GND1, GND2, GRD2, KEY, YEN duplicates USD).
##N vs paper: matches (see above).
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
fl <- list.files(raw, pattern = "[.]txt$", full.names = TRUE, recursive = TRUE)
rd <- function(pat) fread(grep(pat, fl, value = TRUE)[1])
build <- function(x, price) {
  stopifnot(x[, .N, ID][, all(N == 16)], x[, sum(CE), .(ID, Q)][, all(V1 == 1)], x[, uniqueN(paste(price(.SD), GAS, nuc, ren)), .(Q, A)][, all(V1 == 1)])
  data.table(sid = x$sid, task = as.integer(x$Q), profile = as.integer(x$A), choice = as.integer(x$CE),
    attr_monthly_bill = price(x),
    attr_air_emissions = ifelse(x$GAS == 0, "No reduction", paste0(x$GAS, "% lower")),
    attr_nuclear_share = paste0(x$nuc, "%"), attr_renewable_share = paste0(x$ren, "%"))
}
st <- c("1_california" = "California", "2_Michigan" = "Michigan", "3_NewYork" = "New York", "4_Texas" = "Texas")
us <- rbindlist(lapply(names(st), function(p) { x <- rd(p); x[, sid := paste(p, ID)]
  d <- build(x, function(z) paste0("$", z$USD)); d[, cov_state := st[[p]]]; d }))
us[, id := match(sid, unique(sid))]; us[, sid := NULL]
stopifnot(uniqueN(us$id) == 4202)
setcolorder(us, c("id", "task", "profile", "choice")); setorder(us, id, task, profile)
fwrite(us, file.path(out, "murakami_2015_electricity_us.csv"))
jp <- rd("5_jp2013"); jp[, sid := ID]
d <- build(jp, function(z) paste0(z$YEN, "JPY"))
d[, id := match(sid, unique(sid))]; d[, sid := NULL]
stopifnot(uniqueN(d$id) == 4000)
setcolorder(d, c("id", "task", "profile", "choice")); setorder(d, id, task, profile)
fwrite(d, file.path(out, "murakami_2015_electricity_japan.csv"))
