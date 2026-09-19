# verify_meloni_2015_deq_ce_parent.R -- Step 5b.
# Route 3 (published subscale totals, Fig 2 of the article) + route 8 (semantic
# coherence of the statement x target interaction). Parents only (S1 Protocol 101-181).
#
# WHAT IS INFERRED. The four target blocks are NOT inferred: data/meloni_2015_disability.py
# melts the S1 workbook's DEQ*_CE_* columns by name for the parent rows, so the IRW item
# code IS the source column name and MD/SD/CD/ND come straight from the deposit. What is
# inferred (mapping_basis=paper_order) is which of the S2 codebook's eleven roman-numbered
# PARENT-protocol statements (i)..(xi) each DEQ1..DEQ11 carries: the codebook prints them
# as a flat roman list tied to no variable code.
#
# ROUTE 3 IS THE NEW EVIDENCE relative to the child sibling. Fig 2 of the article prints
# the parents' mean agreement for the three disability models: individual 1.45, social
# 2.56, biopsychosocial 2.16. Those are the three contiguous blocks of the codebook's
# statement list -- individual = (i) ethical / (ii) aesthetic / (iii) religious /
# (iv) medical, social = (v) socio-relational / (vi) environmental / (vii) employment,
# biopsychosocial = (viii)-(xi), the compound statements. If the statement numbering were
# shifted, the three published means could not all be reproduced.

suppressMessages(library(irw))
TABLE <- "meloni_2015_deq_ce_parent"

d  <- irw::irw_fetch(TABLE)
st <- as.integer(sub("DEQ([0-9]+)_CE_.*", "\\1", d$item))
tg <- sub(".*_CE_", "", d$item)
m  <- tapply(d$resp, d$item, mean)
g  <- function(i, t) unname(m[sprintf("DEQ%d_CE_%s", i, t)])

ok <- logical(0)
say <- function(lbl, val, pass) {
    ok[[length(ok) + 1L]] <<- pass
    cat(sprintf("%-96s %s\n", paste0(lbl, ": ", val), if (pass) "OK" else "FAIL"))
}

cat(sprintf("N respondents %d, N items %d, rows %d\n\n",
            length(unique(d$id)), length(unique(d$item)), nrow(d)))
cat("mean agreement (1 = strongly disagree .. 4 = strongly agree), statement x target\n")
cat(sprintf("%-4s %6s %6s %6s %6s   %s\n", "st", "MD", "SD", "CD", "ND", "statement"))
lbl <- c("he's bad", "he's ugly", "God wanted it", "he's sick", "others mistreat him",
         "he encounters lots of obstacles", "nobody will give him a job",
         "body does not function well + world makes him things difficult",
         "world makes him things difficult + body does not function well",
         "does not walk well and does not take the bus",
         "nobody will give him a job and he does not walk well")
for (i in 1:11)
    cat(sprintf("%-4d %6.2f %6.2f %6.2f %6.2f   %s\n", i,
                g(i,"MD"), g(i,"SD"), g(i,"CD"), g(i,"ND"), lbl[i]))
cat("\n")

blockmean <- function(sts) mean(d$resp[st %in% sts])

## ---- ROUTE 3: reproduce the three published parent means from Fig 2 ----------------
pub <- c(individual = 1.45, social = 2.56, biopsychosocial = 2.16)
obs <- c(individual = blockmean(1:4), social = blockmean(5:7), biopsychosocial = blockmean(8:11))
say("R3a individual model (statements 1-4) reproduces Fig 2's 1.45",
    sprintf("observed %.3f, |diff| %.3f", obs[1], abs(obs[1] - pub[1])), abs(obs[1]-pub[1]) < 0.03)
say("R3b social model (statements 5-7) reproduces Fig 2's 2.56",
    sprintf("observed %.3f, |diff| %.3f", obs[2], abs(obs[2] - pub[2])), abs(obs[2]-pub[2]) < 0.03)
say("R3c biopsychosocial model (statements 8-11) reproduces Fig 2's 2.16",
    sprintf("observed %.3f, |diff| %.3f", obs[3], abs(obs[3] - pub[3])), abs(obs[3]-pub[3]) < 0.03)

# The published triple also has to REJECT the neighbouring partitions, or it would be
# evidence for nothing. Score every contiguous 3-way split of the eleven statements.
cat("\nevery contiguous 3-way partition of statements 1..11, scored against Fig 2\n")
best <- NULL
for (a in 2:8) for (b in (a+1):10) {
    e <- max(abs(blockmean(1:a) - pub[1]),
             abs(blockmean((a+1):b) - pub[2]),
             abs(blockmean((b+1):11) - pub[3]))
    if (a == 4 && b == 7)
        cat(sprintf("  ind 1-%d / soc %d-%d / bps %d-11   max|err| %.3f   <- shipped\n", a, a+1, b, b+1, e))
    else if (e < 0.20)
        cat(sprintf("  ind 1-%d / soc %d-%d / bps %d-11   max|err| %.3f\n", a, a+1, b, b+1, e))
    if (!(a == 4 && b == 7)) best <- min(c(best, e))
}
shipped_err <- max(abs(obs - pub))
say("R3d the shipped partition beats every one of the other 34 contiguous partitions",
    sprintf("shipped max|err| %.3f vs best rival %.3f (ratio %.1fx)",
            shipped_err, best, best / shipped_err), shipped_err < best / 3)

## ---- ROUTE 8: statement x target contrasts, parents ---------------------------------
cat("\n")
# P0 (option axis). Statements 1-3 attribute the difficulty to badness/ugliness/God's
# will. Under the shipped coding (1 = strongly disagree) parents reject them; under a
# flipped coding they would be endorsing them for a wheelchair user.
say("P0 DEQ1_CE_MD ('he's bad') sits at the disagreement floor, so resp 1 = strongly disagree",
    sprintf("mean %.2f of 1-4; %.0f%% of parents answered exactly 1", g(1,"MD"),
            100 * mean(d$resp[d$item == "DEQ1_CE_MD"] == 1)),
    g(1,"MD") < 1.5)

# P1. Statement 6 is the social-model statement; the article says parents preferred the
# social model. It must be the top statement for both externally-obstructed targets.
say("P1 DEQ6 'he encounters lots of obstacles' is the top statement for MD and for SD",
    sprintf("MD %.2f (next %.2f), SD %.2f (next %.2f)", g(6,"MD"),
            sort(sapply(1:11, function(i) g(i,"MD")), decreasing = TRUE)[2], g(6,"SD"),
            sort(sapply(1:11, function(i) g(i,"SD")), decreasing = TRUE)[2]),
    which.max(sapply(1:11, function(i) g(i,"MD"))) == 6 &&
    which.max(sapply(1:11, function(i) g(i,"SD"))) == 6)

# P2. Statements 1/2/3 (ethical, aesthetic, religious) are the individual model's
# pre-modern attributions and must be the three least endorsed for every disabled target.
low3 <- function(t) sort(order(sapply(1:11, function(i) g(i, t)))[1:3])
say("P2 statements 1,2,3 are the three lowest-agreement statements for MD, SD and CD alike",
    sprintf("MD %s, SD %s, CD %s", paste(low3("MD"), collapse=","),
            paste(low3("SD"), collapse=","), paste(low3("CD"), collapse=",")),
    all(low3("MD") == 1:3) && all(low3("SD") == 1:3) && all(low3("CD") == 1:3))

# P3. Statement 10 is the only purely mobility-specific statement ("he does not walk well
# and he does not take the bus"), so Giovanni (wheelchair) minus Paolo (autistic) must be
# the largest of the eleven gaps.
gaps <- sapply(1:11, function(i) g(i,"MD") - g(i,"CD"))
say("P3 DEQ10 has the largest MD(wheelchair) - CD(autistic) gap of the eleven statements",
    sprintf("gap %.2f (MD %.2f, CD %.2f); next largest %.2f at DEQ%d", gaps[10],
            g(10,"MD"), g(10,"CD"), sort(gaps, decreasing = TRUE)[2],
            which.max(replace(gaps, 10, -Inf))),
    which.max(gaps) == 10)

# P4. Statement 2 ("he's ugly") is the one individual-model attribution that can apply to
# an able-bodied person, so ND must EXCEED all three disability targets on it -- and this
# must not happen for statements 1 or 3.
excND <- function(i) g(i,"ND") > max(g(i,"MD"), g(i,"SD"), g(i,"CD"))
say("P4 among statements 1-3, only DEQ2 'he's ugly' is higher for ND(able-bodied) than for every disability target",
    sprintf("ND 1/2/3 = %.2f/%.2f/%.2f vs max disability target %.2f/%.2f/%.2f",
            g(1,"ND"), g(2,"ND"), g(3,"ND"),
            max(g(1,"MD"),g(1,"SD"),g(1,"CD")), max(g(2,"MD"),g(2,"SD"),g(2,"CD")),
            max(g(3,"MD"),g(3,"SD"),g(3,"CD"))),
    excND(2) && !excND(1) && !excND(3))

# P5. Employment is the only listed difficulty that plausibly applies to Elena, who has no
# disability, so statement 7 must be ND's top statement.
say("P5 DEQ7 'nobody will give him a job' is the highest statement for ND(able-bodied)",
    sprintf("ND %.2f vs next %.2f (DEQ%d)", g(7,"ND"),
            sort(sapply(1:11, function(i) g(i,"ND")), decreasing = TRUE)[2],
            order(sapply(1:11, function(i) g(i,"ND")), decreasing = TRUE)[2]),
    which.max(sapply(1:11, function(i) g(i,"ND"))) == 7)

# P6. The statements that separate disabled from able-bodied targets must be the social
# and biopsychosocial explanations (6, 8, 9), not the individual-model ones.
dgap <- sapply(1:11, function(i) mean(c(g(i,"MD"), g(i,"SD"), g(i,"CD"))) - g(i,"ND"))
say("P6 the three largest disability-minus-ND gaps are statements 6, 8 and 9",
    sprintf("6 %.2f, 8 %.2f, 9 %.2f; next 10 %.2f, 11 %.2f",
            dgap[6], dgap[8], dgap[9], dgap[10], dgap[11]),
    identical(sort(order(dgap, decreasing = TRUE)[1:3]), c(6L, 8L, 9L)))

## ---- WHAT THIS DOES NOT ESTABLISH ---------------------------------------------------
cat("\nNOT ESTABLISHED by these routes:\n")
cat(sprintf("  * statements 8 and 9 are the SAME two clauses in reversed order (means MD %.2f/%.2f,\n    SD %.2f/%.2f, CD %.2f/%.2f); nothing distributional can decide which is which.\n",
            g(8,"MD"), g(9,"MD"), g(8,"SD"), g(9,"SD"), g(8,"CD"), g(9,"CD")))
cat(sprintf("  * statements 1 vs 3 ('he's bad' / 'God wanted it') -- P4 pins 2, but 1 and 3 both sit\n    at the floor for every disabled target (MD %.2f/%.2f, SD %.2f/%.2f, CD %.2f/%.2f).\n",
            g(1,"MD"), g(3,"MD"), g(1,"SD"), g(3,"SD"), g(1,"CD"), g(3,"CD")))
cat(sprintf("  * statement 5 'others mistreat him' is not pinned within the social block (MD %.2f,\n    SD %.2f, CD %.2f, ND %.2f); only 6 and 7 are.\n",
            g(5,"MD"), g(5,"SD"), g(5,"CD"), g(5,"ND")))
cat(sprintf("  * statement 11 is not separated from 10 by anything but P3's ordering of the same\n    mobility contrast (MD-CD gaps %.2f vs %.2f).\n", gaps[10], gaps[11]))
cat("  Hence the recorded status is PARTIAL, not VERIFIED.\n\n")

cat(if (all(unlist(ok))) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
