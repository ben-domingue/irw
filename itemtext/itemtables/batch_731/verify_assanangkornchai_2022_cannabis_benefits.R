# verify_assanangkornchai_2022_cannabis_benefits.R -- Step 5b, batch_731.
#
# Claim: IRW item V5nn is questionnaire Part 4 item nn (V501 = item 1 ... V520 =
# item 20), so V503 = "Improve spasticity" (item 3) and V516 = "Treat spasticity
# from multiple sclerosis" (item 16) -- even though the deposit's Code sheet labels
# V503 "Treatment of spasticity in multiple sclerosis".
#
# Route: the paper's Table 3 (PeerJ 10:e12809) prints RDS-weighted % "yes" for 14
# benefit items. Those are exactly reproduced by an RDS-II (Volz-Heckathorn)
# estimate, weight = 1/network size, pooled over all four regions. The live
# table carries network size as cov_network_size, so the estimate is recomputed
# here from IRW data alone. Each of the 14 Table 3 labels must land on exactly one
# item and on the item its questionnaire number predicts.
#
# Does NOT establish: the six items Table 3 omits (V503 aside from being ruled out
# as "spasticity in MS", V506, V510, V511, V514, V518) are pinned only by the
# numbering convention the other 14 obey, plus semantic correlation partners
# printed below as corroboration (not a pass criterion).

suppressMessages(library(irw))
TABLE <- "assanangkornchai_2022_cannabis_benefits"

# Table 3 label -> published %, and the item its questionnaire number predicts
PUB <- data.frame(
  label = c("Treatment of chronic pain in adults", "An antiemesis for patients who receive chemotherapy",
            "Treatment of intractable epilepsy in children", "Treatment of spasticity in multiple sclerosis",
            "Treatment of Parkinson's disease", "Treatment of Alzheimer's disease",
            "Treatment of generalized anxiety disorder", "Treatment of cancers", "Improvement of insomnia",
            "Increased appetite in HIV/AIDS patients", "Improved PTSD symptoms",
            "Treatment of substance dependence", "Treatment of brain tumour",
            "Decreased severity of chronic cough"),
  pct = c(83.6, 65.9, 73.6, 73.8, 79.1, 73.4, 82.6, 89.9, 99.1, 77.0, 78.6, 51.9, 50.1, 62.6),
  predicted = c("V501", "V502", "V515", "V516", "V512", "V517", "V519", "V508", "V504",
                "V505", "V507", "V513", "V509", "V520"),
  stringsAsFactors = FALSE)

d <- as.data.frame(suppressMessages(irw::irw_fetch(TABLE)))
stopifnot("cov_network_size" %in% names(d))
d <- d[!is.na(d$cov_network_size) & d$cov_network_size > 0, ]
w <- 1 / d$cov_network_size
est <- round(100 * tapply(d$resp * w, d$item, sum) / tapply(w, d$item, sum), 1)
cat("RDS-II % yes per item (1/network size, pooled):\n"); print(format(est, nsmall = 1), quote = FALSE)

ok <- TRUE
cat(sprintf("\n%-52s %6s %-6s %-22s\n", "Table 3 label", "pub", "pred", "items matching to 0.1"))
for (i in seq_len(nrow(PUB))) {
  hits <- names(est)[abs(est - PUB$pct[i]) < 0.05]
  good <- identical(hits, PUB$predicted[i])
  ok <- ok && good
  cat(sprintf("%-52s %6.1f %-6s %-22s %s\n", PUB$label[i], PUB$pct[i], PUB$predicted[i],
              paste(hits, collapse = ","), if (good) "ok" else "MISMATCH"))
}
cat(sprintf("\nV503 = %.1f vs 'spasticity in MS' 73.8 -> codebook label for V503 is %s\n",
            est["V503"], if (abs(est["V503"] - 73.8) > 0.05) "NOT supported (it is V516's)" else "supported"))

# Corroboration only for the six unpublished items: top correlation partner
wide <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(wide) <- sub("^resp\\.", "", names(wide))
cm <- cor(wide[, -1], use = "pairwise.complete.obs")
cat("\nTop correlation partners for items absent from Table 3 (corroboration, not scored):\n")
for (it in c("V503", "V506", "V510", "V511", "V514", "V518")) {
  s <- sort(cm[it, setdiff(colnames(cm), it)], decreasing = TRUE)[1:2]
  cat(sprintf("  %s: %s\n", it, paste(sprintf("%s %.2f", names(s), s), collapse = ", ")))
}
cat("  expected among top 2: V503~V516 (spasticity), V506~V507/V519 (anxiety/PTSD/GAD), V510~V509 (cancer),\n",
    "  V511~V515 (epilepsy), V514~V502 (chemo nausea), V518~V516 (multiple sclerosis)\n", sep = "")

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
