##Provider-choice discrete choice experiment with caretakers of children with diarrhoea (India) from
##Wagner, Z., Mohanan, M., Mukherji, A., Zutshi, R., Patil, S., Krishnappa, J., Banerjee, S., &
##Sood, N. (2025). Investigating the know-do gap in antibiotics prescribing: Experimental evidence
##from India. Science Advances, 11. https://doi.org/10.1126/sciadv.ady9868
##Replication data: Harvard Dataverse doi:10.7910/DVN/5FXWC3, CC0 1.0. Files read: HH_dce.tab
##(original Stata HH_dce.dta, value labels), readme.docx, "Figure 2.do" (as text). Design facts:
##article (PMC12422172), Methods "Discrete choice experiment". know_do_gap.dta (provider data) not used.
##Usage: Rscript wagner_2025.R <dir holding HH_dce.dta> <output dir>
##
##1,189 caretakers (household survey, Karnataka and Bihar; article: "DCE with 1189 caretakers who
##recently visited a provider for their child's diarrhea"; matches). Each choice set showed two
##providers ("Caretakers were asked to choose among 2 providers", readme); outcome `chosen`
##(exactly one per set, forced choice, no opt-out). Fixed blocked design: 48 blocks (`block`,
##"random number between 1 to 48"), 192 design choice sets (`choice`, kept as trial_choice_set),
##each (block, set, profile) always has the same levels. task = `set` (1-4), profile =
##`profile_order` (1-2), both recorded. The article says each respondent saw EIGHT choice sets; the
##deposit has at most 4 sets per household (1,176 households with 4, 13 with fewer): flagged, not
##resolved. id = hhid (a town/enumerator/serial composite) re-keyed to integers.
##Three versions (article: "we had three versions of the DCE, each including only four attributes.
##Kindness, quality rating, and name were always included, and we randomly varied whether medicines
##prescribed, doctor fee, or time to clinic were also included"); a household saw one version
##(constant within household in the data). The two attributes left out of a version are stored as
##"(not shown)" (the .dta codes them 4/6 with value label "NA"); trial_version names the extra
##attribute shown (medicine / price / time).
##Level text = the .dta value labels (English; the language read/shown to caretakers is not
##documented): medicine ("2 packets of sugar salt solution", "+ 10 zinc tablets", "+ bottle of
##antibiotic syrup", "Bottle of antibiotic syrup", "Injection"), price (doctor fee "100"/"300"/"500",
##INR per Figure 2.do), time to clinic, kindness ("Provider is rude and talks down to patients" /
##"Provider is very kind and friendly to patients"), quality ("1 Star"/"3 Stars"/"5 Stars").
##attr_name is the authors' CATEGORY of the provider name ("Dalit name", "Hindu name", "Muslim name");
##the names actually shown are not in the deposit.
##Respondents were told to assume all providers have a 30-min wait, air-conditioned facility,
##central location (article). Dropped: submissiondate, result/qdce1/qdce2 (interview status;
##all result = completed), select, v1 (design bookkeeping), the set-level id. No covariates or
##weights in the DCE file.
library(haven); library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
s <- read_dta(file.path(raw, "HH_dce.dta"))
L <- function(v) { x <- as.character(as_factor(s[[v]], levels = "labels")); ifelse(x == "NA", "(not shown)", x) }
s <- as.data.table(s)
stopifnot(nrow(s) == 9480L, uniqueN(s$hhid) == 1189L, all(s$result == 1))
d <- data.table(hid = s$hhid, task = as.integer(s$set), profile = as.integer(s$profile_order), choice = as.integer(s$chosen),
                attr_medicine = L("medicine"), attr_price = L("price"), attr_time = L("time"), attr_kindness = L("treat"),
                attr_quality = L("quality"), attr_name = paste(L("name"), "name"),
                trial_choice_set = as.integer(s$choice), trial_block = as.integer(s$block))
d[, trial_version := fifelse(attr_medicine != "(not shown)", "medicine", fifelse(attr_price != "(not shown)", "price", "time"))]
stopifnot(d[, (attr_medicine != "(not shown)") + (attr_price != "(not shown)") + (attr_time != "(not shown)")] == 1L,
          d[, uniqueN(trial_version), hid][, all(V1 == 1)], d[, .(sum(choice), .N), .(hid, task)][, all(V1 == 1 & N == 2)],
          s[, .(uniqueN(paste(name, quality, treat, time, price, medicine))), .(block, set, profile_order)][, all(V1 == 1)])
for (v in grep("^attr_", names(d), value = TRUE)) stopifnot(!anyNA(d[[v]]), all(d[[v]] != ""))
d[, id := match(hid, sort(unique(hid)))][, hid := NULL]
setcolorder(d, c("id", "task", "profile", "choice"))
setorder(d, id, task, profile)
fwrite(d, file.path(out, "wagner_2025_provider_choice.csv"))
