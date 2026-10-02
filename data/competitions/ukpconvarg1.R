##UKPConvArg1: crowdsourced pairwise judgements of argument convincingness (MTurk, 2016).
##Habernal, I., & Gurevych, I. (2016). Which argument is more convincing? Analyzing and
##predicting convincingness of Web arguments using bidirectional LSTM. Proceedings of the
##54th Annual Meeting of the ACL (Volume 1: Long Papers), 1589-1599.
##https://doi.org/10.18653/v1/P16-1150
##Data: https://github.com/UKPLab/acl2016-convincing-arguments, pinned to commit
##ca9d24e41b8805ff2e1d3585d552b49bb64a65f7, folder data/UKPConvArg1-full-XML (32 files, the
##full corpus, "Table 2, UKPConvArgAll").
##Licence: README.md, "The data are licensed under CC-BY (Creative Commons Attribution 4.0
##International License)." (checked 2026-10-01). The README adds that the arguments come
##from createdebate.com (CC BY 3.0) and convinceme.net (Creative Commons Public Domain);
##the argument texts are not copied here, only their ids.
##
##Each XML file is one debate and side (e.g. evolution-vs-creation_evolution); arguments
##are only ever compared within their own file. The question is the same everywhere ("which
##argument is more convincing"), argument ids are unique across files, so the corpus is one
##table with the file in `debate`; its contest graph has one component per debate.
##
##One row per MTurk assignment (a single worker's vote on a pair), in file then source
##order. agent_a = arg1 id, agent_b = arg2 id; value "a1" -> "agent_a", "a2" -> "agent_b",
##"equal" -> "draw". rater = turkID re-keyed to an integer (sorted order of the raw ids;
##raw worker ids are not published). date = assignmentSubmitTime in Unix seconds (UTC, as
##the source states). pair_id (the source's "<arg1>_<arg2>"), hit_id and worker_stance
##("opposite", "same" or "none") are kept. The workers' free-text reasons, MACE competence
##scores and the estimated gold label are not kept. homefield is blank.

library(xml2)
cache <- path.expand("~/.cache/irw-comps/discovery-1001/ukp")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
sha <- "ca9d24e41b8805ff2e1d3585d552b49bb64a65f7"
tgz <- file.path(cache, paste0(sha, ".tar.gz"))
if (!file.exists(tgz))
  download.file(paste0("https://codeload.github.com/UKPLab/acl2016-convincing-arguments/tar.gz/", sha), tgz, mode = "wb")
untar(tgz, exdir = cache)
dir <- file.path(cache, paste0("acl2016-convincing-arguments-", sha), "data", "UKPConvArg1-full-XML")
files <- sort(list.files(dir, pattern = "\\.xml$", full.names = TRUE))
stopifnot(length(files) == 32)

rows <- lapply(files, function(f) {
  pairs <- xml_find_all(read_xml(f), "/list/annotatedArgumentPair")
  do.call(rbind, lapply(pairs, function(p) {
    m <- xml_find_all(p, "./mTurkAssignments/mTurkAssignment")
    txt <- function(path) xml_text(xml_find_first(m, path))
    data.frame(a1 = xml_text(xml_find_first(p, "./arg1/id")), a2 = xml_text(xml_find_first(p, "./arg2/id")),
               pair_id = xml_text(xml_find_first(p, "./id")),
               turk = txt("./turkID"), hit_id = txt("./hitID"), submit = txt("./assignmentSubmitTime"),
               value = txt("./value"), worker_stance = txt("./workerStance"),
               debate = sub("\\.xml$", "", basename(f)), stringsAsFactors = FALSE)
  }))
})
x <- do.call(rbind, rows)
stopifnot(all(x$value %in% c("a1", "a2", "equal")), !anyNA(x$turk))
workers <- sort(unique(x$turk))

df <- data.frame(agent_a = x$a1, agent_b = x$a2,
                 date = as.numeric(as.POSIXct(sub("\\.0 UTC$", "", x$submit), format = "%Y-%m-%d %H:%M:%S", tz = "UTC")),
                 homefield = "",
                 winner = c(a1 = "agent_a", a2 = "agent_b", equal = "draw")[x$value],
                 rater = match(x$turk, workers), pair_id = x$pair_id, hit_id = x$hit_id,
                 worker_stance = x$worker_stance, debate = x$debate, row.names = NULL)
stopifnot(!anyNA(df$date), df$agent_a != df$agent_b)
out <- "ukpconvarg1_convincingness_2016.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "votes,", length(unique(df$pair_id)), "pairs,", length(unique(c(df$agent_a, df$agent_b))),
    "arguments,", length(workers), "workers,", sum(df$winner == "draw"), "equal\n")
