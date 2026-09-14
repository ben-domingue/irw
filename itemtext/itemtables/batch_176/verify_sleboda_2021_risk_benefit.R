# verify_sleboda_2021_risk_benefit.R
#
# mapping_basis is data_labels (item codes ARE the S1 .sav column names, melted
# verbatim by data/sleboda_2021_risk_benefit.py), so the item_text<->item axis
# needs no route. This script exists for the two things that DID take inference:
#
#  (A) section_prompt <-> code prefix. The processing script's header calls the
#      prefixes "genetic testing / stem-cell research / pesticides /
#      energy-nuclear / vaccination"; the .sav labels say "GT for Plant breeding",
#      "StemCell", "Pesticides", "Enumbers", "Vaccination". The paper's S2 Table
#      (S1 File) prints M (SD) of benefit/harm for humans/environment per
#      technology -- 20 falsifiable per-item means + SDs.
#
#  (B) option_text<->resp for the five *_new items. The S1 File's English says
#      "(1 = absolutely old; 11 = absolutely new)" for every technology, but the
#      .sav VALUE labels put "Helt ny" (completely new) at 1 and "Mycket bekant"
#      (very familiar) at 11 for GT/SC/PE, and the reverse for EN/VA. The shipped
#      anchors follow the value labels. Test: under the shipped anchors both
#      gene-technology applications must read as NEWER than pesticides, E-number
#      food additives and vaccination; under the S1 File's uniform direction
#      pesticides would be the newest of the five.
#
# Uses server-side aggregate queries (no table export). Falls back to irw_fetch.

suppressMessages(library(irw))
TABLE <- "sleboda_2021_risk_benefit"

stats <- tryCatch({
  tbl <- irw:::.fetch_redivis_table(TABLE, source = irw:::.irw_resolve_source(source = "core"))
  q <- sprintf(paste("SELECT CAST(item AS STRING) AS item, COUNT(*) AS n,",
                     "AVG(CAST(resp AS FLOAT64)) AS m, STDDEV_SAMP(CAST(resp AS FLOAT64)) AS sd",
                     "FROM `%s` WHERE resp IS NOT NULL GROUP BY item"), tbl$qualified_reference)
  as.data.frame(irw:::.irw_query_tibble(q))
}, error = function(e) {
  message("aggregate query failed (", conditionMessage(e), "); falling back to irw_fetch")
  d <- irw::irw_fetch(TABLE)
  data.frame(item = sort(unique(d$item)),
             n  = as.vector(tapply(d$resp, d$item, length)[sort(unique(d$item))]),
             m  = as.vector(tapply(d$resp, d$item, mean)[sort(unique(d$item))]),
             sd = as.vector(tapply(d$resp, d$item, sd)[sort(unique(d$item))]))
})
M  <- setNames(stats$m, stats$item)
SD <- setNames(stats$sd, stats$item)

ok <- TRUE

# ---- (A) S2 Table, Sleboda & Lagerkvist 2021 S1 File, N = 3228 ------------------
pub <- read.csv(text = "
prefix,label,b4hum_m,b4hum_sd,h4hum_m,h4hum_sd,b4env_m,b4env_sd,h4env_m,h4env_sd
GT,GT for plant breeding,6.58,2.43,6.08,2.41,5.54,2.51,6.29,2.43
SC,GT for stem cells,7.13,2.41,5.45,2.33,5.51,2.42,5.27,2.40
PE,Pesticides,5.98,2.38,7.08,2.33,4.58,2.61,7.35,2.43
EN,Food additives,5.51,2.53,6.48,2.42,4.64,2.59,6.22,2.41
VA,Vaccination,7.71,2.53,5.22,2.53,5.71,2.54,5.07,2.49", strip.white = TRUE)

cat("(A) S2 Table M (SD) vs live, per technology x item\n")
cat(sprintf("%-18s %-6s %6s %6s %6s %6s\n", "technology", "dim", "pubM", "liveM", "pubSD", "liveSD"))
n_m <- 0; n_sd <- 0; n_tot <- 0
for (i in seq_len(nrow(pub))) for (dim in c("b4hum", "h4hum", "b4env", "h4env")) {
  it <- paste0(pub$prefix[i], "_", dim)
  pm <- pub[[paste0(dim, "_m")]][i]; ps <- pub[[paste0(dim, "_sd")]][i]
  cat(sprintf("%-18s %-6s %6.2f %6.2f %6.2f %6.2f%s\n", pub$label[i], dim, pm, M[[it]], ps, SD[[it]],
              if (abs(M[[it]] - pm) > 0.015) "   <-- mean differs" else ""))
  n_tot <- n_tot + 1
  n_m  <- n_m  + (abs(M[[it]] - pm) <= 0.015)
  n_sd <- n_sd + (abs(SD[[it]] - ps) <= 0.015)
}
cat(sprintf("means within 0.015: %d/%d; SDs within 0.015: %d/%d\n", n_m, n_tot, n_sd, n_tot))
# Known: VA b4hum published 7.71 vs data 7.51 with the SD (2.53) matching -- a
# printing error in S2 Table (7.71 is also not reachable by any other VA item).
# Also check that no prefix permutation fits better than the identity.
perm_fit <- sapply(pub$prefix, function(p) sapply(seq_len(nrow(pub)), function(i)
  sum(abs(M[paste0(p, "_", c("b4hum","h4hum","b4env","h4env"))] -
          unlist(pub[i, c("b4hum_m","h4hum_m","b4env_m","h4env_m")])))))
rownames(perm_fit) <- pub$label
cat("\nsum |live - published| over the 4 means (rows = published technology, cols = code prefix):\n")
print(round(perm_fit, 2))
best <- colnames(perm_fit)[apply(perm_fit, 1, which.min)]
cat("best-fitting prefix per published technology:", paste(pub$label, "->", best, collapse = "; "), "\n")
if (!(n_m >= 19 && n_sd == 20 && identical(unname(best), pub$prefix))) ok <- FALSE

# ---- (B) direction of the *_new anchors ----------------------------------------
shipped_hi_is_new <- c(GT = FALSE, SC = FALSE, PE = FALSE, EN = TRUE, VA = TRUE)  # from .sav value labels
raw <- M[paste0(names(shipped_hi_is_new), "_new")]
newness_shipped <- ifelse(shipped_hi_is_new, raw, 12 - raw)   # 1..11, high = new
newness_s1file  <- raw                                        # S1 File: 11 = new everywhere
cat("\n(B) *_new item: raw live mean, and implied 'newness' (11 = absolutely new)\n")
print(round(data.frame(raw_mean = raw, newness_shipped = newness_shipped,
                       newness_if_S1File_direction = newness_s1file,
                       row.names = c("gene tech plant breeding", "gene tech stem cells",
                                     "pesticides", "E-number additives", "vaccination")), 2))
gene  <- newness_shipped[1:2]; old <- newness_shipped[3:5]
cond_shipped <- min(gene) > max(old)
cond_s1      <- min(newness_s1file[1:2]) > max(newness_s1file[3:5])
cat(sprintf("shipped anchors: min(gene tech) %.2f > max(pesticides, E-numbers, vaccination) %.2f ? %s\n",
            min(gene), max(old), cond_shipped))
cat(sprintf("S1 File uniform direction: same test ? %s (pesticides newest at %.2f)\n",
            cond_s1, newness_s1file[3]))
if (!cond_shipped) ok <- FALSE

cat("\nNot established: (B) is a plausibility ordering of five technologies, not a\n",
    "published statistic -- it shows the .sav value-label direction yields gene technology\n",
    "newer than pesticides, E-numbers and vaccination while the S1 File's uniform direction\n",
    "makes pesticides the newest; it does not show why the Swedish survey reversed the\n",
    "anchors for three technologies. (A) pins technology per prefix, not item order within\n",
    "a technology (not needed: item codes are the .sav column names).\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
