# verify_pecino_2018_justice_climate.R -- batch_129, 2026-09-10
#
# THIS TABLE SHIPPED NO ITEM TEXT. It is BLOCKED on text availability: the source
# article never names or reproduces the instrument these six items come from, its
# only supporting file is the SPSS data deposit, and that deposit labels the six
# columns by DIMENSION only ("Support", "Innovation", "Goals"), never by item.
# So mapping_basis = unknown and Step 5b status = NO_ROUTE -- there is no
# item_text <-> item mapping to re-run.
#
# What this script re-runs is the three claims the round actually made:
#
#   (A) IDENTITY / RESP AXIS. The live table's cl1ap..cl6me are the S1 .sav
#       columns of the same names, and its integers are that file's value-label
#       codes in the labelled direction. Falsifiable prediction: all 36
#       item x level cell counts match the .sav cell for cell.
#
#   (B) NO ITEM TEXT AT THE SOURCE. The .sav's variable labels for those six
#       columns are exactly "Support","Support","Innovation","Support",
#       "Innovation","Goals" -- dimension names, shared by up to three items, so
#       they cannot distinguish cl1ap from cl2ap or cl4ap.
#
#   (C) STEP 3b MIS-NAMING. The paper's Interpersonal Justice Climate measure is
#       four Colquitt items on a 1-5 scale, present in the deposit as
#       jus12int..jus15int and NOT in IRW. The table named for it holds six
#       FOCUS-93 climate items on 1-6 instead.
#
#   VERDICT: PASS = all three reproduce; the block stands and is correctly reasoned.
#   VERDICT: FAIL = one did not reproduce; a human should look before this table is
#                   re-queued, re-named, or the block relied on again.
#
# What this does NOT establish: anything about item wording, because none was
# shipped and none exists at the source. Every check here is about the join keys
# and about the ABSENCE of text, not about text.
#
# Needs: R packages irw, haven (or foreign); network access to PLOS.

suppressMessages(library(irw))

TABLE    <- "pecino_2018_justice_climate"
SAV_URL  <- paste0("https://journals.plos.org/plosone/article/file",
                   "?type=supplementary&id=10.1371/journal.pone.0207458.s001")
SAV_SHA  <- "7408cb35f09f4e3316b32e76159d87edf6d7c2dbf7310f8ff7375d2365b208fb"
ITEMS    <- c("cl1ap", "cl2ap", "cl3in", "cl4ap", "cl5in", "cl6me")

# (A) as read from the .sav on 2026-09-10, rows = counts of resp 1..6
EXPECT_CELLS <- rbind(
    cl1ap = c(  4,  11,  54,  79, 116, 178),
    cl2ap = c(  8,  34,  88, 114, 105,  93),
    cl3in = c(  3,  49, 142, 125,  91,  32),
    cl4ap = c(  8,  72, 134,  93,  78,  57),
    cl5in = c(  5,  27, 128, 142,  93,  47),
    cl6me = c(  3,  29,  91, 101, 130,  88))

# (B) the ONLY text the deposit attaches to these six columns
EXPECT_VARLABS <- c("Support", "Support", "Innovation", "Support", "Innovation", "Goals")
EXPECT_ANCHORS <- c("No one", "Few", "Someone", "Quite", "Considerable", "Everyone")

UA <- "IRW-Finder/1.0 (ben.domingue@gmail.com)"
ok_A <- FALSE; ok_B <- FALSE; ok_C <- FALSE

cat(sprintf("table : %s\n\n", TABLE))

## ---------------------------------------------------------------- fetch source
sav <- tempfile(fileext = ".sav")
got <- tryCatch({
    system2("curl", c("-sSL", "-A", shQuote(UA), "-o", shQuote(sav), shQuote(SAV_URL)))
    file.exists(sav) && file.size(sav) > 50000
}, error = function(e) { cat("fetch error: ", conditionMessage(e), "\n", sep = ""); FALSE })

if (!got) {
    cat("could not fetch the PLOS S1 Dataset; nothing re-confirmed this run\n")
} else {
    if (requireNamespace("digest", quietly = TRUE)) {
        sha <- digest::digest(file = sav, algo = "sha256")
        cat(sprintf(".sav sha256      : %s  (%s)\n", sha,
                    if (identical(sha, SAV_SHA)) "byte-identical to the copy read 2026-09-10"
                    else "DIFFERS from the recorded copy"))
    }
    if (!requireNamespace("haven", quietly = TRUE)) stop("package 'haven' not available")
    d <- haven::read_sav(sav)
    cat(sprintf(".sav rows        : %d\n\n", nrow(d)))

    ## ------------------------------------------------ (A) identity / resp axis
    cat("== (A) live item x resp cell counts vs the .sav's own columns ==\n")
    live <- tryCatch(irw::irw_fetch(TABLE), error = function(e) NULL)
    if (is.null(live)) {
        cat("irw_fetch failed; (A) not re-confirmed this run\n")
    } else {
        lt <- table(factor(live$item, levels = ITEMS), factor(live$resp, levels = 1:6))
        st <- t(vapply(ITEMS, function(cc)
            as.numeric(table(factor(as.numeric(d[[cc]]), levels = 1:6))), numeric(6)))
        cat(sprintf("%-8s %-28s %-28s %s\n", "item", "live 1..6", "source 1..6", "match"))
        for (i in seq_along(ITEMS))
            cat(sprintf("%-8s %-28s %-28s %s\n", ITEMS[i],
                        paste(sprintf("%4d", lt[i, ]), collapse = ""),
                        paste(sprintf("%4d", st[i, ]), collapse = ""),
                        if (all(lt[i, ] == st[i, ])) "yes" else "NO"))
        ok_A <- all(lt == st) && all(st == EXPECT_CELLS)
        cat(sprintf("\n=> all 36 cells reproduce, and match the 2026-09-10 reading: %s\n",
                    if (ok_A) "YES" else "NO"))
    }

    ## -------------------------------------------- (B) no item text at the source
    cat("\n== (B) what text the deposit actually attaches to these six columns ==\n")
    varlabs <- vapply(ITEMS, function(cc) {
        l <- attr(d[[cc]], "label"); if (is.null(l)) NA_character_ else as.character(l) }, character(1))
    for (i in seq_along(ITEMS))
        cat(sprintf("  %-8s variable label = %s\n", ITEMS[i], varlabs[i]))
    anch <- names(attr(d[[ITEMS[1]]], "labels"))
    cat(sprintf("  value labels (cl1ap) = %s\n", paste(anch, collapse = " / ")))
    # cl7..cl40 must carry the OTHER anchor set, which is why the split produced 6 items
    other <- names(attr(d[["cl7re"]], "labels"))
    cat(sprintf("  value labels (cl7re) = %s\n", paste(other, collapse = " / ")))
    dup <- sum(duplicated(varlabs))
    cat(sprintf("  distinct variable labels among the six: %d (so %d item(s) share a label)\n",
                length(unique(varlabs)), dup))
    ok_B <- identical(unname(varlabs), EXPECT_VARLABS) &&
            identical(anch, EXPECT_ANCHORS) && !identical(anch, other) && dup > 0
    cat(sprintf("=> the only text present is a shared DIMENSION name, not item wording: %s\n",
                if (ok_B) "YES" else "NO"))

    ## ------------------------------------------------------ (C) Step 3b mismatch
    cat("\n== (C) the paper's actual interpersonal justice items are elsewhere in the deposit ==\n")
    jus <- paste0("jus", 12:15, "int")
    jlabs <- vapply(jus, function(cc) as.character(attr(d[[cc]], "label")), character(1))
    jlev  <- names(attr(d[[jus[1]]], "labels"))
    for (i in seq_along(jus))
        cat(sprintf("  %-9s variable label = %-18s levels = %d\n", jus[i], jlabs[i],
                    length(names(attr(d[[jus[i]]], "labels")))))
    cat(sprintf("  jus12int anchors     = %s\n", paste(jlev, collapse = " / ")))
    cat(sprintf("  in IRW as items?     = %s\n",
                if (!is.null(live)) paste(intersect(jus, unique(live$item)), collapse = ", ") else "unknown"))
    ok_C <- all(grepl("^Interpersonal", jlabs)) && length(jlev) == 5 &&
            (is.null(live) || length(intersect(jus, unique(live$item))) == 0)
    cat("=> 4 Colquitt items on a 1-5 scale, absent from IRW, while the table named\n")
    cat(sprintf("   for them holds 6 items on a 1-6 scale: %s\n", if (ok_C) "YES" else "NO"))
}

cat("\nNote: this script verifies the BLOCK, the join keys and the mis-naming -- not any\n",
    "item_text, because none was shipped and none is published. The dimension labels do\n",
    "not separate cl1ap / cl2ap / cl4ap (all 'Support') from one another.\n", sep = "")

cat(if (ok_A && ok_B && ok_C) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
