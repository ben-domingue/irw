# Mapping verification for ALSECYPIAMH_WU_2022_SDQ (issue #1647).
#
# There is NO level-1 anchor. The study's own CPS Study 2.sav labels SDQ_Pro
# "Prosocial Behaviour" and leaves SDQ_Pro1..SDQ_Pro5 unlabelled; the OSF node
# publishes only the CPS supplement, and the JORA paper is paywalled. The
# shipped mapping therefore assumes SDQ_Pro1..5 follow the SDQ's own fixed
# prosocial order (SDQ items 1, 4, 9, 17, 20). This script tests the two
# endpoints of that assumption plus the SDQ_Pro composite claim.
#
# CHECK A (composite): SDQ_Pro == round(mean(SDQ_Pro1..5)) for every
#   respondent, checked in the source .sav. CHECK A2: that composite is no
#   longer shipped as an item in the IRW table (issue #1691).
# CHECK B (endpoints): in community adolescent samples the SDQ prosocial item
#   "I try to be nice to other people" is the most endorsed and "I often
#   volunteer to help others" the least. Predicts Pro1 = highest mean and
#   Pro5 = lowest mean of the five.
# This pins the two endpoints only -- it does NOT distinguish Pro2/Pro3/Pro4
# from each other. Hence PARTIAL, not VERIFIED.

options(irw.itemtext_disclaimer = FALSE)
suppressMessages(library(irw))

d <- as.data.frame(irw_fetch("ALSECYPIAMH_WU_2022_SDQ"))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
its <- paste0("SDQ_Pro", 1:5)

# CHECK A now runs against the SOURCE file, not the IRW table. SDQ_Pro was
# removed from the table (issue #1691), so `w$SDQ_Pro` is NULL there and
# `all(NULL == round(m))` returns TRUE vacuously -- the check would report a
# pass while testing nothing.
sav <- tempfile(fileext = ".sav")
download.file("https://osf.io/download/sj7xc/", sav, mode = "wb", quiet = TRUE)
raw <- haven::read_sav(sav)
m_raw <- rowMeans(raw[, its])
a_ok <- all(raw$SDQ_Pro == round(m_raw))
cat("CHECK A -- SDQ_Pro == round(mean(SDQ_Pro1..5)) in CPS Study 2.sav for all",
    nrow(raw), "respondents:", a_ok, "\n")

# And the composite must NOT be in the shipped table any more.
a2_ok <- !("SDQ_Pro" %in% unique(d$item))
cat("CHECK A2 -- SDQ_Pro absent from the IRW table:", a2_ok, "\n")

m <- rowMeans(w[, its])

mu <- sort(colMeans(w[, its]), decreasing = TRUE)
cat("\nCHECK B -- per-item means, descending:\n")
print(round(mu, 4))
b_ok <- names(mu)[1] == "SDQ_Pro1" && names(mu)[5] == "SDQ_Pro5"
cat("highest =", names(mu)[1], "(predicted SDQ_Pro1); lowest =", names(mu)[5],
    "(predicted SDQ_Pro5) ->", b_ok, "\n")

cat("\nceiling %% (resp == 3) per item:\n")
print(round(sapply(w[, its], function(v) 100 * mean(v == 3)), 2))

cat("\nNOT ESTABLISHED: the relative order of SDQ_Pro2, SDQ_Pro3 and SDQ_Pro4.\n")
cat(if (a_ok && a2_ok && b_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
