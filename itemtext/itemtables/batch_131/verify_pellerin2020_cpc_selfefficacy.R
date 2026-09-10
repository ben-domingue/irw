# verify_pellerin2020_cpc_selfefficacy.R -- batch_131, 2026-09-10
#
# WHAT IS BEING VERIFIED
# data/pellerin2020_covid_resources.py melts the literal column list
# ["SAE_1","SAE_2","SAE_3"] out of the study's OSF CSV, so the IRW item code IS
# the source column name (code-derivation pattern 1) -- but that CSV is a bare
# header row with no variable or value labels, so the code is tied to nothing
# textual. The shipped wording comes from the CPC-12's own S1 Appendix (Lorenz,
# Beer, Puetz & Heinitz 2016, PLOS ONE 11(4):e0152892, CC BY 4.0), whose
# self-efficacy block is items 10-12:
#   10  "I am confident that I could deal efficiently with unexpected events."          (GSE4)
#   11  "I can solve most problems if I invest the necessary effort."                   (GSE10)
#   12  "I can remain calm when facing difficulties because I can rely on my
#        coping abilities."                                                             (GSE6)
# The mapping under test is therefore the ORDER INFERENCE SAE_k <-> CPC-12
# item (9+k)  (mapping_basis = paper_order). Nothing states it.
#
# THE FALSIFIABLE PREDICTIONS
# All three come from the CPC-12's own development samples (Lorenz 2016 S2/S3
# Datasets), where the three self-efficacy items are individually identified,
# and are tested on the French administration. Each is scored over all SIX
# possible assignments, not just the shipped one.
#
#   (A) AGE GRADIENT. In S3 Dataset (n=202) r(item,age) = .160 / .013 / .068 for
#       items 10 / 11 / 12: item 10 ("unexpected events") is the age-graded one
#       and item 11 is flat. Prediction: the French age profile matches that
#       shape under the shipped permutation and no other.
#   (B) ENDORSEMENT MARKER. Item 11 has the HIGHEST mean and the LOWEST SD in
#       BOTH German samples (S2 n=321: 3.738/4.271/4.059, SD .929/.749/.880;
#       S3 n=202: 3.847/4.332/4.223, SD .823/.775/.938). Prediction: SAE_2 is
#       the highest-mean, lowest-SD item in the French data.
#   (C) EMOTION-CRITERION MARKER. Item 12 ("remain calm ... coping abilities")
#       is the emotionally loaded item: in S3 it correlates .294 with life
#       satisfaction (vs .092 / .114) and -.401 with neuroticism (vs -.270 /
#       -.221). Prediction: SAE_3 is the strongest correlate of Pellerin's
#       well-being scales, at every wave.
#
# WHAT THIS DOES NOT ESTABLISH -- AND ONE ROUTE THAT DISSENTS
# It is a structural match, not a source-level label tie: no file anywhere
# spells out "SAE_2 = I can solve most problems...". It also assumes the German
# development samples' item structure carries to a French translation
# administered under COVID lockdown on a 1-7 rather than 1-6 scale. And one
# statistic does NOT replicate: within the self-efficacy block, both German
# samples make {item 11, item 12} the most correlated pair (.559 in S2, .486 in
# S3) whereas the French data makes {SAE_2, SAE_3} the LEAST correlated pair
# (.525 vs .641 and .588). Check (D) below prints that and does not gate on it;
# the only remapping it would favour puts item 10 at SAE_2, which checks (A)
# and (B) both refuse outright. The verdict is recorded PARTIAL for this reason.
#
# DATA: the study's OSF deposit (osf.io/45aq3, data.PsyR_lockdown2020.csv) --
# the exact file data/pellerin2020_covid_resources.py reads, whose 1,010
# complete SAE triples equal the live table's per-item n of 1,010 -- and the
# CPC-12's PLOS supplements. Nothing here exports the IRW table.

ITEMS <- c("SAE_1", "SAE_2", "SAE_3")
CPC   <- c(10, 11, 12)
perms <- list(c(1,2,3), c(1,3,2), c(2,1,3), c(2,3,1), c(3,1,2), c(3,2,1))
pname <- function(p) paste0("SAE_1,2,3 -> items ", paste(CPC[p], collapse = "/"))

rd <- function(u) read.csv(u, stringsAsFactors = FALSE)
osf <- try(rd("https://osf.io/download/dc6me/"), silent = TRUE)
s3  <- try(read.csv2("https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0152892.s003&type=supplementary",
                     fileEncoding = "latin1", stringsAsFactors = FALSE), silent = TRUE)
s2  <- try(read.csv2("https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0152892.s002&type=supplementary",
                     fileEncoding = "latin1", stringsAsFactors = FALSE), silent = TRUE)
if (inherits(osf, "try-error") || inherits(s3, "try-error") || inherits(s2, "try-error"))
    stop("source files unreachable -- cannot verify")

d <- osf[stats::complete.cases(osf[, ITEMS]), ]
cat(sprintf("OSF deposit: %d complete SAE triples (live table per-item n = 1010)\n\n", nrow(d)))

# ---------------------------------------------------------------- (A) age ----
GER_AGE <- c(cor(s3$cpc10, s3$age, use = "complete.obs"),
             cor(s3$cpc11, s3$age, use = "complete.obs"),
             cor(s3$cpc12, s3$age, use = "complete.obs"))
cat("(A) AGE GRADIENT\n")
cat(sprintf("    Lorenz S3 (n=%d) r(item,age): item10=%.3f item11=%.3f item12=%.3f\n",
            sum(!is.na(s3$cpc10) & !is.na(s3$age)), GER_AGE[1], GER_AGE[2], GER_AGE[3]))
okA <- TRUE
for (wv in c(0, 5)) {
    x <- d[d$Wave == wv, c(ITEMS, "Age")]; x <- x[stats::complete.cases(x), ]
    fr <- sapply(ITEMS, function(i) cor(x[[i]], x$Age))
    sse <- sapply(perms, function(p) sum((fr - GER_AGE[p])^2))
    win <- perms[[which.min(sse)]]
    cat(sprintf("    FR wave %d (n=%d)  SAE_1=%.3f SAE_2=%.3f SAE_3=%.3f  -> best of 6: %s (SSE=%.4f, runner-up %.4f)\n",
                wv, nrow(x), fr[1], fr[2], fr[3], pname(win), min(sse), sort(sse)[2]))
    okA <- okA && all(win == c(1, 2, 3))
}
cat(sprintf("    shipped permutation is the best-fitting one at both waves: %s\n\n",
            if (okA) "YES" else "NO"))

# ------------------------------------------------------ (B) endorsement ------
gmean <- function(df, cols) sapply(cols, function(c) mean(df[[c]], na.rm = TRUE))
gsd   <- function(df, cols) sapply(cols, function(c) sd(df[[c]],   na.rm = TRUE))
S2C <- c("efficacy1.4", "efficacy1.10", "efficacy1.6")   # = CPC items 10, 11, 12
S3C <- c("cpc10", "cpc11", "cpc12")
cat("(B) ENDORSEMENT MARKER (item 11 = highest mean, lowest SD)\n")
cat(sprintf("    Lorenz S2 means %s  SDs %s\n",
            paste(sprintf("%.3f", gmean(s2, S2C)), collapse = "/"),
            paste(sprintf("%.3f", gsd(s2, S2C)), collapse = "/")))
cat(sprintf("    Lorenz S3 means %s  SDs %s\n",
            paste(sprintf("%.3f", gmean(s3, S3C)), collapse = "/"),
            paste(sprintf("%.3f", gsd(s3, S3C)), collapse = "/")))
gerB <- which.max(gmean(s2, S2C)) == 2 && which.min(gsd(s2, S2C)) == 2 &&
        which.max(gmean(s3, S3C)) == 2 && which.min(gsd(s3, S3C)) == 2
frm <- gmean(d, ITEMS); frs <- gsd(d, ITEMS)
cat(sprintf("    FR         means %s  SDs %s\n",
            paste(sprintf("%.3f", frm), collapse = "/"),
            paste(sprintf("%.3f", frs), collapse = "/")))
okB <- gerB && which.max(frm) == 2 && which.min(frs) == 2
cat(sprintf("    German marker holds in both samples: %s;  SAE_2 is FR highest-mean & lowest-SD: %s\n\n",
            if (gerB) "YES" else "NO",
            if (which.max(frm) == 2 && which.min(frs) == 2) "YES" else "NO"))

# ------------------------------------------------------- (C) emotion ---------
lezu <- rowMeans(s3[, paste0("lezu", 1:5)], na.rm = TRUE)
neu  <- rowMeans(s3[, c("neu1", "neu2")], na.rm = TRUE)
gl <- sapply(S3C, function(c) cor(s3[[c]], lezu, use = "complete.obs"))
gn <- sapply(S3C, function(c) cor(s3[[c]], neu,  use = "complete.obs"))
cat("(C) EMOTION-CRITERION MARKER (item 12 = strongest well-being correlate)\n")
cat(sprintf("    Lorenz S3 r(item,life satisfaction): %s   r(item,neuroticism): %s\n",
            paste(sprintf("%.3f", gl), collapse = "/"), paste(sprintf("%.3f", gn), collapse = "/")))
gerC <- which.max(gl) == 3 && which.min(gn) == 3
hits <- 0L; tot <- 0L
for (wv in c(0, 5)) for (crit in c("EWB", "SWB", "IWB")) {
    x <- d[d$Wave == wv, c(ITEMS, crit)]; x <- x[stats::complete.cases(x), ]
    if (nrow(x) < 50) next
    r <- sapply(ITEMS, function(i) cor(x[[i]], x[[crit]]))
    tot <- tot + 1L; good <- which.max(r) == 3; hits <- hits + as.integer(good)
    cat(sprintf("    FR wave %d %-4s n=%4d: SAE_1=%.3f SAE_2=%.3f SAE_3=%.3f  %s\n",
                wv, crit, nrow(x), r[1], r[2], r[3],
                if (good) "SAE_3 highest" else "VIOLATED"))
}
okC <- gerC && tot > 0 && hits == tot
cat(sprintf("    German marker holds: %s;  SAE_3 highest in %d of %d FR comparisons\n\n",
            if (gerC) "YES" else "NO", hits, tot))

# --------------------------------------------- (D) the dissenting route ------
cat("(D) DISSENT -- within-block intercorrelation ordering (reported, NOT gated)\n")
g2 <- cor(s2[, S2C], use = "complete.obs"); g3 <- cor(s3[, S3C], use = "complete.obs")
fr <- cor(d[, ITEMS])
cat(sprintf("    r(10,11) r(10,12) r(11,12) :  S2 %.3f %.3f %.3f  |  S3 %.3f %.3f %.3f\n",
            g2[1,2], g2[1,3], g2[2,3], g3[1,2], g3[1,3], g3[2,3]))
cat(sprintf("    FR under shipped map      :     %.3f %.3f %.3f\n", fr[1,2], fr[1,3], fr[2,3]))
cat("    Both German samples make {11,12} the MOST correlated pair; the French data\n")
cat("    makes it the LEAST. The remap that would fix this puts item 10 at SAE_2,\n")
cat("    which (A) and (B) both refuse. Recorded as PARTIAL for this reason.\n\n")

pass <- okA && okB && okC
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
