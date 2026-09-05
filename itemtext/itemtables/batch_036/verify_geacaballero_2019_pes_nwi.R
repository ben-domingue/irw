# verify_geacaballero_2019_pes_nwi.R
#
# Claim being tested (mapping_basis = paper_explicit):
#   each live item code carries the Spanish wording of the numbered item that
#   the study's own .sav variable label assigns to it ("intmanagement" =
#   'item 1', ... "propercollaboration" = 'item 31'), with the wording taken
#   from the numbered questionnaire in Supplemental Information 1
#   (peerj-07-7369-s001.docx), and resp 1..4 = absolutely disagree .. absolutely
#   agree per the .sav's own value labels.
#
# Two independent falsifiable predictions, neither of which is a count check
# that validate_items.R already made:
#
# ROUTE 9 (option_text <-> resp, and item identity).  The deposit's SPSS file
#   (10.7717/peerj.7369/supp-2, md5 900e527ddd057d26d89c230adbf62b2f) stores
#   LABEL STRINGS; the live table stores integers.  RAW below is the per-item
#   count of each label in the .sav, in the order absolutely disagree /
#   slightly disagree / slightly agree / absolutely agree.  A correct mapping
#   reproduces the live per-item x per-resp counts cell for cell; a flipped
#   scale direction, or any two item codes swapped, breaks it.  All 30 count
#   signatures below are DISTINCT, so this separates every item from every
#   other item, not just the scale direction.
#
# ROUTE 3 (published subscale statistics).  The paper reports Cronbach's alpha
#   for the whole scale and for each of the five PES-NWI dimensions.  The
#   dimension membership is a property of the item NUMBERS, so recomputing the
#   alphas from the items this file assigns to each dimension tests the
#   number->code assignment against a published number.
#
# What this does NOT establish: nothing ties the Spanish sentence itself to the
# data beyond the .sav's "item N" label and the supplement's numbering -- the
# routes below verify that the live column called X came from the .sav column
# called X and carries the anchors the .sav says it does, and that the items
# assigned to each dimension behave as the published alphas say that dimension
# does.  Item codes are self-describing in Spanish/English ("nursingdiagn" =
# "Se usan los diagnosticos enfermeros", item 10), which is what rules out a
# permutation within a dimension.

suppressMessages(library(irw))

TABLE <- "geacaballero_2019_pes_nwi"

RAW <- matrix(byrow = TRUE, ncol = 4, c(
    16, 33, 89, 131,
    43, 92, 84, 50,
    21, 39, 88, 121,
    47, 50, 97, 75,
    71, 67, 84, 47,
    51, 95, 83, 40,
    74, 79, 69, 47,
    53, 69, 99, 48,
    34, 50, 88, 97,
    56, 71, 96, 46,
    48, 79, 95, 47,
    41, 78, 104, 46,
    66, 63, 81, 59,
    35, 43, 87, 104,
     8, 24, 116, 121,
    18, 33, 111, 107,
    17, 62, 111, 79,
    30, 47, 120, 72,
    21, 69, 92, 87,
    51, 87, 93, 38,
    40, 88, 96, 45,
    38, 74, 114, 43,
    35, 61, 108, 65,
    11, 39, 123, 96,
    30, 62, 96, 81,
     7, 23, 125, 114,
    35, 47, 73, 114,
    60, 93, 84, 32,
    29, 42, 88, 110,
    24, 57, 123, 65))
rownames(RAW) <- c(
    "asignationpatients", "careeropportunit", "comprehensicoord",
    "directorvisible", "enoughnurses", "enoughsupportserv", "enoughworkers",
    "gestconsprob", "goodcoordinator", "intmanagement", "levelpowerheadnurse",
    "managlistens", "mentoringnews", "mistakeopport", "nursingcompetence",
    "nursingdiagn", "nursingmodel", "nursingphilosophy", "oportcomisions",
    "oportdecisions", "oportdevelopment", "plancuidadosescrito", "progquality",
    "propercollaboration", "qualitymanagers", "relationsnursphysic",
    "supportcoordinator", "timedebatcasses", "workpraised", "worktimephysicians")

d <- irw::irw_fetch(TABLE)
d$resp <- as.integer(d$resp)

cat("== ROUTE 9: deposit .sav label counts vs live resp counts, per item ==\n")
cat(sprintf("%-21s %-18s %-18s %s\n", "item", "sav(1,2,3,4)", "live(1,2,3,4)", "match"))
bad <- 0
for (it in rownames(RAW)) {
    lv <- as.vector(table(factor(d$resp[d$item == it], levels = 1:4)))
    ok <- all(lv == RAW[it, ])
    if (!ok) bad <- bad + 1
    cat(sprintf("%-21s %-18s %-18s %s\n", it,
                paste(RAW[it, ], collapse = ","),
                paste(lv, collapse = ","), if (ok) "OK" else "MISMATCH"))
}
sigs <- apply(RAW, 1, paste, collapse = ",")
cat(sprintf("\ncells compared: %d | mismatched items: %d | distinct count signatures: %d of %d\n",
            length(RAW), bad, length(unique(sigs)), nrow(RAW)))

cat("\n== ROUTE 3: published Cronbach alpha per PES-NWI dimension ==\n")
DIMS <- list(
    "D1 Nurse participation in centre affairs (items 1-9)" =
        c("intmanagement", "oportdecisions", "oportdevelopment", "managlistens",
          "directorvisible", "careeropportunit", "gestconsprob", "oportcomisions",
          "levelpowerheadnurse"),
    "D2 Nursing foundation for quality of care (items 10-19, 18 absent)" =
        c("nursingdiagn", "progquality", "mentoringnews", "nursingmodel",
          "asignationpatients", "nursingphilosophy", "plancuidadosescrito",
          "qualitymanagers", "nursingcompetence"),
    "D3 Management and leadership of head nurse (items 20-24)" =
        c("goodcoordinator", "supportcoordinator", "mistakeopport",
          "comprehensicoord", "workpraised"),
    "D4 Adequate human resources (items 25-28)" =
        c("enoughworkers", "enoughnurses", "enoughsupportserv", "timedebatcasses"),
    "D5 Nurse-physician relationship (items 29-31)" =
        c("worktimephysicians", "relationsnursphysic", "propercollaboration"))
PUBLISHED <- c(0.87, 0.85, 0.93, 0.84, 0.81)   # PeerJ 7:e7369, Results
TOL <- 0.025

w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item",
             direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))

alpha <- function(X) {
    X <- X[complete.cases(X), , drop = FALSE]
    k <- ncol(X)
    k / (k - 1) * (1 - sum(apply(X, 2, var)) / var(rowSums(X)))
}

worst <- 0
for (i in seq_along(DIMS)) {
    a <- alpha(w[, DIMS[[i]], drop = FALSE])
    worst <- max(worst, abs(a - PUBLISHED[i]))
    cat(sprintf("%-68s published %.2f  observed %.3f  diff %+.3f\n",
                names(DIMS)[i], PUBLISHED[i], a, a - PUBLISHED[i]))
}
a_all <- alpha(w[, rownames(RAW), drop = FALSE])
cat(sprintf("%-68s published %.3f  observed %.3f  (published value is for all 31 items;\n%s\n",
            "whole scale", 0.943, a_all,
            "   the IRW table omits item 18 'education', so a small gap is expected here)"))
cat(sprintf("\nlargest dimension deviation: %.3f (tolerance %.3f)\n", worst, TOL))

pass <- bad == 0 && length(unique(sigs)) == nrow(RAW) && worst <= TOL
cat(if (pass) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
