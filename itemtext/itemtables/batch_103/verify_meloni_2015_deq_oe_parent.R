# verify_meloni_2015_deq_oe_parent.R -- Step 5b.
# Route 3 (published subscale totals: Fig 1 of the article) + route 8 (semantic
# coherence of the category x stimulus interaction). Parents only (S1 Protocol 101-181).
#
# WHAT IS INFERRED. The 36 item codes are NOT inferred: data/meloni_2015_disability.py
# melts the S1 workbook's DEQ_OE_* columns by name for the parent rows, so the IRW item
# code IS the source column name (core-model derivation pattern 1). What IS inferred is
# what each code's two halves NAME -- the stimulus block (MD/SD/CD/ND) and the nine
# coder-assigned disability-model categories (Eth/Est/Rel/Med/Env/SRel/Bio/Oth/Idont),
# because the S2 codebook prints the categories and the four questions but never prints
# a variable code.
#
# ROUTE 3. Fig 1 of the article prints the PARENTS' mean frequency preference for the
# three macro models: individual 1.9, social 1.39, biopsychosocial 0.14. S2's Table 1A
# defines those as the presence (0/1) of the category group in each of the THREE
# disability conditions (motor, sensory, intellectual), summed -> a 0-3 score, with
# individual = {Ethical, Aesthetic, Religious, Medical}, social = {Environmental,
# Socio-relational}, biopsychosocial = {Biopsychosocial}. If ND were a disability
# condition, or the category grouping were shifted, the three published means could not
# be reproduced together. Rival condition triples are computed and printed for contrast.
#
# ROUTE 8. Two content predictions that follow from the CATEGORY NAMES:
#   - "Aesthetic Model" (a judgement of beauty/ugliness) should never be coded for a
#     person whose difficulty is a disability, and only for the able-bodied woman (ND).
#   - "I don't know" is stated in S2 to be "usually more common in children than in
#     adults", so it should be empty throughout the parent rows.
#   - "Environmental Model" (architectural barriers) should peak for the wheelchair user
#     (MD) and bottom out for the autistic child (CD); "Socio-Relational Model"
#     (attitudes, prejudice, communication) should peak for the autistic child.
#
# LIVE TIE. The deposit is the thing the routes above are computed on, so the live IRW
# table is tied to it by a per-item fingerprint -- n, resp_min, resp_max and number of
# distinct resp levels for all 36 codes -- taken from irw::irw_table_sets(), which is a
# server-side aggregate and does NOT export the table.
#
# NOT ESTABLISHED by any of this: the order of Ethical vs Religious vs Medical within the
# individual group, of Environmental vs Socio-relational within the social group, or of
# Other vs I-don't-know; and MD/SD/CD are separated only by the route-8 content ordering,
# not by any published per-condition number. Status is PARTIAL for that reason.

suppressMessages(library(irw))
TABLE <- "meloni_2015_deq_oe_parent"

CATS  <- c("Eth", "Est", "Rel", "Med", "Env", "SRel", "Bio", "Oth", "Idont")
CONDS <- c("MD", "SD", "CD", "ND")
IND <- c("Eth", "Est", "Rel", "Med"); SOC <- c("Env", "SRel"); BIO <- "Bio"
PUB <- c(individual = 1.9, social = 1.39, biopsychosocial = 0.14)  # Fig 1, Parents
TOL <- 0.01

ok  <- logical(0)
say <- function(lbl, val, pass) {
    ok[[length(ok) + 1L]] <<- pass
    cat(sprintf("%-104s %s\n", paste0(lbl, ": ", val), if (pass) "OK" else "FAIL"))
}

## ---- the deposit (S1 Data), parents only ------------------------------------
url   <- paste0("https://journals.plos.org/plosone/article/file",
                "?type=supplementary&id=10.1371/journal.pone.0128876.s001")
cache <- ".cache/meloni_2015_deq_oe_parent/s001.xls"
if (!file.exists(cache)) {
    dir.create(dirname(cache), recursive = TRUE, showWarnings = FALSE)
    try(download.file(url, cache, mode = "wb", quiet = TRUE), silent = TRUE)
}
if (!file.exists(cache)) stop("could not obtain S1 Data (", url, ")")
suppressMessages(library(readxl))
s1 <- as.data.frame(readxl::read_excel(cache, sheet = "Dataset_S1"))
p  <- s1[s1$Protocol >= 101 & s1$Protocol <= 199, ]
cat(sprintf("S1 parent rows: %d\n\n", nrow(p)))

col   <- function(cond, cat) as.numeric(p[[sprintf("DEQ_OE_%s_%s", cond, cat)]])
pres  <- function(cond, grp) as.integer(Reduce(`+`, lapply(grp, function(g) col(cond, g))) > 0)
score <- function(conds, grp) Reduce(`+`, lapply(conds, function(cd) pres(cd, grp)))

## ---- route 3: Fig 1 ---------------------------------------------------------
cat("ROUTE 3 -- Fig 1, parents' mean frequency preference (0-3 presence score)\n")
cat(sprintf("%-26s %10s %10s %8s\n", "conditions summed", "model", "published", "observed"))
obs <- c(individual = mean(score(c("MD","SD","CD"), IND)),
         social     = mean(score(c("MD","SD","CD"), SOC)),
         biopsychosocial = mean(score(c("MD","SD","CD"), BIO)))
for (m in names(PUB))
    cat(sprintf("%-26s %10s %10.2f %8.4f\n", "MD+SD+CD (shipped)", m, PUB[[m]], obs[[m]]))
worst <- max(abs(obs - PUB))
say("route 3 all three published means reproduced", sprintf("max |diff| = %.4f (tol %.2f)", worst, TOL), worst <= TOL)

cat("\nrival condition triples (should NOT reproduce Fig 1):\n")
rivals <- list(c("MD","SD","ND"), c("MD","CD","ND"), c("SD","CD","ND"))
rival_worst <- sapply(rivals, function(cs)
    max(abs(c(mean(score(cs, IND)), mean(score(cs, SOC)), mean(score(cs, BIO))) - PUB)))
for (i in seq_along(rivals))
    cat(sprintf("  %-26s ind %.4f  soc %.4f  bio %.4f   max|diff| %.4f\n",
                paste(rivals[[i]], collapse = "+"),
                mean(score(rivals[[i]], IND)), mean(score(rivals[[i]], SOC)),
                mean(score(rivals[[i]], BIO)), rival_worst[i]))
say("every rival triple misses Fig 1 by more than the shipped one",
    sprintf("best rival %.4f vs shipped %.4f", min(rival_worst), worst),
    min(rival_worst) > worst + TOL)

## ---- route 8: category x stimulus content -----------------------------------
cat("\nROUTE 8 -- mean coded mentions, category x stimulus\n")
cat(sprintf("%-6s %s\n", "", paste(sprintf("%7s", CATS), collapse = "")))
M <- sapply(CATS, function(cc) sapply(CONDS, function(cd) mean(col(cd, cc))))
for (cd in CONDS)
    cat(sprintf("%-6s %s\n", cd, paste(sprintf("%7.3f", M[cd, ]), collapse = "")))

say("Aesthetic Model coded only for the able-bodied stimulus (ND)",
    sprintf("MD %.3f SD %.3f CD %.3f ND %.3f", M["MD","Est"], M["SD","Est"], M["CD","Est"], M["ND","Est"]),
    all(M[c("MD","SD","CD"), "Est"] == 0) && M["ND","Est"] > 0)
say("'I don't know' never coded in the parent rows",
    sprintf("max over stimuli = %.3f", max(M[, "Idont"])), max(M[, "Idont"]) == 0)
say("Environmental Model peaks at the wheelchair stimulus, bottoms at the autistic one",
    sprintf("MD %.3f > SD %.3f > CD %.3f", M["MD","Env"], M["SD","Env"], M["CD","Env"]),
    M["MD","Env"] > M["SD","Env"] && M["SD","Env"] > M["CD","Env"])
say("Socio-Relational Model peaks at the autistic stimulus",
    sprintf("CD %.3f vs MD %.3f SD %.3f ND %.3f", M["CD","SRel"], M["MD","SRel"], M["SD","SRel"], M["ND","SRel"]),
    M["CD","SRel"] == max(M[, "SRel"]))
say("Medical Model peaks at the blind stimulus and is lowest at the able-bodied one",
    sprintf("SD %.3f, ND %.3f", M["SD","Med"], M["ND","Med"]),
    M["SD","Med"] == max(M[, "Med"]) && M["ND","Med"] == min(M[, "Med"]))

## ---- live tie: per-item fingerprint -----------------------------------------
cat("\nLIVE TIE -- per-item fingerprint, deposit vs irw_table_sets() (no export)\n")
s  <- irw::irw_table_sets(TABLE, source = "core", per_item = TRUE)
pi <- as.data.frame(s$per_item)
rownames(pi) <- pi$item
bad <- character(0)
for (cd in CONDS) for (cc in CATS) {
    it <- sprintf("DEQ_OE_%s_%s", cd, cc)
    v  <- col(cd, cc); v <- v[!is.na(v)]
    dep <- c(length(v), min(v), max(v), length(unique(v)))
    liv <- as.numeric(c(pi[it, "n"], pi[it, "resp_min"], pi[it, "resp_max"], pi[it, "n_resp_levels"]))
    if (!isTRUE(all.equal(dep, liv))) {
        bad <- c(bad, it)
        cat(sprintf("  MISMATCH %-18s deposit %s | live %s\n", it,
                    paste(dep, collapse = "/"), paste(liv, collapse = "/")))
    }
}
cat(sprintf("  fingerprints compared: %d, mismatches: %d\n", length(CONDS) * length(CATS), length(bad)))
say("every live item code reproduces its S1 column's n/min/max/levels",
    sprintf("%d/%d", length(CONDS) * length(CATS) - length(bad), length(CONDS) * length(CATS)),
    length(bad) == 0)

cat("\nNot established: order within {Ethical, Religious, Medical}, within {Environmental,\n",
    "Socio-relational}, or Other vs I-don't-know beyond the content checks above; MD/SD/CD\n",
    "are separated only by route-8 content ordering, not by a published per-condition number.\n", sep = "")
cat(sprintf("\n%d/%d checks passed\n", sum(ok), length(ok)))
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
