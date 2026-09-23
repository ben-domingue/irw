# Verifies the item_text <-> item mapping for di_riso_2025_contact_behavior.
# Copied from references/verify_template.R.
#
# Claim under test: Touching / Contact_with_professionals / Contact_with_unknown
# carry, respectively, the three "Attitudes toward physical touch" statements of
# Di Riso et al. (2025), PLOS ONE 20(3):e0314607, Table 2 (image t002), which
# prints M and SD per statement. If any two item_texts were swapped, the
# published (M, SD) pairs would land on the wrong code.
#
# Second, independent check: keying polarity. Two statements are aversive
# (intrusive; very unpleasant with unknown people) and one is approving
# (contact with professionals is pleasant), so on raw data the aversive pair
# must correlate positively and each must correlate negatively with the
# approving one.
#
# The table is small (3,434 rows), so the full fetch is a deliberate, negligible export.

suppressMessages(library(irw))

TABLE <- "di_riso_2025_contact_behavior"

PUB <- data.frame(
    item = c("Touching", "Contact_with_professionals", "Contact_with_unknown"),
    text = c("I often find touching or being touched an intrusive gesture",
             "I find that physical contact with professionals is pleasant",
             "I find it very unpleasant to have physical contact with unknown people"),
    mean = c(3.27, 3.77, 4.00),
    sd   = c(1.18, 1.02, 1.17),
    stringsAsFactors = FALSE)
TOL <- 0.01

d <- as.data.frame(irw::irw_fetch(TABLE))
d$resp <- as.numeric(d$resp)
obs_m  <- tapply(d$resp, d$item, mean)
obs_sd <- tapply(d$resp, d$item, sd)

cat(sprintf("%-28s %7s %7s %7s %7s\n", "item", "pub_M", "obs_M", "pub_SD", "obs_SD"))
for (i in seq_len(nrow(PUB))) {
    it <- PUB$item[i]
    cat(sprintf("%-28s %7.2f %7.3f %7.2f %7.3f\n", it, PUB$mean[i], obs_m[[it]], PUB$sd[i], obs_sd[[it]]))
}
dm  <- max(abs(obs_m[PUB$item]  - PUB$mean))
dsd <- max(abs(obs_sd[PUB$item] - PUB$sd))
cat(sprintf("\nlargest |dM| = %.4f, largest |dSD| = %.4f (tol %.2f)\n", dm, dsd, TOL))

# Every item's nearest published row must be its own (published means are 0.50
# and 0.23 apart, so this separates all three items).
nearest <- sapply(PUB$item, function(it)
    PUB$item[which.min(abs(PUB$mean - obs_m[[it]]) + abs(PUB$sd - obs_sd[[it]]))])
uniq_ok <- all(nearest == PUB$item)
cat("nearest published row for each item is its own row:", uniq_ok, "\n")

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
r <- cor(w[, PUB$item], use = "pairwise.complete.obs")
cat(sprintf("\nr(Touching, Contact_with_unknown)       = %+.3f (expect > 0)\n", r["Touching", "Contact_with_unknown"]))
cat(sprintf("r(Touching, Contact_with_professionals) = %+.3f (expect < 0)\n", r["Touching", "Contact_with_professionals"]))
cat(sprintf("r(Contact_with_unknown, _professionals) = %+.3f (expect < 0)\n", r["Contact_with_unknown", "Contact_with_professionals"]))
pol_ok <- r["Touching", "Contact_with_unknown"] > 0 &&
          r["Touching", "Contact_with_professionals"] < 0 &&
          r["Contact_with_unknown", "Contact_with_professionals"] < 0

cat(if (dm <= TOL && dsd <= TOL && uniq_ok && pol_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
