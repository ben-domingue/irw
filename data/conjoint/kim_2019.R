##Costa Rican firms' trade-policy paired conjoint from
##Kim, I. S., Milner, H. V., Bernauer, T., Osgood, I., Spilker, G., & Tingley, D. (2019).
##Firms and global value chains: Identifying firms' multidimensional trade preferences.
##International Studies Quarterly, 63(1), 153-167. https://doi.org/10.1093/isq/sqy055
##Replication data: Harvard Dataverse doi:10.7910/DVN/RT8CHM, CC0 1.0. Files read:
##conjoint_final.csv (long, one row per respondent x vignette x policy; Dataverse original
##format) and crsurvey_full.csv (Qualtrics wide export; only the conjoint display columns
##F.<task>.<pos> = attribute name at row <pos>, F.<task>.<profile>.<pos> = level shown, and the
##response ID are read). Design text: web_appendix_conjoint.pdf A1/A2.
##Usage: Rscript kim_2019.R <raw dir> <output dir>
##
##Survey of Costa Rican firms (Qualtrics, Nov 2013 - Feb 2014; the respondent answers for the
##firm). Up to 5 tasks of 2 trade policies ("Política Comercial 1/2"), 5 attributes, shown in
##Spanish. Levels are stored as the Spanish text in the Qualtrics display columns (the export
##stores them without accents, e.g. "debil", "Proteccion a la inversion extranjera"); they
##differ from the web appendix's Spanish table (which lists pequeña/mediana/grande, a stray
##"moderate" and the English 2-level dispute attribute): the display columns are what Qualtrics
##showed. Attribute names: attr_dispute = Uso de mecanismos de solucion de diferencias,
##attr_flex = Flexibilidad de los compromisos internacionales, attr_barriers = Reduccion de las
##barreras arancelarias y no arancelarias, attr_invest = Proteccion a la inversion extranjera,
##attr_subsidy = Subsidio a la exportacion.
##Attribute row order was randomized once per respondent (the same order in all 5 tasks in the
##display columns); attrpos_* record it.
##choice = `select` from conjoint_final.csv: "Luego por favor indique cuál es la política que su
##empresa preferiría" (forced choice, no opt-out; appendix A2, Table A1 note).
##Task = vignette_id (task number in the display columns). Profile position: conjoint_final.csv
##has no profile column; each (respondent, task) has two rows in separate halves of the file.
##Each long row is matched to profile 1 or 2 of the same task in the display columns through its
##5 levels (authors' English codes <-> displayed Spanish: baja/bajo = low, moderada/moderado =
##moderate, grande/alto = high, debil = weak, fuerte = strong, agresivo = aggresive, pasivo =
##passive); a task is kept only when the two rows match the two displayed profiles one-to-one.
##Dropped: 1 task with no chosen policy; tasks whose profiles could not be matched (count
##printed). The survey export holds respondent names, e-mails, IP addresses, GPS coordinates and
##company names; none of these is read beyond the response ID, which is re-keyed to integers.
##No firm covariates kept. No survey weight in the deposit.
##Counts: 325 respondents / 1,595 tasks here. The paper analyses the 214 firms in tradable
##industries (crsurvey_final.csv) who did the conjoint, 1,049 tasks (appendix Figure A3); all
##325 respondents are kept here. Randomization rules are not documented.
library(data.table)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
L <- fread(file.path(raw, "conjoint_final.csv"))
S <- fread(file.path(raw, "crsurvey_full.csv"), encoding = "UTF-8",
           select = c("V1", grep("^F\\.[1-5]\\.", names(fread(file.path(raw, "crsurvey_full.csv"), nrows = 0)), value = TRUE)))
an <- c("Uso de mecanismos de solucion de diferencias" = "dispute",
        "Flexibilidad de los compromisos internacionales" = "flex",
        "Reduccion de las barreras arancelarias y no arancelarias" = "barriers",
        "Proteccion a la inversion extranjera" = "invest",
        "Subsidio a la exportacion" = "subsidy")
W <- rbindlist(lapply(1:5, function(t) rbindlist(lapply(1:5, function(k) rbindlist(lapply(1:2, function(p)
  data.table(V1 = S$V1, task = t, pos = k, profile = p, aname = S[[sprintf("F.%d.%d", t, k)]],
             lev = S[[sprintf("F.%d.%d.%d", t, p, k)]])))))))
W <- W[V1 %in% L$resp_id]
stopifnot(all(W$aname %in% names(an)), !anyNA(W$lev), all(W$lev != ""))
W[, att := an[aname]]
stopifnot(W[, .(n = uniqueN(att)), .(V1, task, profile)]$n == 5)
## attribute order per respondent, constant across tasks
po <- unique(W[, .(V1, task, att, pos)]); stopifnot(po[, .(n = uniqueN(pos)), .(V1, att)]$n == 1)
P <- dcast(W, V1 + task + profile ~ att, value.var = "lev")
Q <- dcast(unique(W[, .(V1, task, profile, att, pos)]), V1 + task + profile ~ paste0("attrpos_", att), value.var = "pos")
P <- merge(P, Q, by = c("V1", "task", "profile"))
code <- c(baja = "low", bajo = "low", moderada = "moderate", moderado = "moderate", grande = "high", alto = "high",
          debil = "weak", fuerte = "strong", agresivo = "aggresive", pasivo = "passive")
stopifnot(all(unlist(P[, .(dispute, flex, barriers, invest, subsidy)]) %in% names(code)))
P[, key := paste(code[dispute], code[flex], code[barriers], code[invest], code[subsidy])]
L[, key := paste(dispute, flex, reduc_barrier, invest, subsidy)]
L[, row := .I]
m <- merge(L[, .(V1 = resp_id, task = vignette_id, key, select, row)], P[, .(V1, task, profile, key)],
           by = c("V1", "task", "key"), allow.cartesian = TRUE)
## keep tasks where the 2 long rows map one-to-one onto profiles 1 and 2
ok <- m[, .(n = .N, np = uniqueN(profile), nr = uniqueN(row)), .(V1, task)][n == 2 & np == 2 & nr == 2]
nt <- uniqueN(L[, .(resp_id, vignette_id)])
m <- m[ok, on = c("V1", "task")]
ch <- m[, .(s = sum(select)), .(V1, task)][s == 1]
cat("tasks in long file:", nt, " matched one-to-one:", nrow(ok), " with one chosen:", nrow(ch), "\n")
m <- m[ch, on = c("V1", "task")]
d <- merge(m[, .(V1, task, profile, choice = as.integer(select))], P, by = c("V1", "task", "profile"))
ids <- data.table(V1 = unique(d$V1))[order(V1)][, id := .I]
d <- merge(d, ids, by = "V1")
setnames(d, c("dispute", "flex", "barriers", "invest", "subsidy"), paste0("attr_", c("dispute", "flex", "barriers", "invest", "subsidy")))
d <- d[, c("id", "task", "profile", "choice", paste0("attr_", c("dispute", "flex", "barriers", "invest", "subsidy")),
           paste0("attrpos_", c("dispute", "flex", "barriers", "invest", "subsidy"))), with = FALSE]
stopifnot(d[, .(.N, sum(choice)), .(id, task)][, all(N == 2 & V2 == 1)])
setorder(d, id, task, profile)
cat("respondents:", uniqueN(d$id), " tasks:", nrow(d) / 2, "\n")
fwrite(d, file.path(out, "kim_2019_trade_policy_firms.csv"))
