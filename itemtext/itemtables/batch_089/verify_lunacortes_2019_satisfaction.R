# Step 5b verification for lunacortes_2019_satisfaction.
#
# THE MAPPING CLAIM. The IRW item codes satis_1/2/3 are a mechanical lowercase
# rename of the S1 File XLSX headers "SATIS 1"/"SATIS 2"/"SATIS 3"
# (data/lunacortes_2019_vsn_scales.py), so code -> data column is not in doubt.
# What IS inferred is the WORDING: PLOS Table 1 prints the three Satisfaction
# items as an UNLABELLED bullet list, and the extraction assumes bullet order
# == the SATIS1/2/3 numbering that Table 2 uses for its factor loadings.
#
# Two falsifiable predictions follow from that assumption, both content-driven
# (i.e. they would break if the bullets were permuted):
#
#  (a) Loading rank. Table 2 reports SATIS1 0.91 > SATIS2 0.88 > SATIS3 0.64.
#      Bullet 3 ("Normally, this kind of experience makes me feel satisfied") is
#      trait-level rather than about the specific trip, so it should be the
#      WEAKEST indicator of experience-specific satisfaction, and bullet 1
#      ("Overall, I am satisfied with the experience") the global item, the
#      strongest. A just-identified single-factor solution on the live data must
#      reproduce that rank order.
#  (b) Mean/SD ordering. Bullet 2 ("met my vacation needs VERY WELL") is the most
#      demanding claim -> lowest mean. Bullet 3 is a generic disposition
#      statement -> least spread (smallest SD).
#
# What this does NOT establish: it separates bullet 3 from the other two firmly,
# and it is consistent for bullets 1 vs 2, but the published 0.91 vs 0.88 gap and
# the observed loading gap are small, so bullets 1 and 2 are not distinguished
# with the strength item 3 is. Hence status PARTIAL, not VERIFIED.

suppressMessages(library(irw))

TABLE <- "lunacortes_2019_satisfaction"
PUB_LOAD <- c(satis_1 = 0.91, satis_2 = 0.88, satis_3 = 0.64)  # PLOS ONE t002

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
w <- reshape(d[, c("id", "item", "resp")], idvar = "id",
             timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
w <- w[complete.cases(w[, c("satis_1", "satis_2", "satis_3")]), ]
cat(sprintf("complete cases: %d\n\n", nrow(w)))

m  <- colMeans(w[, c("satis_1", "satis_2", "satis_3")])
sd_ <- apply(w[, c("satis_1", "satis_2", "satis_3")], 2, sd)
R  <- cor(w[, c("satis_1", "satis_2", "satis_3")])
r12 <- R[1, 2]; r13 <- R[1, 3]; r23 <- R[2, 3]
# just-identified 1-factor loadings from the 3 correlations
lam <- c(satis_1 = sqrt(r12 * r13 / r23),
         satis_2 = sqrt(r12 * r23 / r13),
         satis_3 = sqrt(r13 * r23 / r12))

cat(sprintf("correlations: r12=%.4f r13=%.4f r23=%.4f\n\n", r12, r13, r23))
cat(sprintf("%-8s %9s %9s %9s %9s\n", "item", "pub_load", "obs_load", "mean", "sd"))
for (i in c("satis_1", "satis_2", "satis_3"))
    cat(sprintf("%-8s %9.2f %9.3f %9.3f %9.3f\n", i, PUB_LOAD[i], lam[i], m[i], sd_[i]))

ok_load <- identical(order(-lam), order(-PUB_LOAD)) &&
           lam["satis_3"] == min(lam)
ok_mean <- (m["satis_2"] == min(m)) && (sd_["satis_3"] == min(sd_))

cat(sprintf("\n(a) loading rank matches published 0.91>0.88>0.64: %s\n",
            ifelse(ok_load, "YES", "NO")))
cat(sprintf("    (obs %.3f > %.3f > %.3f)\n", lam[1], lam[2], lam[3]))
cat(sprintf("(b) satis_2 lowest mean (%.3f) and satis_3 smallest SD (%.3f): %s\n",
            m["satis_2"], sd_["satis_3"], ifelse(ok_mean, "YES", "NO")))
cat("Does NOT establish: the satis_1 vs satis_2 ordering beyond a small gap;\n",
    "PARTIAL, not VERIFIED.\n", sep = "")

cat(if (ok_load && ok_mean) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
