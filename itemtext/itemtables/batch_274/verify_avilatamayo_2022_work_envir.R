# Step 5b verification for avilatamayo_2022_work_envir  (batch_274)
#
# mapping_basis = paper_order. The IRW item code IS the SPSS column name
# (data/avilatamayo_2022_csr.py melts by name), and the .sav variable labels
# pin each code to an ORDINAL ("Work environment 1" .. "Work environment 5").
# What is INFERRED is that the k-th row under "Entorno de trabajo" in the S1
# Appendix (which numbers nothing) is item k. This script tests what can be
# tested against numbers:
#
#   A. route 9 -- option_text <-> resp. The .sav stores 1..7 with English value
#      labels; the live table stores 1..7. All 35 item x level cell counts must
#      match, which a flipped or permuted anchor set would break immediately.
#   B. route 3 -- subscale total. The 5 live items composited must reproduce the
#      paper's published Working-environment M / SD / Cronbach's alpha
#      (Table 1: 4.77 / 1.37 / .87). Pins membership and rules out reverse-scoring.
#   C. route 8 -- semantic coherence of the per-item means against item content.
#
# What this does NOT establish: the ORDER of the five item texts within the
# subscale. No per-item statistic is published anywhere in the paper (Fig 2 is a
# second-order path diagram, not per-item loadings), and items 2.3 and 2.4 have
# means 4.907 vs 4.908 -- indistinguishable. Hence PARTIAL, not VERIFIED.
#
# irw_fetch() is used deliberately: this table is 2,162 rows (~100 KB), so the
# export cost is negligible, and per item x level counts cannot be had from
# irw_table_sets().

suppressMessages(library(irw))
TABLE <- "avilatamayo_2022_work_envir"
ITEMS <- paste0("Work_Envir_2.", 1:5, "_1")

# --- source: the study's own S1 Dataset (.sav), fetched fresh -----------------
SAV_URL <- paste0("https://journals.plos.org/plosone/article/file",
                  "?type=supplementary&id=10.1371/journal.pone.0266711.s001")
tmp <- tempfile(fileext = ".sav")
download.file(SAV_URL, tmp, quiet = TRUE, mode = "wb")
cat("S1 Dataset sha256:", as.character(tools::sha256sum(tmp)), "\n")
cat("expected           329b550875b3e6b29e2d454a3a776e229f1bc05ac1c9bf2c07f7db879aea6662\n\n")
raw <- haven::read_sav(tmp)
raw <- as.data.frame(raw[, ITEMS])
raw[] <- lapply(raw, as.numeric)

# --- live --------------------------------------------------------------------
d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

# --- A. route 9: item x level cell counts ------------------------------------
cat("=== A. item x response-level counts: S1 .sav vs live IRW table ===\n")
cat(sprintf("%-18s %-6s %8s %8s\n", "item", "resp", "sav", "live"))
bad <- 0
for (it in ITEMS) {
    sv <- raw[[it]]
    sv <- sv[!is.na(sv) & sv %in% 1:7]          # the mean-imputed non-integers are dropped
    lv <- d$resp[d$item == it]
    for (k in 1:7) {
        a <- sum(sv == k); b <- sum(lv == k)
        cat(sprintf("%-18s %-6d %8d %8d%s\n", it, k, a, b, if (a != b) "   <-- MISMATCH" else ""))
        if (a != b) bad <- bad + 1
    }
}
cat(sprintf("\nmismatched cells: %d of 35\n\n", bad))

# --- B. route 3: published subscale statistics --------------------------------
cat("=== B. Working-environment composite vs paper Table 1 ===\n")
ids <- sort(unique(d$id))
m <- matrix(NA_real_, nrow = length(ids), ncol = length(ITEMS),
            dimnames = list(as.character(ids), ITEMS))
m[cbind(match(d$id, ids), match(d$item, ITEMS))] <- d$resp
m <- m[complete.cases(m), , drop = FALSE]   # 3 mean-imputed cells were dropped upstream
comp <- rowMeans(m)
k <- ncol(m)
alpha <- k/(k-1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
PUB <- c(M = 4.77, SD = 1.37, alpha = 0.87)
obs <- c(M = mean(comp), SD = sd(comp), alpha = alpha)
for (nm in names(PUB))
    cat(sprintf("%-6s published %6.2f   observed %8.4f   diff %7.4f\n",
                nm, PUB[[nm]], obs[[nm]], obs[[nm]] - PUB[[nm]]))
ok_b <- all(abs(obs - PUB) < 0.015)
cat(sprintf("n complete cases: %d\n\n", nrow(m)))

# --- C. route 8: per-item means vs content ------------------------------------
cat("=== C. per-item means (live) ===\n")
mu <- sapply(ITEMS, function(it) mean(d$resp[d$item == it]))
lab <- c("generic: policies always provide a safe and healthy environment",
         "specific: follows the latest health standards (ergonomic keypads)",
         "maintains and further develops occupational-safety standards",
         "analyses and monitors health and safety risks of its activities",
         "removes psychosocial hazards that contribute to stress and disease")
for (i in 1:5) cat(sprintf("%-18s %6.3f  %s\n", ITEMS[i], mu[i], lab[i]))
cat(sprintf("\nrange %.3f (item 1, the broadest claim) down to %.3f (item 5, the most demanding);\n",
            max(mu), min(mu)))
cat(sprintf("items 2.3 and 2.4 differ by %.4f -- this route cannot separate them.\n\n", abs(mu[3] - mu[4])))

cat("Establishes: the 1..7 anchors attach to resp in the source's own order (A, 35/35 cells),\n")
cat("that these five codes are the published Working-environment subscale and are stored raw,\n")
cat("not reverse-scored (B). Does NOT establish the order of the five item texts within the\n")
cat("subscale: no per-item statistic is published, and two items' means are 0.002 apart.\n")

cat(if (bad == 0 && ok_b) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
