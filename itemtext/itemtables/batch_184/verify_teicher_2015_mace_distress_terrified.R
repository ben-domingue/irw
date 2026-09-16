# verify_teicher_2015_mace_distress_terrified.R -- batch_184
#
# Claim being verified. The IRW item codes ARE the Teicher & Parigger (2015) S9 File
# (pone.0117423.s018) column stems (data/teicher_2015_mace_items.py strips "_Terrified").
# The deposit has no text labels, so item_text was tied to codes by:
#   (1) the developer's own MACEscore R package (S7 File, s016) listing the MACE-X
#       variables in instrument order -- the 35 *_Terrified stems there, in order, must
#       be the 35 follow-up-bearing items of the S3 File MACE-X form (s012, items 4-38);
#   (2) the S3 form being a post-collection revision at 4 positions, which the data
#       must show: H_/O_Adults_argue behave as HEARING/OBSERVING arguments (nested), not
#       mother/father (form items 31/32), and Intercourse_sib behaves as ACTUAL
#       intercourse nested in Attempt_sex_sib, not "Threatened to harm your sibling"
#       (form item 25). Those 4 items ship with blank item_text;
#   (3) the self-describing codes for the 31 shipped texts reproducing the severity
#       ladders the wording implies (push > marks > medical attention, etc.).
# Also checks the live table reproduces the S9 Terrified columns per item (n and mean),
# so the codes being verified are the columns being described.
# Does NOT establish: that the S3 wording of the 31 shipped items is character-identical
# to the version administered (the S3 form is a later formatting of the MACE-X), nor any
# wording for the 4 blank items.

suppressMessages(library(irw))
TABLE <- "teicher_2015_mace_distress_terrified"
ok <- TRUE
chk <- function(label, cond) {
  cat(sprintf("  [%s] %s\n", if (isTRUE(cond)) "ok" else "FAIL", label))
  if (!isTRUE(cond)) ok <<- FALSE
}

base <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0117423."
td <- tempfile("mace_"); dir.create(td)
dl <- function(sfx, dest) {
  f <- file.path(td, dest)
  utils::download.file(paste0(base, sfx), f, mode = "wb", quiet = TRUE)
  f
}
raw <- read.csv(dl("s018", "s9.csv"), stringsAsFactors = FALSE, check.names = FALSE)
tgz <- dl("s016", "maces.tar.gz"); utils::untar(tgz, exdir = td)
source(file.path(td, "MACEscore", "R", "mace_x_names.R"))
docx <- dl("s012", "macex.docx"); utils::unzip(docx, files = "word/document.xml", exdir = td)
docxml <- paste(readLines(file.path(td, "word", "document.xml"), warn = FALSE), collapse = "")
docxml <- gsub("<[^>]+>", "", docxml)  # text runs can split a phrase across XML elements

shipped_order <- c("Afraid","Leave","Closet","Pushed","Hit","Hit_med","Spank_open","Spanked_bare",
  "Spanked_strap","Sex_comment","Fondled","Touch_them","Attemp_sex","Intercourse","Push_sib","Hit_sib",
  "Hit_sib_med","Sex_comment_sib","Fondled_sib","Touch_them_sib","Attempt_sex_sib","Intercourse_sib",
  "o_sex_com","o_fondled","o_touch_them","o_attempt_sex","o_intercourse","H_Adults_argue","O_Adults_argue",
  "Adults_push_m","Adults_hit_m","Adults_hit_med_m","Adults_push_f","Adults_hit_f","Adults_hit_med")

cat("== (1) developer name list vs shipped order vs S3 form ==\n")
dev <- sub("_Terrified$", "", grep("_Terrified$", mace_x_names(), value = TRUE))
cat("  developer *_Terrified stems:", length(dev), "\n")
chk("developer MACE-X order of *_Terrified stems == shipped item order (35/35)", identical(dev, shipped_order))
n_prompt <- lengths(regmatches(docxml, gregexpr("helpless or terrified", docxml, fixed = TRUE)))
cat("  S3 form occurrences of 'helpless or terrified':", n_prompt, "\n")
chk("S3 form carries the follow-up prompt on exactly 35 items", n_prompt == 35)
allstems <- sub("_Ever$", "", grep("_Ever$", mace_x_names(), value = TRUE))
pos <- match(shipped_order, allstems)
cat("  positions of the 35 stems in the developer's 75-item list:", paste(range(pos), collapse = "-"), "\n")
chk("the 35 stems are MACE-X items 4..38 contiguous (form items carrying the prompt)", identical(pos, 4:38))

cat("== (2) the 4 positions where the S3 form diverges from the administered version ==\n")
ev <- function(v) suppressWarnings(as.numeric(raw[[v]]))
H <- ev("H_Adults_argue"); O <- ev("O_Adults_argue")
pHgO <- mean(H[O == 1] == 1, na.rm = TRUE); pOgH <- mean(O[H == 1] == 1, na.rm = TRUE)
cat(sprintf("  P(H_argue | O_argue) = %.3f (%d/%d); P(O_argue | H_argue) = %.3f; O without H = %d\n",
            pHgO, sum(H == 1 & O == 1, na.rm = TRUE), sum(O == 1, na.rm = TRUE), pOgH,
            sum(O == 1 & H == 0, na.rm = TRUE)))
m <- ev("Adults_push_m"); f <- ev("Adults_push_f")
cat(sprintf("  cor(H_argue, push_m)=%.3f cor(H_argue, push_f)=%.3f | cor(O_argue, push_m)=%.3f cor(O_argue, push_f)=%.3f\n",
            cor(H, m, use = "p"), cor(H, f, use = "p"), cor(O, m, use = "p"), cor(O, f, use = "p")))
chk("O_Adults_argue nested in H_Adults_argue (>=0.95): hearing/observing, not mother/father",
    pHgO >= 0.95 && pOgH < 0.9)
A <- ev("Attempt_sex_sib"); I <- ev("Intercourse_sib"); HM <- ev("Hit_sib_med")
cat(sprintf("  Attempt_sex_sib %.4f  Intercourse_sib %.4f  Hit_sib_med %.4f ; Intercourse_sib=1 with Attempt=1: %d/%d\n",
            mean(A, na.rm = TRUE), mean(I, na.rm = TRUE), mean(HM, na.rm = TRUE),
            sum(I == 1 & A == 1, na.rm = TRUE), sum(I == 1, na.rm = TRUE)))
chk("Intercourse_sib nested in Attempt_sex_sib (actual within attempted), as Intercourse in Attemp_sex",
    all(A[I == 1 & !is.na(I)] == 1) &&
    all(ev("Attemp_sex")[ev("Intercourse") == 1 & !is.na(ev("Intercourse"))] == 1))
chk("Intercourse_sib rarer than Hit_sib_med (implausible for 'Threatened to harm your sibling')",
    mean(I, na.rm = TRUE) < mean(HM, na.rm = TRUE))

cat("== (3) severity ladders implied by the 31 shipped texts ==\n")
ladder <- function(v) {
  p <- sapply(v, function(x) mean(ev(x), na.rm = TRUE))
  cat("  ", paste(sprintf("%s=%.3f", v, p), collapse = " > "), "\n")
  all(diff(p) < 0)
}
chk("parental push > marks > medical", ladder(c("Pushed", "Hit", "Hit_med")))
chk("sibling push > marks > medical", ladder(c("Push_sib", "Hit_sib", "Hit_sib_med")))
chk("mother push > marks > medical", ladder(c("Adults_push_m", "Adults_hit_m", "Adults_hit_med_m")))
chk("father push > marks > medical", ladder(c("Adults_push_f", "Adults_hit_f", "Adults_hit_med")))
chk("spanked (any) > with object/bare", ladder(c("Spank_open", "Spanked_strap")) && ladder(c("Spank_open", "Spanked_bare")))
chk("non-household: comments > fondled > attempted > actual", ladder(c("o_sex_com", "o_fondled", "o_attempt_sex", "o_intercourse")))
chk("household sexual comment/fondle > attempted > actual", ladder(c("Sex_comment", "Attemp_sex", "Intercourse")))

cat("== live table reproduces S9 *_Terrified columns ==\n")
d <- irw::irw_fetch(TABLE)
rec <- c("0" = 0, "No" = 0, "1" = 1, "Yes" = 1, "yes" = 1)
worst <- 0; nbad <- 0
for (it in shipped_order) {
  r <- unname(rec[as.character(raw[[paste0(it, "_Terrified")]])]); r <- r[!is.na(r)]
  l <- d$resp[d$item == it]
  dm <- abs(mean(l) - mean(r)); worst <- max(worst, dm)
  if (length(l) != length(r) || dm > 1e-12) nbad <- nbad + 1
}
cat(sprintf("  items with n or mean mismatch: %d/35 ; worst |mean diff| = %.2e ; live rows %d\n", nbad, worst, nrow(d)))
chk("all 35 live items reproduce S9 *_Terrified n and mean exactly", nbad == 0)
lv <- tapply(d$resp, d$item, function(x) length(unique(x)))
chk("every item uses both resp levels 0 and 1", all(lv == 2))

cat("\nNote: routes (1)+(3) pin each of the 31 shipped texts to its code; route (2) justifies\n",
    "blanking 4 items. None of this shows the S3 wording is character-identical to what was administered.\n", sep = "")
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
