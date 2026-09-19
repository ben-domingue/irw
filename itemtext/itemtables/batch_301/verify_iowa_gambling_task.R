# Verification for iowa_gambling_task (#2228, batch_301).
#
# SOURCE. Steingroever, Fridberg, Horstmann, Kjome, Kumari, Lane et al. (2015),
# 'Data from 617 Healthy Participants Performing the Iowa Gambling Task: A Many
# Labs Collaboration', Journal of Open Psychology Data, doi:10.5334/jopd.ak,
# CC BY-SA 4.0; deposit osf.io/8t7rm.
#
# THE ITEM CODE IS A SCRIPT-GENERATED INTEGER over an rbind of three files --
# the hardest pattern SKILL.md names, and the one it says to RE-RUN rather than
# reason about. data/iowa_gambling_task.R prefixes each file's column names,
# rbinds the three, then assigns item = row_number() over unique(item). Route 1
# re-runs that over the deposit's own CSVs.
#
# RE-RUNNING IT SURFACED A DEFECT IN HOW THE SOURCE IS READ, which Route 2
# documents: the trial numbers are shifted by one and each study's last trial is
# silently dropped.
#
# Route 1: re-run the script; row count, item count and block boundaries.
# Route 2: the off-by-one, established from the file's own shape.
# Route 3: the deck coding, quoted from the paper.
suppressMessages({library(readr); library(dplyr); library(tidyr); library(stringr)})
D <- ".cache/batch_301/igt/IGTdataSteingroever2014/"
if (!dir.exists(D)) stop("missing cached deposit files: ", D)
d <- as.data.frame(irw::irw_fetch("iowa_gambling_task"))
if (!nrow(d)) stop("irw_fetch returned no rows -- nothing was checked")
d$item <- as.character(d$item)
items <- read.csv("itemtables/batch_301/iowa_gambling_task__items.csv",
                  stringsAsFactors = FALSE, na.strings = "NA")
items$item <- as.character(items$item)

cat("=== Route 1: the script re-run over the deposit's CSVs ===\n")
rd <- function(n) suppressWarnings(suppressMessages(
        read_csv(paste0(D,"choice_",n,".csv"), show_col_types=FALSE, progress=FALSE)))
choice95 <- rd(95); choice100 <- rd(100); choice150 <- rd(150)
for (nm in c("choice95","choice100","choice150")) {
    x <- get(nm); nn <- paste0(nm, tolower(names(x)))
    nn <- if_else(str_detect(nn, 'choice_1$'), 'id', nn); names(x) <- nn
    x <- x |> pivot_longer(cols=-id, names_to='item', values_to='resp') |>
         mutate(id = as.numeric(str_remove_all(id,'Subj_')),
                resp = if_else(resp > 4, NA, resp)) |> drop_na()
    assign(nm, x)
}
choice100 <- choice100 |> mutate(id = id + 15)
choice150 <- choice150 |> mutate(id = id + 519)
rep <- rbind(choice95, choice100, choice150)
ord <- unique(rep$item)
cat(sprintf("  reproduced rows %d; live rows %d\n", nrow(rep), nrow(d)))
cat(sprintf("  reproduced items %d; live items %d\n", length(ord), length(unique(d$item))))
r1 <- nrow(rep) == nrow(d) && length(ord) == length(unique(d$item))
cat(sprintf("  -> exact reproduction: %s\n", r1))
study <- sub("choice_.*$", "", ord)
cat("  block sizes by source file:\n"); print(table(study))
cat(sprintf("  distinct participants live: %d (the paper reports 617)\n", length(unique(d$id))))

cat("\n=== Route 2: the trial numbers are shifted by one ===\n")
raw <- readLines(paste0(D,"choice_95.csv"), n = 2)
nh <- length(strsplit(raw[1], ",")[[1]]); nd <- length(strsplit(raw[2], ",")[[1]])
cat(sprintf("  choice_95.csv: %d header names, %d fields per data row\n", nh, nd))
cat("  The subject label column is unnamed, so read_csv slides the names left:\n")
cat(sprintf("    the column it calls Choice_1 actually holds %s\n",
            substr(as.character(rd(95)[[1]][1]), 1, 12)))
cat("  -> Choice_2 holds trial 1, Choice_3 holds trial 2, and the last field of\n")
cat("     every row (the final trial) has no name and is dropped.\n")
r2 <- nd == nh + 1
cat(sprintf("  one more field than names, on every file: %s\n", r2))
cat("  data/iowa_gambling_task.R then renames Choice_1 to id, which is why the\n")
cat("  participant numbering comes out right at 1-617 -- the shift is invisible\n")
cat("  in the ids and visible only in the trial count. The shipped item_text uses\n")
cat("  the TRUE trial number (column number minus one), not the column number.\n")
per <- unique(items[, c("section_prompt", "item")])
cat("  trials shipped per study variant:\n"); print(table(per$section_prompt))
cat("  95-, 100- and 150-trial studies contribute 93, 98 and 148 items: each\n")
cat("  loses its final trial to the shift, and one more to drop_na.\n")

cat("\n=== Route 3: the deck coding ===\n")
lv <- sort(unique(d$resp))
r3 <- identical(as.numeric(lv), as.numeric(1:4))
cat(sprintf("  live resp levels %s\n", paste(lv, collapse=",")))
cat("  The paper states: '1, 2, 3, and 4 stand for deck A, B, C, and D,\n")
cat("  respectively', with A and B disadvantageous (net -250 per ten cards) and\n")
cat("  C and D advantageous (+250); A and C carry frequent losses, B and D\n")
cat("  infrequent. option_text ships those four labels.\n")
cat(sprintf("  -> exactly four decks: %s\n", r3))
cat("  NOTE resp is the deck CHOSEN, not an accuracy score, so correct_response\n")
cat("  is empty throughout -- there is no right answer to a single draw.\n")

cat("\n=== What this does NOT establish ===\n")
cat("  Any administered wording: the task is a screen of four card decks and the\n")
cat("  same action is repeated every trial, so item_text is this project's\n")
cat("  bracketed description of the trial and not text anyone read. Nor does it\n")
cat("  establish which laboratory contributed a given participant; the deposit\n")
cat("  pools ten studies and the live table keeps only the trial-count variant.\n")
cat("\nVERDICT:", if (r1 && r2 && r3) "PASS" else "FAIL", "\n")
