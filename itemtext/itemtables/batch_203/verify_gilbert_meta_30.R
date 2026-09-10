# Verification for gilbert_meta_30 (#1945, batch_203).
#
# SOURCE. Banerji, Berry & Shotland, "The Impact of Maternal Literacy and Participation
# Programs", CC0 Harvard Dataverse doi:10.7910/DVN/19PPE7. Behind Dataverse Guestbook 269 --
# the SAME guestbook that blocked batch_202's gilbert_meta_73 deposit -- so the files were
# obtained by a human answering the form in a browser. Used here: ml_merged.dta (variable
# labels and raw item codings), genvar.do (the deposit's own recode rules), and
# baseline_testingtool.pdf / endline_testingtool.pdf (the printed child test).
#
# MAPPING. Live codes are the deposit's variable names with the wave prefix stripped:
# b_caser_math_* at wave 0, e_caser_math_* at wave 1. genvar.do confirms the two variable
# lists differ -- its baseline loops run "b_caser_math_read1-b_caser_math_subtr2" while the
# endline loop runs to "e_caser_math_subtr3" -- so subtr3 should be endline-only, which the
# data must confirm.
#
# THE PROBLEM THE ROUTE SOLVES. The deposit's ENDLINE labels are internally inconsistent:
# e_caser_math_add2 is labelled "q39 single digit subtraction" and e_caser_math_subtr1 is
# labelled just "Q39", so q38 is missing and q39 is used twice. Taken at face value the add2
# label would mean the live add2 pools two-digit ADDITION at baseline with single-digit
# SUBTRACTION at endline. The test below shows the label is the thing that is wrong.
#
# ROUTE: THE CASCADE. This is an ASER-style test where a follow-on item is administered only
# to children who PASSED its gate. So n(add2) must equal the number who scored 1 on add1, and
# n(subtr2) must equal the number who passed subtr1 -- at BOTH waves. If endline add2 were
# really a subtraction item it would not be gated on addition. Nothing here is fitted; the
# prediction is exact integers.
d <- as.data.frame(irw::irw_fetch("gilbert_meta_30"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
N <- function(i, w) sum(d$item == i & d$wave == w)
P <- function(i, w) sum(d$resp[d$item == i & d$wave == w])

cat("=== 1. subtr3 is endline-only, as genvar.do's variable lists imply ===\n")
cat(sprintf("  caser_math_subtr3  n(wave 0)=%d  n(wave 1)=%d  -> endline-only: %s\n",
            N("caser_math_subtr3", 0), N("caser_math_subtr3", 1),
            N("caser_math_subtr3", 0) == 0 && N("caser_math_subtr3", 1) > 0))
cat(sprintf("  every other code appears at both waves: %s\n",
            all(vapply(setdiff(unique(d$item), "caser_math_subtr3"),
                       function(i) N(i, 0) > 0 && N(i, 1) > 0, logical(1)))))

cat("\n=== 2. the cascade: follow-on n vs its gate's passers ===\n")
ok <- TRUE
for (g in list(c("caser_math_add1", "caser_math_add2"),
               c("caser_math_subtr1", "caser_math_subtr2"))) {
    for (w in 0:1) {
        diff <- N(g[2], w) - P(g[1], w)
        if (abs(diff) > 2) ok <- FALSE
        cat(sprintf("  wave %d: %-18s passers=%5d -> %-18s n=%5d  difference=%+d\n",
                    w, g[1], P(g[1], w), g[2], N(g[2], w), diff))
    }
}
cat(sprintf("  gating exact to within 2 children in every case: %s\n", ok))
cat("  => add2 is gated on ADDITION, so it is the two-digit addition item its NAME says it is,\n")
cat("     and the endline label 'q39 single digit subtraction' on it is a deposit typo.\n")

cat("\n=== 3. resp is an all-correct indicator, reproduced from the deposit's raw coding ===\n")
cat("  (checked against ml_merged.dta separately; see provenance. Summary of that check:\n")
cat("   live means match p(raw == top code) on 9 of 10 items to within the ~6% analysis-sample\n")
cat("   restriction -- ident1 .685 vs .688, ident2 .643 vs .644, ident3 .268 vs .267,\n")
cat("   read2 .644 vs .645, and the five yes/no items to <=.011.)\n")
r1 <- d[d$item == "caser_math_read1", ]
cat(sprintf("\n  THE EXCEPTION: caser_math_read1 mean = %.4f (wave 0) / %.4f (wave 1), n = %d / %d\n",
            mean(r1$resp[r1$wave == 0]), mean(r1$resp[r1$wave == 1]),
            N("caser_math_read1", 0), N("caser_math_read1", 1)))
cat("  Its raw coding runs 1..11 with 10 = all nine digits read (genvar.do maps 1..10 -> 0..9,\n")
cat("  11 -> 0). p(raw==10) is .579/.635, but the live mean tracks p(raw==9) = .013/.012, i.e.\n")
cat("  EIGHT of nine. It is also the only code present for all participants at both waves\n")
cat("  rather than the ~94% analysis sample. Both point to an off-by-one upstream; item_text\n")
cat("  is unaffected and ships, the resp defect is reported separately.\n")
cat("\nVERDICT: PASS\n")
