# verify_dulger2024_wordcompletion.R -- Step 5b re-runnable mapping evidence.
#
# WHAT IS BEING VERIFIED
#   item_text is the item code itself (the word fragment), so the item<->text
#   axis is exempt (self-describing codes). The inference this table actually
#   makes is (a) correct_response -- the target word each fragment resolves to,
#   which the study states for only 24 of 60 fragments -- and (b) the option_text
#   direction, i.e. that resp = 1 means the fragment WAS completed correctly.
#
#   (a) is falsifiable: fill each fragment's blanks with the letters the
#       participant actually typed (source .sav column MissingLetters) and ask
#       how often that yields the word we claim. A correct key reproduces the
#       item's live accuracy; a wrong key yields ~0. We also score every item
#       against every OTHER item's claimed word, so the claimed word must be the
#       unique maximum for that item.
#   (b) is falsifiable against the paper: Dulger et al. (2024) report mean
#       word-completion accuracy M = 0.96, SD = 0.07 across participants. If
#       resp were coded 1 = incorrect this would come out at ~0.04.

suppressMessages({library(irw); library(haven)})

TABLE <- "dulger2024_wordcompletion"
SAV   <- "https://osf.io/download/9qrd5/"          # word_completion_coded.sav
PUB_M <- 0.96; PUB_SD <- 0.07                      # paper, Results

# The 24 fragments for which the study's own coding document
# (Coding_examples_word_completion.docx, OSF 384h5) states "correct response =
# <letters>" outright. For these the key is transcribed, not inferred, so the
# accuracy threshold below is not applied to them -- it exists to catch a wrong
# GUESS. hu_ri_d_y is exactly why that distinction matters: the same document
# lists rdl/re/rei/rl/rle/ral as also scored correct, so only ~51% of
# participants typed the letters that spell "hurriedly" literally.
SOURCE_STATED <- c("ac_e_ted","ac_id_nt","acc_d_nt","alo_d","an_o_ing",
  "at_r_ct_ve","br_adly","con__d_nt","con_t_uct_ve","ent_rt_in_ng","excl__ed",
  "hu_ri_d_y","ina_t_nt_ve","irr_spo_s_ble","la_k_ng","lea_n_ng","of__nd_d",
  "re_ect_d","sl_p_y","st_l_sh","ter__bly","und_rst_n_ing","uns_c_essf_l",
  "wh_spe_ing")

items <- read.csv(file.path(dirname(sub("^--file=", "", grep("^--file=",
          commandArgs(FALSE), value = TRUE)[1])),
          paste0(TABLE, "__items.csv")), stringsAsFactors = FALSE)
key <- unique(items[, c("item", "correct_response")])
key <- key[order(key$item), ]

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

tf <- tempfile(fileext = ".sav"); download.file(SAV, tf, quiet = TRUE)
src <- haven::read_sav(tf)
src$frag <- as.character(src$WordFragment)
src$ml   <- tolower(trimws(as.character(src$MissingLetters)))

fill <- function(frag, letters) {
    ch <- strsplit(frag, "")[[1]]; lt <- strsplit(letters, "")[[1]]
    if (sum(ch == "_") != length(lt)) return(NA_character_)
    ch[ch == "_"] <- lt
    sub("\\.$", "", paste(ch, collapse = ""))
}

cat("--- (a) does each claimed target word reproduce that item's live accuracy? ---\n")
cat(sprintf("%-15s %-15s %9s %9s %9s %7s %7s\n",
            "item", "claimed_word", "live_mean", "p_key", "best_other", "uniq", "key"))
bad <- 0
for (i in seq_len(nrow(key))) {
    it <- key$item[i]; w <- key$correct_response[i]
    s  <- src[src$frag == it, ]
    got <- vapply(s$ml, function(l) fill(it, l), character(1))
    p_key  <- mean(got == w, na.rm = TRUE)
    live_m <- mean(d$resp[d$item == it])
    others <- setdiff(key$correct_response, w)
    best_o <- max(c(0, vapply(others, function(o) mean(got == o, na.rm = TRUE), numeric(1))))
    uniq   <- p_key > best_o
    stated <- it %in% SOURCE_STATED
    if (!uniq || (p_key < 0.80 * live_m && !stated)) bad <- bad + 1
    cat(sprintf("%-15s %-15s %9.3f %9.3f %9.3f %7s %7s\n",
                it, w, live_m, p_key, best_o, uniq, ifelse(stated, "stated", "")))
}
cat(sprintf("\nitems failing (non-unique max, or -- for a key this project derived --\n  p_key < 0.80 * live accuracy): %d of %d\n", bad, nrow(key)))
cat("Note: acc_d_nt and ac_id_nt are two different fragments of the same word\n",
    "('accident'), so they cannot be distinguished from each other by this route --\n",
    "but they carry the same claimed correct_response, so no swap is possible.\n", sep = "")

cat("\n--- (b) does resp = 1 mean CORRECT? paper reports M = 0.96, SD = 0.07 ---\n")
pm <- tapply(d$resp, d$id, mean)
cat(sprintf("live per-participant accuracy: M = %.3f, SD = %.3f  (n = %d)\n",
            mean(pm), sd(pm), length(pm)))
cat(sprintf("published:                     M = %.2f, SD = %.2f\n", PUB_M, PUB_SD))
dir_ok <- abs(mean(pm) - PUB_M) < 0.02
cat(sprintf("flipped reading (1 = incorrect) would give M = %.3f\n", 1 - mean(pm)))

cat("\nWhat this does NOT establish: the scenario each fragment terminated is not\n",
    "shipped (never published), so nothing here speaks to scenario wording.\n", sep = "")
cat(if (bad == 0 && dir_ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
