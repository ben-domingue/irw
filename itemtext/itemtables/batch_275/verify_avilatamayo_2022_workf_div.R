# Step 5b verification for avilatamayo_2022_workf_div  (batch_275)
#
# mapping_basis = paper_order. The IRW item code IS the SPSS column name
# (data/avilatamayo_2022_csr.py selects columns by prefix and melts by name,
# with no rename), and the .sav variable labels pin each code to an ORDINAL
# ("Workforce diversity 1" .. "Workforce diversity 6") but carry no wording.
# What is INFERRED is that the k-th row under "Diversidad" / "Workforce
# diversity" in the S1 Appendix (which numbers no row) is item k.
#
# Tested here:
#   A. route 9 -- option_text <-> resp. The .sav stores 1..7 with English value
#      labels ("Totally disagree".."Totally agree"); the live table stores 1..7.
#      All 42 item x level cell counts must match; a flipped or permuted anchor
#      set breaks this immediately.
#   B. route 3 -- published subscale statistics. Table 1 of the paper reports
#      Workforce diversity M = 4.91, SD = 1.32, Cronbach's alpha = .89.
#   C. route 3-bis -- published subgroup means. Table 3 reports the composite by
#      contract type: Full-time 5.11, Fixed-term 4.66, t = 3.61.
#   D. route 8 -- semantic coherence of the per-item means against item content.
#
# What this does NOT establish: the ORDER of the six item texts within the
# subscale. The paper publishes no per-item statistic (Fig 2 is a second-order
# path diagram with seven construct-level loadings; Tables 1-3 are composite
# level). The block-final "En general" summary item is NOT pinned by route 7
# here: its corrected item-total r (.753) is second, behind item 4 (.755), and
# its mean (5.268) is third, behind items 2 (5.333) and 5 (5.279) -- unlike the
# empl_stab block, where the summary item topped both. Route D separates the two
# "special programmes for women and minorities" items from the three "equal
# treatment / non-discrimination" items, but cannot order within either group
# (4.2/4.5/4.6 span only 0.065). Hence PARTIAL, not VERIFIED.
#
# irw_fetch() is used deliberately: this table is 2,597 rows (~120 KB), so the
# export cost is negligible, and per item x level counts cannot be had from
# irw_table_sets().

suppressMessages(library(irw))
TABLE <- "avilatamayo_2022_workf_div"
ITEMS <- paste0("Workf_Div_4.", 1:6, "_1")

# --- source: the study's own S1 Dataset (.sav), fetched fresh -----------------
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0266711.s001")
tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
cat("S1 Dataset sha256:", as.character(tools::sha256sum(tmp)), "\n")
cat("expected           329b550875b3e6b29e2d454a3a776e229f1bc05ac1c9bf2c07f7db879aea6662\n\n")
sav <- haven::read_sav(tmp)
raw <- as.data.frame(sav[, ITEMS]); raw[] <- lapply(raw, as.numeric)
contract <- as.numeric(sav[["Type_of_contract"]])   # 1 = Full-time, 2 = Contingent

# --- live --------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# --- A. route 9: item x level cell counts ------------------------------------
cat("=== A. item x response-level counts: S1 .sav vs live IRW table ===\n")
cat(sprintf("%-18s %-5s %8s %8s\n", "item", "resp", "sav", "live"))
bad <- 0
for (it in ITEMS) {
    sv <- raw[[it]]; sv <- sv[!is.na(sv) & sv %in% 1:7]   # mean-imputed non-integers dropped
    lv <- d$resp[d$item == it]
    for (k in 1:7) {
        a <- sum(sv == k); b <- sum(lv == k)
        cat(sprintf("%-18s %-5d %8d %8d%s\n", it, k, a, b,
                    if (a != b) "   <-- MISMATCH" else ""))
        if (a != b) bad <- bad + 1
    }
}
cat(sprintf("\nmismatched cells: %d of 42\n\n", bad))

# --- live wide matrix ---------------------------------------------------------
ids <- sort(unique(d$id))
m <- matrix(NA_real_, nrow = length(ids), ncol = length(ITEMS),
            dimnames = list(as.character(ids), ITEMS))
m[cbind(match(d$id, ids), match(d$item, ITEMS))] <- d$resp

# --- B. route 3: published subscale statistics --------------------------------
cat("=== B. Workforce-diversity composite vs paper Table 1 ===\n")
mc <- m[complete.cases(m), , drop = FALSE]
comp <- rowMeans(mc); k <- ncol(mc)
alpha <- k/(k-1) * (1 - sum(apply(mc, 2, var)) / var(rowSums(mc)))
PUB <- c(M = 4.91, SD = 1.32, alpha = 0.89)
obs <- c(M = mean(comp), SD = sd(comp), alpha = alpha)
for (nm in names(PUB))
    cat(sprintf("%-6s published %6.2f   observed %8.4f   diff %8.4f\n",
                nm, PUB[[nm]], obs[[nm]], obs[[nm]] - PUB[[nm]]))
ok_b <- all(abs(obs - PUB) < 0.015)
cat(sprintf("n complete cases: %d  (one mean-imputed cell on item 4.1 dropped upstream)\n\n",
            nrow(mc)))

# --- C. route 3-bis: published means by contract type -------------------------
cat("=== C. composite by contract type vs paper Table 3 ===\n")
sav_comp <- rowMeans(raw)                       # .sav rows, in .sav order
g1 <- sav_comp[contract == 1]; g2 <- sav_comp[contract == 2]
tt <- t.test(g1, g2, var.equal = TRUE)
cat(sprintf("Full-time   published 5.11   observed %.3f  (n = %d)\n", mean(g1), length(g1)))
cat(sprintf("Fixed-term  published 4.66   observed %.3f  (n = %d)\n", mean(g2), length(g2)))
cat(sprintf("t-value     published 3.61   observed %.3f\n\n", unname(tt$statistic)))
ok_c <- abs(mean(g1) - 5.11) < 0.01 && abs(mean(g2) - 4.66) < 0.01 &&
        abs(unname(tt$statistic) - 3.61) < 0.02

# --- D. route 8: per-item means vs content ------------------------------------
cat("=== D. per-item means and corrected item-total r (live) ===\n")
mu  <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
tot <- rowSums(mc)
r   <- sapply(ITEMS, function(it) cor(mc[, it], tot - mc[, it]))
lab <- c("a very good action plan supporting equal opportunities",
         "very good anti-discrimination policies (gender, pregnancy, disability, ethnicity)",
         "specialized staff development programmes for women and minorities",
         "stands for good policies to support women and minorities",
         "treats all employees equally, fairly and with respect regardless of gender/ethnicity",
         "OVERALL: gives all employees the same chances in every situation")
for (i in 1:6) cat(sprintf("%-18s mean %6.3f  item-rest r %5.3f  %s\n",
                           ITEMS[i], mu[i], r[i], lab[i]))
cat(sprintf("\nThe two 'targeted programmes for women and minorities' items (4.3, 4.4) sit at\n"))
cat(sprintf("%.3f and %.3f; the three 'equal treatment / non-discrimination' items (4.2, 4.5,\n",
            mu[3], mu[4]))
cat(sprintf("4.6) sit at %.3f / %.3f / %.3f -- a spread of only %.3f, so this route cannot\n",
            mu[2], mu[5], mu[6], max(mu[c(2,5,6)]) - min(mu[c(2,5,6)])))
cat("order them. The block-final summary item 4.6 is NOT the block maximum on either\n")
cat("mean or item-rest r, so route 7 does not pin it either.\n\n")

cat("Establishes: the 1..7 anchors attach to resp in the source's own order (A, 42/42\n")
cat("cells), and these six codes are the published Workforce-diversity subscale stored\n")
cat("raw rather than reverse-scored (B and C both reproduce published values).\n")
cat("Does NOT establish the order of the six item texts within the subscale.\n")

cat(if (bad == 0 && ok_b && ok_c) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
