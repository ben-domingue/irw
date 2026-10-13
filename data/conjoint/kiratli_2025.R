##Alliance-cohesion vignette experiment (US public) from
##Kiratli, O. S. (2025). The politics of alliance cohesion: Experimental evidence on American attitudes toward
##corrective measures in security partnerships. Perspectives on Politics. https://doi.org/10.1017/S1537592725103071
##Replication data: Harvard Dataverse doi:10.7910/DVN/NITW7O, CC0 1.0. Files read: "condlongcondensed.tab"
##(downloaded in original format = Stata condlongcondensed.dta with value labels, saved here as data.dta), the
##authors' "alliancecohesiondo.do" (read as text, not run) and the open-access article (design, attribute wording).
##Usage: Rscript kiratli_2025.R <dir holding data.dta> <output dir>
##
##1,993 voting-eligible US respondents (Qualtrics quota sample, fielded 12-13 November 2024 per EndDate; the
##article says December 2024), each rating FIVE vignettes (9,965 rows = 1,993 x 5): "Country X, an ally of the
##US, [act]. Country X has a [regime type], [military power], [formal alliance]. In response, the US government
##plans to [corrective measure]." Five randomized attributes (article, "multifactorial vignette"; fully
##randomized, approximately uniform; no restriction mentioned, none observed):
##  attr_uncooperative_act: Veto = blocks the accession of a new member into the alliance despite US demands;
##    Break sanctions = breaks US sanctions against a third country; Rival weapons = purchases weapons from Russia
##    and China that are incompatible with the American systems; Underspending = refuses to meet the 2% GDP
##    defense spending target; No troops = refuses to send troops to a joint operation with the US. The deposit
##    labels only the short names (the authors' figure labels); the sentences are the article's template wording
##    (not verbatim screens), mapped by the short names.
##  attr_us_response: Break alliance / Economic measures / Denounce / Reduce support / No change, stored as the
##    article's template wording (break the alliance; impose economic measures, such as trade restrictions or
##    financial penalties; publicly denounce; reduce military support; continue current policies without change).
##  attr_regime: authoritarian / partially democratic / democratic; attr_military_power: basic / average /
##    advanced military capabilities (the article says "moderate" for the middle level; the deposit label
##    "average" is kept); attr_formal_treaty: an informal alliance with the US / a treaty-based alliance with the
##    US. Value labels of the deposit.
##Task = row order within respondent (each respondent has exactly 5 rows; the deposit has no task column, so the
##order is INFERRED and may not be the display order); profile = 1. Attribute order shown is the article's format.
##Outcomes (article; all single-profile ratings; no choice/opt-out):
##  rating (Q3) "How much do you agree with the proposed action toward Country X?" 0 (do not agree at all) - 10
##    (agree completely); rating_alliance_favorability (Q4) "How favorable are you to having an alliance with
##    Country X?" 0 (not favorable at all) - 10 (the article says 0 to 11; the data run 0-10);
##  rating_contribution (Q5) "Should the government increase, maintain, or reduce its financial and military
##    contributions to this alliance?" stored 1 = Increase, 2 = Keep the same, 3 = Decrease (deposit value labels;
##    the article's rescaled sQ5 is 11/6/1). Lower = more favourable to the alliance; stored raw.
##    Q4 and Q5 were asked in random order after Q3.
##Covariates: cov_gender (Q2_2: 1 Female, 2 Male), cov_education (edu value labels, text), cov_party_id7 (partisan:
##Strong Democrat ... Strong Republican; "not sure / prefer not to answer" -> NA), cov_attention_pass (1 =
##Q14_1_3 equals 6, the authors' filter `keep if Q14_1_3==6` for every figure; 1,502 respondents, matching the
##article's N = 1,502; the other 491 failed the attention check and are KEPT, flagged 0).
##Dropped: ResponseId (Qualtrics id; respondents re-keyed 1..1993 in file order), EndDate, scaled_var and sQ5
##(derived), Q14_1_x foreign-policy items, Q16 trust/interest, ideology, income, race, Hispanic origin, employment,
##region, state (and codes).
##Count check: attention-check passers 1,502 respondents = article N; 1,502 x 5 = 7,510 rows ("over 7,500
##observations"). Spot check: mean rating by uncooperative act / US response in the 1,502 (see the build).
library(data.table); library(haven)
a <- commandArgs(TRUE); raw <- a[1]; out <- a[2]
r <- as.data.table(read_dta(file.path(raw, "data.dta")))
stopifnot(nrow(r) == 9965, uniqueN(r$ResponseId) == 1993)
# respondent ids in order of first appearance; task = running row within respondent
r[, id := match(ResponseId, unique(ResponseId))]
r[, task := seq_len(.N), by = id]
stopifnot(r[, .N, id][, all(N == 5)])
lab <- function(v) { l <- attr(r[[v]], "labels"); setNames(names(l), as.character(l)) }
unlab <- function(x, l) { y <- unname(l[as.character(as.integer(x))]); stopifnot(!anyNA(y)); y }
act <- c("Veto" = "blocks the accession of a new member into the alliance despite US demands",
         "Break sanctions" = "breaks US sanctions against a third country",
         "Rival weapons" = "purchases weapons from Russia and China that are incompatible with the American systems",
         "Underspending" = "refuses to meet the 2% GDP defense spending target",
         "No troops" = "refuses to send troops to a joint operation with the US")
resp <- c("Break alliance" = "break the alliance with Country X",
          "Economic measures" = "impose economic measures against Country X, such as trade restrictions or financial penalties",
          "Denounce" = "publicly denounce Country X's actions",
          "Reduce support" = "reduce military support to Country X",
          "No change" = "continue current policies without change")
la <- lab("actionn1x"); lc <- lab("corrective")
stopifnot(setequal(la, names(act)), setequal(lc, names(resp)))
pid <- c("1" = "Strong Democrat", "2" = "Weak Democrat", "3" = "Independent, close to Democrat", "4" = "Independent",
         "5" = "Independent, close to Republican", "6" = "Weak Republican", "7" = "Strong Republican")
stopifnot(all(r$Q3 %in% 0:10), all(r$Q4 %in% 0:10), all(r$Q5 %in% 1:3))
d <- data.table(id = r$id, task = r$task, profile = 1L, rating = as.integer(r$Q3),
                rating_alliance_favorability = as.integer(r$Q4), rating_contribution = as.integer(r$Q5),
                attr_uncooperative_act = act[unlab(r$actionn1x, la)], attr_us_response = resp[unlab(r$corrective, lc)],
                attr_regime = unlab(r$countryn1x, lab("countryn1x")), attr_military_power = unlab(r$countryn2x, lab("countryn2x")),
                attr_formal_treaty = unlab(r$countryn3x, lab("countryn3x")),
                cov_gender = c("1" = "female", "2" = "male")[as.character(as.integer(r$Q2_2))],
                cov_education = unlab(r$edu, lab("edu")), cov_party_id7 = unname(pid[as.character(as.integer(r$partisan))]),
                cov_attention_pass = as.integer(as.integer(r$Q14_1_3) == 6L))
stopifnot(!anyNA(d$cov_gender), d[, uniqueN(cov_attention_pass), id][, all(V1 == 1)], d[cov_attention_pass == 1, uniqueN(id)] == 1502)
setorder(d, id, task, profile)
fwrite(d, file.path(out, "kiratli_2025_alliance_cohesion.csv"))
