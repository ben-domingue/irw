##Questions-driven reading of mathematics: comparative judgement of the relevance of text
##sections to a question. Makri, D., & Jones, I. (2026). Investigating Questions Driven
##Reading of Mathematics Data Sets. Loughborough University data repository (figshare),
##doi:10.17028/rd.lboro.31135015.v1 (article 31135015, version 1, published 2026-01-26).
##The deposit refers to "our corresponding paper" without citing it.
##Licence: figshare API for the article, "license": {"name": "CC BY-NC 4.0",
##"url": "https://creativecommons.org/licenses/by-nc/4.0/"}, checked 2026-10-01.
##Non-commercial: hostable under Ben's 10-01 rule; Derived License carries NC (#2688).
##
##Design (record description): undergraduates read text sections presenting and
##explaining parity and periodicity of real functions, "towards answering" a question,
##and judged pairs of sections on "their relevance to a given question" (No More Marking
##comparative judgement). Six sessions, each with its own question and its own judges:
##C1-C3 questions rated by experts as highly conceptual, P1-P3 highly procedural. The
##question numbers come from the deposit's xlsx (sheet names): C1 = Q7L, C2 = Q16L,
##C3 = Q13L, P1 = Q3L, P2 = Q11L, P3 = Q17L.
##
##Each session's 21 sections carry their own random codes (no code is shared between
##sessions), so relevance to one question and to another never share an agent. As with
##other sources whose agent ids are globally unique (quizbowl, chickadees), this is one
##table with the session in `session` and `question_type` (conceptual / procedural); its
##contest graph is six disconnected components. Ben ruled 10-01 (#2688) that comparative
##judgement of texts is a contest with the texts as contestants, relevance included.
##
##One row per decision, in source order. agent_a = chosen section, agent_b = not chosen,
##so winner is always "agent_a" (the source records only the choice). rater = judge (the
##source's anonymised JUDGE-<session>-<n>). date = createdAt (dd/mm/yyyy HH:MM, read as
##UTC) in Unix seconds. time_taken = timeTaken in seconds, as recorded (one C1 value is
##exactly 86,400 s = 24 h, kept). excluded = the source's flag (1/0):
##No More Marking excluded all 25 decisions of one judge, JUDGE-C2-20; they are kept so
##users can choose, and the authors' participant count for C2 (16) includes that judge.
##homefield is blank. The free-text follow-up answers (xlsx) are not used.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/31135015")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
src <- list(C1 = c("61279354", "6d345a0ecf73763a09d031d705aee308"),
            C2 = c("61279357", "dbceb57969031e065b8cf11a360e6053"),
            C3 = c("61279360", "bb1e04e79ad27a238ccd56315c99ce7b"),
            P1 = c("61279363", "00530633dbd18c28bce6086e6e71a74f"),
            P2 = c("61279366", "45b2fdfb430181e219fbc1e63693f008"),
            P3 = c("61279369", "21f495a520af678192211df59aaa9b4a"))
question <- c(C1 = "Q7L", C2 = "Q16L", C3 = "Q13L", P1 = "Q3L", P2 = "Q11L", P3 = "Q17L")
out <- NULL
for (s in names(src)) {
  f <- file.path(cache, paste0("decisions-", s, ".csv"))
  if (!file.exists(f))
    download.file(paste0("https://ndownloader.figshare.com/files/", src[[s]][1]), f, mode = "wb")
  stopifnot(unname(tools::md5sum(f)) == src[[s]][2])
  x <- read.csv(f, check.names = FALSE, stringsAsFactors = FALSE)
  stopifnot(names(x) == c(paste0("judge-", s, "-ID"), "timeTaken", "chosen", "notChosen",
                          "createdAt", "excluded"),
            x$chosen != x$notChosen, x$excluded %in% c(TRUE, FALSE))
  out <- rbind(out, data.frame(
    agent_a = x$chosen, agent_b = x$notChosen,
    date = as.numeric(as.POSIXct(x$createdAt, format = "%d/%m/%Y %H:%M", tz = "UTC")),
    homefield = "", winner = "agent_a", rater = x[[1]],
    session = s, question = question[[s]],
    question_type = if (substr(s, 1, 1) == "C") "conceptual" else "procedural",
    time_taken = x$timeTaken / 1000, excluded = as.integer(x$excluded)))
}
stopifnot(!anyNA(out$date), !anyNA(out$time_taken),
          nrow(out) == 1948, sum(out$excluded) == 25,
          all(tapply(c(out$agent_a, out$agent_b), rep(out$session, 2),
                     function(v) length(unique(v))) == 21),
          length(unique(c(out$agent_a, out$agent_b))) == 126)
fn <- "makri_2026_mathtext_relevance.csv"
write.csv(out, fn, row.names = FALSE, na = "")
cat(fn, nrow(out), "decisions,", length(unique(c(out$agent_a, out$agent_b))), "sections,",
    length(unique(out$rater)), "judges\n")
