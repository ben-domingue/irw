# verify_zamzuri_2021_rpap_risk_perception.R
#
# Claims being re-run:
#  (a) item axis: live item D<n> is the item Zamzuri et al. (2021) PLOS ONE
#      16(8):e0256636 Table 2 prints against code D<n> (rows 1-12, Risk Perception).
#  (b) resp axis: the live table stores D2, D3, D7, D8, D9, D10, D11, D12
#      REVERSE-SCORED (live = 9 - administered), D1, D4, D5, D6 as administered;
#      so the shipped anchors are 1=Strongly Agree / 8=Strongly Disagree for the
#      reversed eight and 1=Strongly Disagree / 8=Strongly Agree for the rest.
#      The reversed set is exactly the set the authors' own S1 Data Sheet3 header
#      marks with an _r suffix (D2_r, D3_r, D7_r .. D12_r).
#
# Route: per-item descriptive statistics (Step 5b route 1) + keying direction
# (route 6). Table 2 prints each item's raw Mean (SD) for the same N = 253 sample
# (S1 Data Sheet1; data/zamzuri_2021_rpap.py melts D1..D12 by name, no recoding).
# Each live item is compared against all 24 candidates (12 published rows x
# {as printed, reflected 9 - M}); it must land nearest its own code, in the
# direction the _r header predicts. SD is invariant to reflection, so M carries
# the direction and (M, SD) jointly carry identity.
#
# NOT established exactly: two items miss 2-dp rounding precision. D2 lands 0.015
# from its reflected row (live 6.3874 -> administered 2.613 vs printed 2.60) and D12
# 0.021 (live 4.4229 -> 4.577 vs printed 4.56; SD 2.2815 vs 2.27). Both remain far
# nearer their own row than any other candidate (next: 0.52 and 0.14). The other 10
# match within 0.006.

suppressMessages(library(irw))

TABLE <- "zamzuri_2021_rpap_risk_perception"
ITEMS <- paste0("D", 1:12)
REV   <- c("D2", "D3", "D7", "D8", "D9", "D10", "D11", "D12")   # Sheet3 *_r headers

# Table 2, Mean (SD), rows 1-12 (codes D1-D12), transcribed from the article XML.
PUB_M  <- c(4.77, 2.60, 2.18, 7.87, 7.26, 5.87, 6.63, 7.34, 6.69, 2.25, 3.30, 4.56)
PUB_SD <- c(2.05, 1.99, 1.69, 0.58, 1.45, 2.08, 1.51, 1.29, 1.50, 1.56, 1.91, 2.27)
names(PUB_M) <- names(PUB_SD) <- ITEMS

d <- as.data.frame(irw::irw_fetch(TABLE))
obs_m  <- tapply(d$resp, d$item, mean)[ITEMS]
obs_sd <- tapply(d$resp, d$item, sd)[ITEMS]

cand <- rbind(
  data.frame(code = ITEMS, dir = "as_printed", M = PUB_M,     SD = PUB_SD),
  data.frame(code = ITEMS, dir = "reflected",  M = 9 - PUB_M, SD = PUB_SD))

cat(sprintf("%-4s %8s %8s | %-4s %-10s %6s %6s %7s | %s\n",
            "item", "obs_M", "obs_SD", "best", "dir", "pub_M*", "pub_SD", "dist", "2nd-best dist"))
ok <- logical(0); resid <- numeric(0)
for (i in ITEMS) {
  dist <- sqrt((obs_m[i] - cand$M)^2 + (obs_sd[i] - cand$SD)^2)
  o <- order(dist); b <- cand[o[1], ]
  want_dir <- if (i %in% REV) "reflected" else "as_printed"
  ok[i] <- b$code == i && b$dir == want_dir
  resid[i] <- dist[o[1]]
  cat(sprintf("%-4s %8.4f %8.4f | %-4s %-10s %6.2f %6.2f %7.4f | %.4f (%s %s)\n",
              i, obs_m[i], obs_sd[i], b$code, b$dir, b$M, b$SD, dist[o[1]],
              dist[o[2]], cand$code[o[2]], cand$dir[o[2]]))
}
cat(sprintf("\n%d/12 live items land nearest their own Table 2 code in the predicted direction\n", sum(ok)))
cat(sprintf("items within 2-dp rounding (dist <= 0.008): %d/12; max residual %.4f (%s)\n",
            sum(resid <= 0.008), max(resid), names(which.max(resid))))

# Semantic sanity on direction: D8 ('With at least one person who is knowledgeable
# ... can help prevent the disease') cannot plausibly sit at 1.66/8 when read raw
# in a sample whose attitude items average 6.1-7.8; reflected it is 7.34.
cat(sprintf("D8 live mean %.2f -> administered 9 - x = %.2f (Table 2: 7.34)\n", obs_m["D8"], 9 - obs_m["D8"]))

cat(if (all(ok) && max(resid) <= 0.025) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
