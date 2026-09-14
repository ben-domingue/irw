# Step 5b mapping verification for ly_2021_animal_empathy.
#
# The claim under test: item = <VIDEO_ID><exemplar>_<Emotion>, where the video
# code is the code that Ly & Weary's own S1 File ("Ly & Weary interview
# statements") labels with the procedure blurb shipped as section_prompt, and
# the emotion suffix is the S3 File's own rating column name shipped as
# item_text.
#
# Two independent checks:
#  (1) Cell-exact reconstruction. Recompute per-item n and mean directly from
#      the S3 File by grouping on VIDEO_ID x emotion column, and compare with
#      the live table. If the processing script had paired video codes with the
#      wrong emotion column (or shifted the video labels), the 140 pairs would
#      not reconcile. This ties every live item code to a specific source cell
#      block, i.e. to a specific (video, emotion) pair.
#  (2) Falsifiable content prediction from the S1 blurbs. S1 describes CB/CC/CD
#      and PC/PD/PT as painful procedures (branding, band castration,
#      disbudding, surgical castration, tail docking, teeth clipping) and
#      CN/CR/PN/PR as controls (standing / restraint). If the blurb-to-code
#      assignment shipped in section_prompt were wrong, self-reported Pain would
#      not separate those two groups. Require complete separation: every
#      procedure code's mean Pain above every control code's.
#
# What this does NOT establish: it cannot distinguish one painful procedure from
# another statistically (branding vs disbudding); that distinction rests on the
# explicit code labels in S1, which check (1) shows are the same codes the data
# carries. The "1"/"2" exemplar digit is copied verbatim from the S3 VIDEO_ID
# value and the two exemplars of a code share identical shipped text, so no
# exemplar-level inference was made.

suppressMessages(library(irw))

TABLE <- "ly_2021_animal_empathy"
S3 <- "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0247808.s003"
EMOTIONS <- c("Pain", "Anger", "Fear", "Disgust", "Sadness", "Happiness", "Surprise")
PROC <- c("CB", "CC", "CD", "PC", "PD", "PT")   # painful, per S1 File
CTRL <- c("CN", "CR", "PN", "PR")               # control, per S1 File

src <- read.csv(S3, stringsAsFactors = FALSE)
long <- do.call(rbind, lapply(EMOTIONS, function(e)
    data.frame(item = paste0(src$VIDEO_ID, "_", e),
               resp = suppressWarnings(as.numeric(src[[e]])))))
long <- long[!is.na(long$resp), ]

d <- irw::irw_fetch(TABLE)
d$resp <- as.numeric(d$resp)

sm <- tapply(long$resp, long$item, mean); sn <- tapply(long$resp, long$item, length)
lm_ <- tapply(d$resp, d$item, mean);      ln <- tapply(d$resp, d$item, length)
items <- sort(unique(d$item))
stopifnot(setequal(items, names(sm)))
dmean <- max(abs(sm[items] - lm_[items]))
dn    <- max(abs(sn[items] - ln[items]))
cat(sprintf("(1) %d items reconstructed from S3 by VIDEO_ID x emotion column\n", length(items)))
cat(sprintf("    max |mean difference| = %.3e ; max |n difference| = %d\n", dmean, dn))
for (it in head(items, 4))
    cat(sprintf("    %-16s source n=%3d mean=%.4f | live n=%3d mean=%.4f\n",
                it, sn[it], sm[it], ln[it], lm_[it]))

pain <- lm_[paste0(rep(c(PROC, CTRL), each = 2), rep(1:2, 10), "_Pain")]
code <- substr(names(pain), 1, 2)
byc  <- tapply(pain, code, mean)
cat("\n(2) mean self-reported Pain by video code (0-10):\n")
for (k in c(PROC, CTRL))
    cat(sprintf("    %-3s %-9s %.2f\n", k, if (k %in% PROC) "procedure" else "control", byc[[k]]))
sep <- min(byc[PROC]) - max(byc[CTRL])
cat(sprintf("    lowest procedure %.2f (%s) vs highest control %.2f (%s); margin %.2f\n",
            min(byc[PROC]), PROC[which.min(byc[PROC])],
            max(byc[CTRL]), CTRL[which.max(byc[CTRL])], sep))

cat("\nNot established by (2): which painful procedure is which -- that rests on\n",
    "the explicit code labels in the S1 File, confirmed by (1) to be the same codes\n",
    "the data carries.\n", sep = "")

ok <- dmean < 1e-9 && dn == 0 && sep > 0
cat(if (ok) "VERDICT: PASS\n" else "VERDICT: FAIL\n")
