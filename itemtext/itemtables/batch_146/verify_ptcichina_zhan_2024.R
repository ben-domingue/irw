# verify_ptcichina_zhan_2024.R -- Step 5b evidence, re-runnable.
#
# CLAIM UNDER TEST: each live item code ptci1..ptci33 carries the Foa et al.
# (1999) PTCI item whose ORIGINAL number the study's own OSF README assigns to
# it (1-12 identity; 14..31 -> 13..30; 33 -> 31; 35 -> 32; 36 -> 33).
#
# FALSIFIABLE PREDICTION: PTCI_data.sav labels every ptci* column with its
# subscale, and prefixes "b-" on the nine PTCI-9 items. Those labels were written
# by the study against its RENAMED codes and are independent of the README. Foa
# (1999) Appendix B publishes the 36-item subscale key and Wells et al. publish
# the PTCI-9 item set, both against ORIGINAL numbers. If the shipped item_text
# were attached to the wrong code, the six-way class of the shipped sentence
# would disagree with that column's own .sav label.
#
# WHAT THIS DOES NOT ESTABLISH: it pins each item to one of six classes
# (self 18, world 4, blame 2, b-self 3, b-world 3, b-blame 3). It cannot
# distinguish two items inside the same class -- notably the 18 plain "self"
# items. Status is therefore PARTIAL, not VERIFIED.

suppressMessages({library(haven); library(irw)})

TABLE <- "ptcichina_zhan_2024"
ITEMS_CSV <- file.path(dirname(sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])),
                       paste0(TABLE, "__items.csv"))
if (!file.exists(ITEMS_CSV)) ITEMS_CSV <- file.path("itemtables/batch_146", paste0(TABLE, "__items.csv"))

CACHE <- file.path("itemtext/.cache", TABLE)
if (!dir.exists(CACHE)) CACHE <- file.path(".cache", TABLE)
dir.create(CACHE, recursive = TRUE, showWarnings = FALSE)

sav <- file.path(CACHE, "PTCI_data.sav")
if (!file.exists(sav))
  download.file("https://files.osf.io/v1/resources/tj8rh/providers/osfstorage/65800c29513a741d80aed38f",
                sav, quiet = TRUE, mode = "wb")
rme <- file.path(CACHE, "README.txt")
if (!file.exists(rme)) download.file("https://osf.io/download/4bt7v/", rme, quiet = TRUE)

## --- Foa et al. (1999) Appendix A, original numbering (text we shipped) -----
ORIG <- c(
 "1"="The event happened because of the way I acted.",
 "2"="I can't trust that I will do the right thing.",
 "3"="I am a weak person.",
 "4"="I will not be able to control my anger and will do something terrible.",
 "5"="I can't deal with even the slightest upset.",
 "6"="I used to be a happy person but now I am always miserable.",
 "7"="People can't be trusted.",
 "8"="I have to be on guard all the time.",
 "9"="I feel dead inside.",
 "10"="You can never know who will harm you.",
 "11"="I have to be especially careful because you never know what can happen next.",
 "12"="I am inadequate.",
 "14"="If I think about the event, I will not be able to handle it.",
 "15"="The event happened to me because of the sort of person I am.",
 "16"="My reactions since the event mean that I am going crazy.",
 "17"="I will never be able to feel normal emotions again.",
 "18"="The world is a dangerous place.",
 "19"="Somebody else would have stopped the event from happening.",
 "20"="I have permanently changed for the worse.",
 "21"="I feel like an object, not like a person.",
 "22"="Somebody else would not have gotten into this situation.",
 "23"="I can't rely on other people.",
 "24"="I feel isolated and set apart from others.",
 "25"="I have no future.",
 "26"="I can't stop bad things from happening to me.",
 "27"="People are not what they seem.",
 "28"="My life has been destroyed by the trauma.",
 "29"="There is something wrong with me as a person.",
 "30"="My reactions since the event show that I am a lousy coper.",
 "31"="There is something about me that made the event happen.",
 "33"="I feel like I don't know myself anymore.",
 "35"="I can't rely on myself.",
 "36"="Nothing good can happen to me anymore.")

## --- Foa (1999) Appendix B subscale key, ORIGINAL numbers -------------------
SELF  <- c(2,3,4,5,6,9,12,14,16,17,20,21,24,25,26,28,29,30,33,35,36)
WORLD <- c(7,8,10,11,18,23,27)
BLAME <- c(1,15,19,22,31)
## --- PTCI-9 (brief version) item set, ORIGINAL numbers ----------------------
BRIEF <- c(1,7,22,23,25,27,31,33,36)

class_of <- function(o) {
  base <- if (o %in% SELF) "self" else if (o %in% WORLD) "world"
          else if (o %in% BLAME) "blame" else NA_character_
  if (is.na(base)) return(NA_character_)
  if (o %in% BRIEF) paste0("b-", base) else base
}

## --- What we shipped: item_text -> original number --------------------------
it <- read.csv(ITEMS_CSV, stringsAsFactors = FALSE)
shipped <- unique(it[, c("item", "item_text")])
shipped <- shipped[order(as.integer(sub("^ptci", "", shipped$item))), ]
lookup <- setNames(names(ORIG), unname(ORIG))
shipped$orig <- as.integer(lookup[shipped$item_text])

## --- What the .sav says about each code -------------------------------------
d <- read_sav(sav)
sav_label <- sapply(paste0("ptci", 1:33), function(n) {
  l <- attr(d[[n]], "label"); if (is.null(l)) NA_character_ else trimws(l)
})

cat(sprintf("%-8s %6s %-10s %-10s %-6s  %s\n",
            "item", "orig#", "predicted", "sav label", "match", "shipped item_text"))
ok <- logical(nrow(shipped))
for (i in seq_len(nrow(shipped))) {
  code <- shipped$item[i]; o <- shipped$orig[i]
  pred <- if (is.na(o)) NA_character_ else class_of(o)
  obs  <- unname(sav_label[code])
  ok[i] <- !is.na(pred) && !is.na(obs) && identical(pred, obs)
  cat(sprintf("%-8s %6s %-10s %-10s %-6s  %s\n", code,
              ifelse(is.na(o), "??", o), ifelse(is.na(pred), "??", pred),
              ifelse(is.na(obs), "??", obs), ifelse(ok[i], "OK", "MISMATCH"),
              substr(shipped$item_text[i], 1, 62)))
}
cat(sprintf("\nclass agreement: %d/%d items\n", sum(ok), nrow(shipped)))
cat(sprintf("class sizes in the .sav labels: %s\n",
            paste(sprintf("%s=%d", names(table(sav_label)), as.integer(table(sav_label))),
                  collapse = ", ")))

## --- README's own renumbering statement, re-parsed --------------------------
## Each README line is numbered with the NEW code ("13. ptci14 -> ptci13"), so the
## leading ordinal is the target and the arrow's left side is the original number.
txt <- readLines(rme, warn = FALSE)
pat <- "^ *([0-9]+)\\. *ptci([0-9]+) *-> *ptci([0-9]+) *$"
ln <- txt[grepl(pat, txt)]
ord <- as.integer(sub(pat, "\\1", ln))
src <- as.integer(sub(pat, "\\2", ln))
tgt <- as.integer(sub(pat, "\\3", ln))
readme_orig <- rep(NA_integer_, 33)
readme_orig[ord] <- src
bad <- which(ord != tgt)
cat(sprintf("README lines parsed: %d; lines whose arrow target disagrees with their own ordinal: %s\n",
            length(ln), if (length(bad)) paste(sprintf("line %d (%s)", ord[bad], trimws(ln[bad])), collapse = "; ") else "none"))
cat("  (README line 32 reads 'ptci35 -> ptci21'; ptci21 is already the target of line 21\n",
    "   'ptci22 -> ptci21' and 32 is the only unclaimed target, so it is an unambiguous typo for ptci32.)\n", sep = "")
readme_agree <- sum(readme_orig == shipped$orig, na.rm = TRUE)
cat(sprintf("README map vs shipped original numbers: %d/33 agree\n", readme_agree))

## --- live item set (server-side, no export) ---------------------------------
live <- tryCatch(sort(irw::irw_table_sets(TABLE)$item), error = function(e) NULL)
if (!is.null(live))
  cat(sprintf("live item set == shipped item set: %s (%d items)\n",
              identical(sort(unique(it$item)), sort(unique(live))), length(unique(live))))

cat("\nNOT ESTABLISHED: the .sav labels sort items into six classes only\n",
    "(self=18, world=4, blame=2, b-self=3, b-world=3, b-blame=3). A permutation\n",
    "INSIDE a class -- above all among the 18 plain 'self' items -- would pass\n",
    "this test unchanged. That is why the recorded status is PARTIAL.\n", sep = "")

cat(if (all(ok) && readme_agree == 33) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
