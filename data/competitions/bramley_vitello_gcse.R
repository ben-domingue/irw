##Comparative judgement of 150 GCSE English scripts. Bramley, T., & Vitello, S. (2019).
##The effect of adaptivity on the reliability coefficient in adaptive comparative
##judgement. Assessment in Education: Principles, Policy & Practice, 26(1), 43-58.
##https://doi.org/10.1080/0969594X.2017.1418734
##Data: figshare doi:10.6084/m9.figshare.25867039.v1 (version 1), three files
##(Bramley 1a ACJ.csv, Bramley 1b AllvAll.csv, Bramley 2 Random.csv).
##Licence: figshare API for the article, "license": {"name": "CC BY 4.0",
##"url": "https://creativecommons.org/licenses/by/4.0/"}, checked 2026-10-01.
##
##Study labels follow the paper (figshare description): 1a "comparisons are scheduled
##adaptively"; 1b "comparing (nearly) all of a subset of 20 items in a round-robin
##format"; 2 "comparisons are scheduled randomly as well as repeated comparisons of some
##particular pairs". All three judge the same pool of scripts, so they form one table, with
##the study in `study`.
##
##The agents are scripts (the source's item numbers). The source shows "each pairwise
##comparison ... as two rows" and "The second row for each comparison is redundant"; the
##script checks that rows pair up as mirror images and keeps the first of each pair. In
##every first row Win = 1, so agent_a = Item1 is the script judged better and winner is
##always "agent_a". rater = Judge, prefixed by panel because "the judges in 1a and 1b are
##the same, but different to those in 2": "p1_<n>" for studies 1a/1b, "p2_<n>" for study
##2. There is no date. homefield is blank.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/bramley")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
src <- list(`1a` = c("46453336", "62fee228234062badeb822e1a7cd3ed2"),
            `1b` = c("46453339", "d048a0b5ed8cbd2604c9ae31f05baa1c"),
            `2`  = c("46453342", "39570a4704f818173548daab42d2234a"))
out <- NULL
for (st in names(src)) {
  f <- file.path(cache, paste0("f", src[[st]][1], ".csv"))
  if (!file.exists(f))
    download.file(paste0("https://ndownloader.figshare.com/files/", src[[st]][1]), f, mode = "wb")
  stopifnot(unname(tools::md5sum(f)) == src[[st]][2])
  x <- read.csv(f)
  a <- x[seq(1, nrow(x), 2), ]
  b <- x[seq(2, nrow(x), 2), ]
  stopifnot(nrow(a) == nrow(b), a$Judge == b$Judge, a$Item1 == b$Item2, a$Item2 == b$Item1,
            a$Win + b$Win == 1, a$Win == 1, a$Item1 != a$Item2)
  out <- rbind(out, data.frame(agent_a = a$Item1, agent_b = a$Item2, homefield = "",
                               winner = "agent_a",
                               rater = paste0(if (st == "2") "p2_" else "p1_", a$Judge),
                               study = st))
}
fn <- "bramley_vitello_2019_gcse.csv"
write.csv(out, fn, row.names = FALSE, na = "")
cat(fn, nrow(out), "comparisons,", length(unique(c(out$agent_a, out$agent_b))), "scripts,",
    length(unique(out$rater)), "judges\n")
