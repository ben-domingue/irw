# verify_shi_2025_dass21.R -- Step 5b check for shi_2025_dass21 (batch_171).
#
# CLAIM: IRW item codes item1..item21 carry the canonical DASS-21 item numbering
# (Lovibond & Lovibond 1995), so item_text = canonical item N for itemN.
#
# DERIVATION: data/shi_2025_mindfulness.py is a number-preserving rename
# ({pre,post,third}DASS<N> -> item<N>, wave 0/1/2). The source .sav (PLOS ONE
# 10.1371/journal.pone.0331084.s001) carries NO variable or value labels, so the
# number->wording tie is not stated anywhere in the study's materials.
#
# ROUTE (3, published/stored subscale totals): the same .sav stores the study's
# OWN subscale scores per wave -- <wave>DASS压力 (stress), 焦虑 (anxiety),
# 抑郁 (depression). Summing the live items the canonical DASS-21 key assigns to
# each subscale must reproduce those stored scores for every person x wave.
#   Stress     = 1, 6, 8, 11, 12, 14, 18
#   Anxiety    = 2, 4, 7, 9, 15, 19, 20
#   Depression = 3, 5, 10, 13, 16, 17, 21
# Plus a discrimination check: every one of the 147 single cross-subscale swaps
# of the canonical key must FAIL to reproduce them.
#
# DOES NOT ESTABLISH: the order of the seven items WITHIN a subscale (e.g. that
# item1 is "hard to wind down" rather than stress item 6 "over-react"). That rests
# on the canonical numbering being carried through the column suffixes. Nor
# anything about option_text, which ships blank.

suppressMessages({ library(irw); library(haven) })

TABLE <- "shi_2025_dass21"
URL <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0331084.s001"
KEY <- list(S = c(1, 6, 8, 11, 12, 14, 18), A = c(2, 4, 7, 9, 15, 19, 20), D = c(3, 5, 10, 13, 16, 17, 21))
SUBCOL <- c(S = "压力", A = "焦虑", D = "抑郁")
WAVES <- c("pre", "post", "third")

d <- irw::irw_fetch(TABLE)
d <- as.data.frame(d)
tf <- tempfile(fileext = ".sav")
download.file(URL, tf, mode = "wb", quiet = TRUE,
              headers = c("User-Agent" = "IRW-Finder/1.0 (ben.domingue@gmail.com)"))
src <- as.data.frame(haven::read_sav(tf))
names(src)[names(src) == "编号"] <- "id"
cat(sprintf("live rows %d, source persons %d\n", nrow(d), nrow(src)))

ok <- TRUE

# (a) live resp == source column value, cell for cell (ties itemN to <wave>DASS<N>)
agree <- 0; total <- 0
for (w in 0:2) for (i in 1:21) {
    lv <- d[d$wave == w & d$item == paste0("item", i), c("id", "resp")]
    sv <- src[, c("id", paste0(WAVES[w + 1], "DASS", i))]
    mm <- merge(lv, sv, by = "id")
    total <- total + nrow(mm)
    agree <- agree + sum(mm$resp == mm[[3]])
}
cat(sprintf("(a) live resp vs source column <wave>DASS<N>: %d / %d cells agree\n", agree, total))
if (agree != total || total != 196 * 3 * 21) ok <- FALSE

# wide live matrix per wave
wide <- function(w) {
    x <- d[d$wave == w, c("id", "item", "resp")]
    r <- reshape(x, idvar = "id", timevar = "item", direction = "wide")
    names(r) <- sub("^resp\\.", "", names(r))
    merge(r, src[, c("id", paste0(WAVES[w + 1], "DASS", SUBCOL))], by = "id")
}
score <- function(W, key, w) {
    sapply(names(key), function(k) {
        s <- rowSums(W[, paste0("item", key[[k]]), drop = FALSE])
        sum(s == W[[paste0(WAVES[w + 1], "DASS", SUBCOL[[k]])]])
    })
}

# (b) canonical key reproduces the study's own stored subscale scores
cat("\n(b) canonical key vs study's stored subscale scores (exact matches / persons)\n")
Ws <- lapply(0:2, wide)
for (w in 0:2) {
    s <- score(Ws[[w + 1]], KEY, w)
    cat(sprintf("  wave %d (%s): stress %d/%d  anxiety %d/%d  depression %d/%d\n", w, WAVES[w + 1],
                s["S"], nrow(Ws[[w + 1]]), s["A"], nrow(Ws[[w + 1]]), s["D"], nrow(Ws[[w + 1]])))
    if (any(s != nrow(Ws[[w + 1]])) || nrow(Ws[[w + 1]]) != 196) ok <- FALSE
}

# (c) discrimination: every single cross-subscale swap must fail somewhere
n_swaps <- 0; n_survive <- 0; best <- 0
for (a in c("S", "A", "D")) for (b in c("S", "A", "D")) if (a < b) {
    for (p in KEY[[a]]) for (q in KEY[[b]]) {
        k2 <- KEY; k2[[a]][k2[[a]] == p] <- q; k2[[b]][k2[[b]] == q] <- p
        m <- sum(sapply(0:2, function(w) sum(score(Ws[[w + 1]], k2, w))))
        best <- max(best, m)
        n_swaps <- n_swaps + 1
        if (m == 196 * 3 * 3) n_survive <- n_survive + 1
    }
}
cat(sprintf("\n(c) single cross-subscale swaps tested: %d; swaps still reproducing all 1764 stored scores: %d; best rival matches %d/1764\n",
            n_swaps, n_survive, best))
if (n_swaps != 147 || n_survive != 0) ok <- FALSE

cat("\nNOT ESTABLISHED: order of items within each 7-item subscale (rests on canonical numbering",
    "carried by the column suffix); option_text<->resp (ships blank).\n")
cat("RESP-CODING NOTE (not a mapping check): live resp by wave --\n")
print(table(wave = d$wave, resp = d$resp))

cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
