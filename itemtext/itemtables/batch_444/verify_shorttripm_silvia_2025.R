# verify_shorttripm_silvia_2025.R
#
# mapping_basis = data_labels: item codes ARE the Qualtrics export tags in the
# study's own QSF (ChoiceDataExportTags), so the item<->text tie needs no inference.
# What DID carry inference is the option axis for the four *r items: the QSF recodes
# True=4 .. False=1, but the deposited data (and so the live table) store those
# four items ALREADY REVERSE-SCORED, so the shipped anchors for them run
# 1=True .. 4=False. This script re-checks that claim, plus the item mapping,
# against the paper's Table 1 (Silvia & Burnett, Short TriPM preprint,
# 10.31234/osf.io/uy9gb_v1), whose M/SD are reported on the reverse-scored items.

suppressMessages(library(irw))
TABLE <- "shorttripm_silvia_2025"

# Table 1: item -> c(M, SD, n)
PUB <- rbind(
  tripm_bold_2   = c(2.66, 1.01, 1148), tripm_bold_5   = c(2.61, 0.89, 1144),
  tripm_bold_8   = c(2.85, 0.88, 1150), tripm_bold_11r = c(2.48, 1.03, 1148),
  tripm_bold_14r = c(2.78, 0.89, 1149), tripm_dis_3    = c(1.56, 0.82, 1145),
  tripm_dis_6    = c(1.70, 0.98, 1147), tripm_dis_9    = c(1.51, 0.81, 1150),
  tripm_dis_12   = c(1.82, 0.88, 1146), tripm_dis_15   = c(1.90, 0.99, 1147),
  tripm_mean_1r  = c(1.56, 0.76, 1144), tripm_mean_4   = c(1.51, 0.77, 1145),
  tripm_mean_7   = c(1.39, 0.71, 1145), tripm_mean_10  = c(1.46, 0.75, 1146),
  tripm_mean_13r = c(1.58, 0.75, 1148))

d <- irw::irw_fetch(TABLE)
d <- d[!is.na(d$resp), ]
m <- tapply(d$resp, d$item, mean)[rownames(PUB)]
s <- tapply(d$resp, d$item, sd)[rownames(PUB)]
n <- tapply(d$resp, d$item, length)[rownames(PUB)]

cat(sprintf("%-15s %6s %6s | %6s %6s | %5s %5s\n", "item", "pubM", "obsM", "pubSD", "obsSD", "pubN", "obsN"))
for (i in rownames(PUB))
  cat(sprintf("%-15s %6.2f %6.2f | %6.2f %6.2f | %5d %5d\n", i, PUB[i, 1], m[i], PUB[i, 2], s[i], PUB[i, 3], n[i]))
ok1 <- all(abs(m - PUB[, 1]) <= 0.006) && all(abs(s - PUB[, 2]) <= 0.006) && all(n == PUB[, 3])
cat(sprintf("\nmax |dM| = %.4f, max |dSD| = %.4f, n all equal: %s\n",
            max(abs(m - PUB[, 1])), max(abs(s - PUB[, 2])), all(n == PUB[, 3])))

# Direction of the r items: if stored RAW, "I sympathize with others' problems"
# (mean_1r) would sit near the ceiling (~3.44) and correlate negatively with the
# forward meanness items. Stored reversed, it sits at the floor and correlates +.
w <- reshape(as.data.frame(d)[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
pairs <- list(c("tripm_mean_1r", "tripm_mean_4"), c("tripm_mean_13r", "tripm_mean_4"),
              c("tripm_bold_11r", "tripm_bold_2"), c("tripm_bold_14r", "tripm_bold_5"))
rs <- sapply(pairs, function(p) cor(w[[p[1]]], w[[p[2]]], use = "pair"))
for (k in seq_along(pairs)) cat(sprintf("r(%s, %s) = %+.2f\n", pairs[[k]][1], pairs[[k]][2], rs[k]))
ok2 <- all(rs > 0.2)
cat("r items correlate positively with same-subscale forward items => stored already reversed:", ok2, "\n")
cat("Note: the item<->text tie itself rests on the QSF export tags (data_labels); Table 1's\n",
    "M/SD/n per numbered item reproduce exactly, which also separates the near-tied\n",
    "dis_3/mean_1r (SD .82 vs .76, n 1145 vs 1144) and dis_9/mean_4 (SD .81 vs .77).\n", sep = "")

cat(if (ok1 && ok2) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
