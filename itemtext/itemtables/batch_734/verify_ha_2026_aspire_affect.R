# verify_ha_2026_aspire_affect.R -- batch_734
# Claim: item codes are the deposit's own column headers (happy_A/B, energ_A/B, low_A/B,
# irr_A/B, distr_A/B; data/ha_2026_aspire.py strips only the _A/_B partner suffix), and
# are self-describing abbreviations of the adjectives the paper names (Ha, Quiroz &
# McNeish 2026, CHB 181:108981, PMC13267910, Measures: "happy, energetic, low,
# irritable, and distressed"). insec and attr ship with blank item_text.
# Falsifiable check (route 6, keying polarity): the two positive-affect codes
# (happy, energ) must correlate positively with each other and negatively with every
# negative-affect code (low, irr, distr), and the negative codes positively among
# themselves. A swap of any positive-text item with any negative-text item breaks it.
# Does NOT establish order WITHIN a polarity class (happy vs energ; low vs irr vs distr)
# -- that rests on the codes naming their own content.
suppressMessages(library(irw))
TABLE <- "ha_2026_aspire_affect"
d <- as.data.frame(irw::irw_fetch(TABLE))[, c("id", "wave", "item", "resp")]
w <- reshape(d, idvar = c("id", "wave"), timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
pos <- c("happy", "energ"); neg <- c("low", "irr", "distr")
r <- cor(w[, c(pos, neg, "attr", "insec")], use = "pairwise")
print(round(r, 2))
pp <- r[pos, pos][upper.tri(r[pos, pos])]
nn <- r[neg, neg][upper.tri(r[neg, neg])]
pn <- r[pos, neg]
cat(sprintf("\npos-pos r: %s\nneg-neg r: %s\npos-neg r range: %.2f..%.2f\n",
            paste(round(pp, 2), collapse = ","), paste(round(nn, 2), collapse = ","),
            min(pn), max(pn)))
m <- tapply(d$resp, d$item, mean)
cat("item means:", paste(names(m), round(m, 2), sep = "=", collapse = " "), "\n")
cat("Not established: order within polarity class; the referents of insec/attr (no text shipped).\n")
ok <- all(pp > 0) && all(nn > 0) && all(pn < 0)
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
