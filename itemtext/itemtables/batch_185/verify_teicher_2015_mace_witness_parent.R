# verify_teicher_2015_mace_witness_parent.R -- copied from references/verify_template.R
#
# Claim: S9 File column codes (used verbatim as IRW item codes by
# data/teicher_2015_mace_items.py) carry the MACE-X (S3 File) wording of items 33-38:
#   Adults_push_m 33, Adults_hit_m 34, Adults_hit_med_m 35 (mother block)
#   Adults_push_f 36, Adults_hit_f 37, Adults_hit_med 38   (father block)
# with resp 1 = "Yes", 0 = "No". H_Adults_argue / O_Adults_argue ship with BLANK
# item_text because S3 items 31/32 (argue with mother / father) are not what was
# administered (paper: "Hearing and observing adults arguing were eliminated").
#
# Falsifiable predictions:
#  (A) Teicher & Parigger (2015) PLOS ONE Table 10 (image, doi:10.1371/journal.pone.0117423.t010)
#      prints "% Yes" at n = 1051 against each item's wording (MACE-52 numbers 21-25):
#      12.0 / 4.7 / 2.6 / 9.5 / 2.38%. At n = 1051 each printed value's rounding interval
#      admits exactly ONE integer count (126 / 49 / 27 / 100 / 25, all distinct), so the
#      live count of each item must equal its own implied count and no other item's.
#      A swap of any two of the five texts, or a flipped Yes/No, breaks this.
#  (B) Adults_hit_med has no published statistic (not among the paper's "seven considered"
#      items). If it is "hit your FATHER ... medical attention", its endorsers must sit
#      inside the father block (push_f, hit_f) more than the mother block, and it must be the
#      rarest step of the father severity ladder. Adults_hit_med_m must show the mirror
#      pattern.
#  (C) The blanks: if H/O were "argue with mother / father" they would not nest; if they are
#      hearing / observing, O=1 should nearly imply H=1.

suppressMessages(library(irw))
TABLE <- "teicher_2015_mace_witness_parent"
N_PAPER <- 1051

d <- as.data.frame(irw::irw_fetch(TABLE))
w <- reshape(d[, c("id", "item", "resp")], idvar = "id", timevar = "item", direction = "wide")
names(w) <- sub("^resp\\.", "", names(w))
cnt <- sapply(split(d$resp, d$item), function(r) sum(r == 1))
nn  <- sapply(split(d$resp, d$item), length)
ok <- TRUE

## (A) Table 10 exact-count match
PUB <- c(Adults_push_m = 12.0, Adults_hit_m = 4.7, Adults_hit_med_m = 2.6,
         Adults_push_f = 9.5, Adults_hit_f = 2.38)
DEC <- c(1, 1, 1, 1, 2)
implied <- function(p, dec) { h <- 0.5 * 10^-dec
  k <- ceiling((p - h) / 100 * N_PAPER):floor((p + h) / 100 * N_PAPER - 1e-9); k }
cat("(A) Table 10 % Yes (n=1051) vs live counts\n")
cat(sprintf("%-18s %6s %9s %10s %9s %8s  %s\n", "item", "n", "published", "implied k", "live k", "live %", "items whose live k fits"))
for (i in seq_along(PUB)) {
  it <- names(PUB)[i]; k <- implied(PUB[i], DEC[i])
  fits <- names(cnt)[cnt %in% k]
  cat(sprintf("%-18s %6d %9s %10s %9d %8.2f  %s\n", it, nn[[it]], sprintf("%.*f", DEC[i], PUB[i]),
              paste(k, collapse = "/"), cnt[[it]], 100 * cnt[[it]] / nn[[it]], paste(fits, collapse = ",")))
  if (nn[[it]] != N_PAPER || !identical(fits, it)) ok <- FALSE
}
flip <- 100 * (nn[names(PUB)] - cnt[names(PUB)]) / nn[names(PUB)]
cat(sprintf("flipped-direction %%Yes would be: %s\n", paste(sprintf("%.1f", flip), collapse = " / ")))

## (B) Adults_hit_med / Adults_hit_med_m block membership and severity ladder
pr <- function(a, given) { g <- w[[given]] == 1; c(sum(w[[a]][g] == 1), sum(g)) }
show <- function(a, given) { x <- pr(a, given); sprintf("%d/%d", x[1], x[2]) }
cat("\n(B) Nesting of the medical-attention items\n")
cat("  Adults_hit_med endorsers:   push_f", show("Adults_push_f", "Adults_hit_med"),
    " hit_f", show("Adults_hit_f", "Adults_hit_med"),
    " | push_m", show("Adults_push_m", "Adults_hit_med"),
    " hit_m", show("Adults_hit_m", "Adults_hit_med"), "\n")
cat("  Adults_hit_med_m endorsers: push_m", show("Adults_push_m", "Adults_hit_med_m"),
    " hit_m", show("Adults_hit_m", "Adults_hit_med_m"),
    " | push_f", show("Adults_push_f", "Adults_hit_med_m"),
    " hit_f", show("Adults_hit_f", "Adults_hit_med_m"), "\n")
cat("  r(hit_med, hit_f) =", round(cor(w$Adults_hit_med, w$Adults_hit_f), 2),
    " r(hit_med, hit_med_m) =", round(cor(w$Adults_hit_med, w$Adults_hit_med_m), 2),
    " r(hit_med, hit_m) =", round(cor(w$Adults_hit_med, w$Adults_hit_m), 2), "\n")
cat("  ladders (counts): father push_f", cnt[["Adults_push_f"]], "> hit_f", cnt[["Adults_hit_f"]],
    "> hit_med", cnt[["Adults_hit_med"]], "; mother push_m", cnt[["Adults_push_m"]],
    "> hit_m", cnt[["Adults_hit_m"]], "> hit_med_m", cnt[["Adults_hit_med_m"]], "\n")
p <- function(a, g) { x <- pr(a, g); x[1] / x[2] }
b_ok <- p("Adults_push_f", "Adults_hit_med") > p("Adults_push_m", "Adults_hit_med") &&
        p("Adults_hit_f",  "Adults_hit_med") > p("Adults_hit_m",  "Adults_hit_med") &&
        p("Adults_push_m", "Adults_hit_med_m") > p("Adults_push_f", "Adults_hit_med_m") &&
        p("Adults_hit_m",  "Adults_hit_med_m") > p("Adults_hit_f",  "Adults_hit_med_m") &&
        cor(w$Adults_hit_med, w$Adults_hit_f) > cor(w$Adults_hit_med, w$Adults_hit_med_m) &&
        cnt[["Adults_push_f"]] > cnt[["Adults_hit_f"]] && cnt[["Adults_hit_f"]] > cnt[["Adults_hit_med"]] &&
        cnt[["Adults_push_m"]] > cnt[["Adults_hit_m"]] && cnt[["Adults_hit_m"]] > cnt[["Adults_hit_med_m"]] &&
        p("Adults_hit_f", "Adults_hit_med") >= 0.9
cat("  (B) pattern holds:", b_ok, "\n")
if (!b_ok) ok <- FALSE

## (C) The two blank items: hearing vs observing, not mother vs father
cat("\n(C) Arguing items (shipped blank)\n")
cat("  H_Adults_argue =1 among O_Adults_argue =1:", show("H_Adults_argue", "O_Adults_argue"),
    "; O=1 among H=1:", show("O_Adults_argue", "H_Adults_argue"),
    "; %Yes H", sprintf("%.1f", 100 * cnt[["H_Adults_argue"]] / nn[["H_Adults_argue"]]),
    "O", sprintf("%.1f", 100 * cnt[["O_Adults_argue"]] / nn[["O_Adults_argue"]]), "\n")
c_ok <- p("H_Adults_argue", "O_Adults_argue") >= 0.95
cat("  (C) O nested in H (>= 95%):", c_ok, "\n")
if (!c_ok) ok <- FALSE

cat("\nNot established: that the S3 'formatted copy' wording is character-identical to the online\n",
    "form administered (S1/S2 forms print identical wording for items 33-37; item 38 has no\n",
    "second printing). Adults_hit_med is mapped by (B), a data test, since the paper prints no statistic for it.\n",
    "The administered wording of H_/O_Adults_argue is not published; they carry no item_text.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
