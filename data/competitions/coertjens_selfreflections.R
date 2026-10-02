##Comparative judgement of medical students' written self-reflections (D-PAC platform).
##Coertjens, L., Lesterhuis, M., De Winter, B., Goossens, M., De Maeyer, S., & Michels, N.
##(2021). Improving self-reflection assessment practices: comparative judgment as an
##alternative to rubrics. Teaching and Learning in Medicine, 33(5), 525-535.
##https://doi.org/10.1080/10401334.2021.1877709
##Data: Zenodo record 3746671, doi:10.5281/zenodo.3746671 ("Data assessment
##self-reflections"), file "Data self-reflections_Anonimised.csv".
##Licence: Zenodo API for the record, "license": {"id": "cc-by-4.0"} (CC BY 4.0), checked
##2026-10-01.
##
##Record description: 22 self-reflections by sixth-year medical students "were assessed by
##a group of eight raters using comparative judgement".
##
##One row per comparison, in source order. agent_a = representation A, agent_b =
##representation B (the texts, as the source labels them, e.g. "Zelfreflectie 18");
##winner = whichever is the selected representation (no ties are possible). rater =
##assessor (the source's anonymised number 1-8). date = selected at (dd-mm-yy HH:MM, read
##as UTC) in Unix seconds. comparison (id) and the source's timing and feedback columns are
##kept (select_best_duration, select_best_seq, select_best_seq_duration,
##pros_cons_duration, comparative_feedback_seq, comparative_feedback_seq_duration,
##total_duration). homefield is blank.

cache <- path.expand("~/.cache/irw-comps/discovery-1001/3746671")
dir.create(cache, showWarnings = FALSE, recursive = TRUE)
fn <- "Data self-reflections_Anonimised.csv"
f <- file.path(cache, fn)
if (!file.exists(f))
  download.file(paste0("https://zenodo.org/api/records/3746671/files/", URLencode(fn), "/content"), f, mode = "wb")
stopifnot(unname(tools::md5sum(f)) == "1522e37f0ce6e14fabd66a059548f851")
x <- read.csv(f, sep = ";", check.names = FALSE, stringsAsFactors = FALSE)
stopifnot(nrow(x) == 202,
          x[["selected representation"]] == x[["representation A"]] |
          x[["selected representation"]] == x[["representation B"]])

df <- data.frame(agent_a = x[["representation A"]], agent_b = x[["representation B"]],
                 date = as.numeric(as.POSIXct(x[["selected at"]], format = "%d-%m-%y %H:%M", tz = "UTC")),
                 homefield = "",
                 winner = ifelse(x[["selected representation"]] == x[["representation A"]], "agent_a", "agent_b"),
                 rater = x[["assessor Anonymous"]], comparison = x$comparison,
                 select_best_duration = x[["Select best duration"]],
                 select_best_seq = x[["Select best SEQ"]],
                 select_best_seq_duration = x[["Select best SEQ duration"]],
                 pros_cons_duration = x[["Pros & cons duration"]],
                 comparative_feedback_seq = x[["Comparative feedback SEQ"]],
                 comparative_feedback_seq_duration = x[["Comparative feedback SEQ duration"]],
                 total_duration = x[["total duration"]])
stopifnot(!anyNA(df$date), df$agent_a != df$agent_b)
out <- "coertjens_2021_selfreflections.csv"
write.csv(df, out, row.names = FALSE, na = "")
cat(out, nrow(df), "comparisons,", length(unique(c(df$agent_a, df$agent_b))), "texts,",
    length(unique(df$rater)), "assessors\n")
