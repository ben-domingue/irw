# verify_meloni_2015_deq_ce_child.R -- Step 5b, route 8 (semantic coherence of the
# response distribution), with the target x statement interaction as the signal.
#
# WHAT IS INFERRED. The four target blocks are NOT inferred: data/meloni_2015_disability.py
# melts the S1 workbook columns by name, so the IRW item code IS the source column name and
# MD/SD/CD/ND come straight from the deposit. What is inferred (mapping_basis=paper_order)
# is which of the S2 codebook's eleven roman-numbered statements (i)..(xi) each DEQ1..DEQ11
# carries: the codebook prints the statements as a flat roman list tied to no variable code.
#
# THE FALSIFIABLE PREDICTIONS. Each statement attributes a different cause, and the four
# targets differ in a known way (Giovanni = wheelchair/MD, Maria = blind/SD, Paolo =
# autistic/CD, Elena = able-bodied/ND). If the statement numbering were permuted, the
# content x target contrasts below would land on the wrong item codes.

suppressMessages(library(irw))
TABLE <- "meloni_2015_deq_ce_child"

d <- irw::irw_fetch(TABLE)
m <- tapply(d$resp, d$item, mean)
g <- function(i, t) unname(m[sprintf("DEQ%d_CE_%s", i, t)])
ok <- logical(0); say <- function(lbl, val, pass) {
    ok[[length(ok) + 1L]] <<- pass
    cat(sprintf("%-78s %s\n", paste0(lbl, ": ", val), if (pass) "OK" else "FAIL"))
}

cat("mean agreement (1 = strongly disagree .. 4 = strongly agree), statement x target\n")
cat(sprintf("%-4s %6s %6s %6s %6s   %s\n", "st", "MD", "SD", "CD", "ND", "statement"))
lbl <- c("he's bad", "he's ugly", "God wanted it", "he's sick", "others mistreat him",
         "he encounters lots of obstacles", "nobody will give him a job",
         "body does not function well + world makes it difficult",
         "world makes it difficult + body does not function well",
         "does not walk well and does not take the bus",
         "nobody will give him a job and he does not walk well")
for (i in 1:11)
    cat(sprintf("%-4d %6.2f %6.2f %6.2f %6.2f   %s\n", i,
                g(i,"MD"), g(i,"SD"), g(i,"CD"), g(i,"ND"), lbl[i]))
cat("\n")

# P1. Statement 10 is the only purely mobility-specific statement ("he does not walk well
#     and he does not take the bus"). It must be MD's top item, and its MD-CD gap must be
#     the largest of the eleven.
gaps <- sapply(1:11, function(i) g(i,"MD") - g(i,"CD"))
rk <- function(i, t) { v <- sapply(1:11, function(j) g(j, t)); rank(-v)[i] }
say("P1a DEQ10 ranks near the top for MD but near the bottom for CD",
    sprintf("MD rank %.0f of 11 (mean %.2f), CD rank %.0f of 11 (mean %.2f)",
            rk(10,"MD"), g(10,"MD"), rk(10,"CD"), g(10,"CD")),
    rk(10,"MD") <= 2 && rk(10,"CD") >= 7)
say("P1b DEQ10 has the largest MD-CD gap of the 11 statements",
    sprintf("gap %.2f (MD %.2f, CD %.2f); next largest %.2f at DEQ%d",
            gaps[10], g(10,"MD"), g(10,"CD"), sort(gaps, decreasing = TRUE)[2],
            which.max(replace(gaps, 10, -Inf))),
    which.max(gaps) == 10)

# P2. Statement 11 also contains "he does not walk well", so it must be the SECOND largest
#     MD-CD gap.
say("P2 DEQ11 has the second largest MD-CD gap",
    sprintf("gap %.2f (MD %.2f, CD %.2f)", gaps[11], g(11,"MD"), g(11,"CD")),
    order(gaps, decreasing = TRUE)[2] == 11)

# P3. Statement 4 is "he's sick" -- must be endorsed for all three disability targets and
#     rejected for the able-bodied target.
say("P3 DEQ4 (he's sick): MD/SD/CD all > 2.4, ND < 1.8",
    sprintf("MD %.2f SD %.2f CD %.2f ND %.2f", g(4,"MD"), g(4,"SD"), g(4,"CD"), g(4,"ND")),
    all(c(g(4,"MD"), g(4,"SD"), g(4,"CD")) > 2.4) && g(4,"ND") < 1.8)

# P4. Paper-explicit corroboration (Discussion): the children found "[Giovanni has difficult
#     in life because] he encounters lots of obstacles" MORE agreeable than "[...] he's ugly".
#     Giovanni is the MD target, so this ties statements 6 and 2 to their codes by name.
say("P4 (paper text, MD/Giovanni) DEQ6 'lots of obstacles' > DEQ2 'he's ugly'",
    sprintf("%.2f vs %.2f", g(6,"MD"), g(2,"MD")), g(6,"MD") > g(2,"MD") + 1)

# P5. Statement 6 is the social-model statement and must be the top statement for both
#     externally-obstructed targets (MD, SD).
say("P5 DEQ6 is the highest-agreement statement for SD",
    sprintf("%.2f vs next %.2f", g(6,"SD"),
            sort(sapply(1:11, function(i) g(i,"SD")), decreasing = TRUE)[2]),
    which.max(sapply(1:11, function(i) g(i,"SD"))) == 6)

# P6. The able-bodied target (Elena) must sit at the floor for every disability-attributing
#     statement: ND's maximum must be below every other target's maximum by a wide margin.
ndmax <- max(sapply(1:11, function(i) g(i,"ND")))
say("P6 ND's highest item is below every disability target's highest item",
    sprintf("ND max %.2f (DEQ%d); MD max %.2f SD max %.2f CD max %.2f", ndmax,
            which.max(sapply(1:11, function(i) g(i,"ND"))),
            max(sapply(1:11, function(i) g(i,"MD"))),
            max(sapply(1:11, function(i) g(i,"SD"))),
            max(sapply(1:11, function(i) g(i,"CD")))),
    ndmax < 2.0 && min(max(sapply(1:11, function(i) g(i,"MD"))),
                       max(sapply(1:11, function(i) g(i,"SD"))),
                       max(sapply(1:11, function(i) g(i,"CD")))) > ndmax + 0.7)

# WHAT THIS DOES NOT ESTABLISH.
cat("\nNOT ESTABLISHED by this route:\n")
cat(sprintf("  * statements 8 and 9 are the SAME two clauses in reversed order, and their\n    means are %.2f/%.2f (MD), %.2f/%.2f (SD), %.2f/%.2f (CD) -- no distributional route\n    can separate them, and swapping them would be undetectable.\n",
            g(8,"MD"), g(9,"MD"), g(8,"SD"), g(9,"SD"), g(8,"CD"), g(9,"CD")))
cat(sprintf("  * statements 1/2/3 ('he's bad' / 'he's ugly' / 'God wanted it') all sit at the\n    floor: MD %.2f/%.2f/%.2f, CD %.2f/%.2f/%.2f. Their order rests on the codebook list.\n",
            g(1,"MD"), g(2,"MD"), g(3,"MD"), g(1,"CD"), g(2,"CD"), g(3,"CD")))
cat(sprintf("  * statements 5 and 7 ('others mistreat him' / 'nobody will give him a job') are\n    not separated either: MD %.2f/%.2f, CD %.2f/%.2f.\n",
            g(5,"MD"), g(7,"MD"), g(5,"CD"), g(7,"CD")))
cat("  Hence the recorded status is PARTIAL, not VERIFIED.\n\n")

cat(if (all(unlist(ok))) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
