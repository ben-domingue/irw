# verify_uti_newlands_2023_wpai.R -- Step 5b check for batch_259.
#
# Claim: wpai_1..wpai_6 are WPAI:SHP V2.0 questions 1..6 (codes come from the OSF raw file's
# wpai{wave}_{k} columns via a number-preserving regex rename in data/uti_newlands_2023.py; the
# deposit codebook and paper print no WPAI wording), with wpai_1 0=NO/1=YES (employed) and
# wpai_5/wpai_6 0 = "no effect" .. 10 = "completely prevented".
#
# Published comparators (Newlands et al. 2023 Qual Life Res, Online Resource 11, baseline N=240):
#   WPAI-SHP % Work impairment  M 44.5  SD 33.3  range 0-100
#   WPAI-SHP % Activity impairment M 45.7 SD 29.6 range 0-100
# Standard WPAI:SHP scoring (reillyassociates.net/WPAI_Scoring.html):
#   activity impairment = Q6*10;  overall work impairment = [Q2/(Q2+Q4) + (1-Q2/(Q2+Q4))*Q5/10]*100
#
# Checks (baseline wave):
#  A. Skip structure: wpai_1==0 -> wpai_2..5 absent, wpai_1==1 -> all present; wpai_6 present for all.
#     Pins wpai_1 as the employment gate with 0 = NO (form: "If NO ... skip to question 6"), wpai_6 as
#     the only question asked of everyone, and {2,3,4,5} as the employed-only block.
#  B. wpai_6*10 reproduces % Activity impairment (M 45.7, SD 29.6); reversed anchors would give M 54.3.
#  C. wpai_5 is the only 0-10 rating in the employed block; wpai_4 (hours actually worked) has by far
#     the largest mean of the hours items.
#  D. wpai_2 vs wpai_3: OWI computed with wpai_2 as "hours missed because of PROBLEM" reproduces the
#     published SD 33.3; the swap (wpai_3 in that role) gives ~31.0. And wpai_2 correlates positively
#     with wpai_5 (presenteeism due to the same PROBLEM) while wpai_3 (other reasons) does not.
# NOT established: the ~0.5-point residual on the published OWI mean (44.99 here vs 44.5); the paper
# gives n=240 for every row of Online Resource 11 although only 156 were employed, so its exact
# handling of non-employed / 0-hour cases is unstated.
suppressMessages(library(irw))
d <- as.data.frame(irw::irw_fetch("uti_newlands_2023_wpai"))
d <- d[d$wave == 1, ]
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("resp.", "", names(w))
ok <- TRUE

emp <- w$wpai_1
pres <- sapply(paste0("wpai_", 2:5), function(k) !is.na(w[[k]]))
cat(sprintf("A. n=%d; wpai_1 levels: %s; employed(1)=%d all of 2-5 present: %s; not employed(0)=%d none of 2-5 present: %s; wpai_6 present for %d/%d\n",
    nrow(w), paste(sort(unique(emp)), collapse = "/"), sum(emp == 1), all(pres[emp == 1, ]),
    sum(emp == 0), !any(pres[emp == 0, ]), sum(!is.na(w$wpai_6)), nrow(w)))
ok <- ok && all(pres[emp == 1, ]) && !any(pres[emp == 0, ]) && all(!is.na(w$wpai_6))

act <- w$wpai_6 * 10
cat(sprintf("B. activity impairment = wpai_6*10: n=%d M=%.2f SD=%.2f range %g-%g (published 240, 45.7, 29.6, 0-100); reversed anchors M=%.2f\n",
    sum(!is.na(act)), mean(act), sd(act), min(act), max(act), 100 - mean(act)))
ok <- ok && abs(mean(act) - 45.7) < 0.05 && abs(sd(act) - 29.6) < 0.06

e <- w[w$wpai_1 == 1, ]
mx <- sapply(paste0("wpai_", 2:5), function(k) max(e[[k]]))
mu <- sapply(paste0("wpai_", 2:5), function(k) mean(e[[k]]))
cat("C. employed-block max:", paste(sprintf("%s=%g", names(mx), mx), collapse = "  "),
    "\n   means:", paste(sprintf("%s=%.2f", names(mu), mu), collapse = "  "), "\n")
ok <- ok && all(sort(unique(e$wpai_5)) %in% 0:10) && max(e$wpai_2, e$wpai_3, e$wpai_4) > 10 &&
      names(which.max(mu[1:3])) == "wpai_4"

owi <- function(miss) { den <- e[[miss]] + e$wpai_4; ab <- e[[miss]] / den
  o <- (ab + (1 - ab) * e$wpai_5 / 10) * 100; o[is.finite(o)] }
o2 <- owi("wpai_2"); o3 <- owi("wpai_3")
cat(sprintf("D. OWI with wpai_2 as PROBLEM hours: n=%d M=%.2f SD=%.2f | swapped (wpai_3): M=%.2f SD=%.2f | published M 44.5 SD 33.3\n",
    length(o2), mean(o2), sd(o2), mean(o3), sd(o3)))
c2 <- cor(e$wpai_2, e$wpai_5); c3 <- cor(e$wpai_3, e$wpai_5)
cat(sprintf("   cor(wpai_2, wpai_5)=%.3f  cor(wpai_3, wpai_5)=%.3f  cor(wpai_5, wpai_6)=%.3f\n", c2, c3, cor(e$wpai_5, e$wpai_6)))
ok <- ok && abs(sd(o2) - 33.3) < 0.1 && abs(sd(o3) - 33.3) > 1 && abs(mean(o2) - 44.5) < 1 && c2 > 0.3 && c3 < 0.1
cat("Does NOT establish: the 0.5-point residual on the published OWI mean (paper's handling of 0-hour cases unstated).\n")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
