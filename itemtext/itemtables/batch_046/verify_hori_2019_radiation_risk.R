# Step 5b verification for hori_2019_radiation_risk.
#
# CLAIM: item code Qn is questionnaire question n of Hori et al. (2019) PLOS ONE
# 14(3):e0212917 (S1 Fig Japanese / S2 Fig English), and for each item the shipped
# option_text sits on the right resp code (which code is the "yes"/affirmative one).
#
# FALSIFIABLE PREDICTION: Tables 1 and 2 of the paper print, for every one of the 21
# questions, the number of "yes" responses split by the concerns(+) / concerns(-)
# grouping (which is Q14 itself, 355 / 195 per the Results text). If Qn were mapped to
# a different question, or if the affirmative code were the other one, those two cell
# counts would not reproduce. All 21 published (concerns+, concerns-) pairs are
# mutually distinct, so the match distinguishes EVERY item from EVERY other item.
#
# This does NOT establish the exact boundary of the 4-point -> 2-level collapse on
# Q13/Q14/Q18/Q20/Q21, nor the age/years cutpoints behind Q1/Q6/Q8's 1/2 codes; it
# establishes which question each code is and which code is the affirmative one.

suppressMessages(library(irw))

TABLE <- "hori_2019_radiation_risk"

# item -> (affirmative resp code, published concerns(+) n, published concerns(-) n)
# Table 1 (t001): Q1..Q6, Q11, Q12, Q13, Q15.  Table 2 (t002): Q7..Q10, Q16..Q21.
# Q14 is the grouping variable itself (Results: 355 concerns(+), 195 concerns(-)).
YES <- c(Q1=2, Q2=2, Q3=1, Q4=1, Q5=1, Q6=2, Q7=2, Q8=2, Q9=4, Q10=1, Q11=1,
         Q12=1, Q13=1, Q14=1, Q15=1, Q16=1, Q17=1, Q18=1, Q19=1, Q20=1, Q21=1)
PUB_POS <- c(Q1=297, Q2=189, Q3=80, Q4=155, Q5=195, Q6=123, Q7=248, Q8=231, Q9=304,
             Q10=40, Q11=113, Q12=68, Q13=338, Q14=355, Q15=148, Q16=34, Q17=221,
             Q18=315, Q19=109, Q20=345, Q21=62)
PUB_NEG <- c(Q1=128, Q2=60, Q3=58, Q4=82, Q5=97, Q6=47, Q7=96, Q8=89, Q9=161,
             Q10=31, Q11=64, Q12=34, Q13=26, Q14=0, Q15=43, Q16=8, Q17=98,
             Q18=120, Q19=69, Q20=178, Q21=37)

d <- irw::irw_fetch(TABLE)
d$id <- as.character(d$id); d$item <- as.character(d$item)
d$resp <- as.numeric(d$resp)

grp <- d[d$item == "Q14", c("id", "resp")]
names(grp)[2] <- "q14"
cat(sprintf("grouping variable Q14: concerns(+) n=%d, concerns(-) n=%d (published 355 / 195)\n\n",
            sum(grp$q14 == 1), sum(grp$q14 == 2)))

m <- merge(d, grp, by = "id")
cat(sprintf("%-5s %4s %14s %14s %s\n", "item", "yes", "obs (pos,neg)", "pub (pos,neg)", ""))
bad <- 0
for (q in names(YES)) {
    s <- m[m$item == q & m$resp == YES[[q]], ]
    op <- sum(s$q14 == 1); on <- sum(s$q14 == 2)
    ok <- (op == PUB_POS[[q]] && on == PUB_NEG[[q]])
    if (!ok) bad <- bad + 1
    cat(sprintf("%-5s %4d %14s %14s %s\n", q, YES[[q]],
                sprintf("(%d,%d)", op, on),
                sprintf("(%d,%d)", PUB_POS[[q]], PUB_NEG[[q]]),
                if (ok) "OK" else "MISMATCH"))
}

# The mapping is only identified if the published pairs are mutually distinct.
pairs <- paste(PUB_POS, PUB_NEG, sep = ",")
cat(sprintf("\ndistinct published (pos,neg) pairs: %d of %d\n", length(unique(pairs)), length(pairs)))
cat(sprintf("items mismatching: %d of %d\n", bad, length(YES)))
cat("Note: this pins WHICH question each code is and WHICH code is affirmative.\n",
    "It does not pin the collapse boundary of the 4-point items (Q13/Q14/Q18/Q20/Q21)\n",
    "nor the numeric cutpoints behind Q1/Q6/Q8 -- those are stated in provenance.\n", sep = "")

cat(if (bad == 0 && length(unique(pairs)) == length(pairs)) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
