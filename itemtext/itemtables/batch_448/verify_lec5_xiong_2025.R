# verify_lec5_xiong_2025.R -- Step 5b, route 8 (semantic coherence of the response
# distribution) sharpened by a between-sample contrast.
#
# Claim: IRW item lecN (= source column lecN, OSF wg568) is LEC-5 Standard event N.
# The deposit carries no variable labels, so the tie from lecN to event N is an
# inference that the study numbered its columns in the instrument's order.
#
# The live table stacks four samples in the processing script's bind_rows order
# (data/ders16_xiong_2025.R): adolescents (ids 1-5927), college students
# (5928-7393), community adults (7394-8094), male prisoners (8095-9506). Those
# boundaries are checked below against the per-sample means read from the OSF
# .sav files, then the item-content predictions are tested. resp: 1 = exposed
# to the event (LEC_T in each .sav equals the row sum of lec1..lec17).
#
# The predictions follow from the event wording. Disclosure: they were written
# AFTER the per-sample prevalence table had been viewed, so they are not
# pre-registered; each is nonetheless an item-content claim that would break
# if the named items were swapped:
#   P1 lec16 (harm YOU caused), lec11 (captivity), lec7 (assault with a weapon)
#      are all among the 4 items with the highest prisoner : non-prisoner-adult
#      prevalence ratio.
#   P2 lec1 (natural disaster) has the lowest such ratio of all 17 items.
#   P3 lec1 and lec3 (disaster, transport accident) are the two most prevalent
#      events among non-prisoner adults.
#   P4 lec10 (combat / war zone) is the rarest event among non-prisoner adults.
#   P5 lec6 (physical assault) > lec7 (assault with a weapon) in every sample.
#   P6 lec9 (other unwanted sexual experience) > lec8 (sexual assault) in every
#      sample.
#   P7 lec15 (sudden accidental death) > lec14 (sudden violent death) in every
#      sample.
# NOT established: order within {lec2, lec4, lec5}, lec12 vs lec13, lec17's
# position among the moderate-ratio items. Hence PARTIAL, not VERIFIED.

suppressMessages(library(irw))
d <- irw::irw_fetch("lec5_xiong_2025")
d$id <- as.numeric(d$id)
d$s <- cut(d$id, c(0, 5927, 7393, 8094, 9506), labels = c("ado", "col", "com", "pri"))
it <- paste0("lec", 1:17)
m <- with(d, tapply(resp, list(item, s), mean))[it, ]
adult <- with(d[d$s %in% c("col", "com"), ], tapply(resp, item, mean))[it]
ratio <- m[, "pri"] / adult
print(round(cbind(m, nonpri_adult = adult, ratio = ratio), 3))

ok <- logical(0)
# sample boundaries: per-sample means read from the OSF .sav files (col/com/pri)
sav <- rbind(col = c(lec1 = .373, lec6 = .110, lec16 = .008),
             com = c(lec1 = .459, lec6 = .080, lec16 = .010),
             pri = c(lec1 = .397, lec6 = .353, lec16 = .115))
live <- t(m[c("lec1", "lec6", "lec16"), c("col", "com", "pri")])
cat("\nsample-boundary check (.sav vs live):\n"); print(cbind(sav, round(live, 3)))
ok["boundaries"] <- max(abs(sav - live)) < 0.0006

top4 <- names(sort(ratio, decreasing = TRUE))[1:4]
cat("\nP1 top-4 prisoner ratio:", top4, "\n")
ok["P1"] <- all(c("lec16", "lec11", "lec7") %in% top4)
cat("P2 lowest ratio:", names(which.min(ratio)), sprintf("(%.2f)\n", min(ratio)))
ok["P2"] <- names(which.min(ratio)) == "lec1"
top2 <- names(sort(adult, decreasing = TRUE))[1:2]
cat("P3 two most prevalent (non-prisoner adults):", top2, "\n")
ok["P3"] <- setequal(top2, c("lec1", "lec3"))
cat("P4 rarest (non-prisoner adults):", names(which.min(adult)), sprintf("(%.4f)\n", min(adult)))
ok["P4"] <- names(which.min(adult)) == "lec10"
cat("P5 lec6 vs lec7:", sprintf("%.3f>%.3f", m["lec6", ], m["lec7", ]), "\n")
ok["P5"] <- all(m["lec6", ] > m["lec7", ])
cat("P6 lec9 vs lec8:", sprintf("%.3f>%.3f", m["lec9", ], m["lec8", ]), "\n")
ok["P6"] <- all(m["lec9", ] > m["lec8", ])
cat("P7 lec15 vs lec14:", sprintf("%.3f>%.3f", m["lec15", ], m["lec14", ]), "\n")
ok["P7"] <- all(m["lec15", ] > m["lec14", ])
print(ok)
cat("Does NOT establish: order within {lec2,lec4,lec5}, lec12 vs lec13, or lec17's position.\n")
cat(if (all(ok)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
