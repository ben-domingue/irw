args <- commandArgs(trailingOnly = TRUE)
tables <- args
for (t in tables) {
  gt_file <- paste0(".gt_", gsub("[^A-Za-z0-9_]", "_", t), ".rds")
  if (file.exists(gt_file)) { cat("cached:", t, "\n"); next }
  cat("=====", t, "=====\n")
  df <- tryCatch(irw::irw_fetch(t), error=function(e) {cat("ERROR:", conditionMessage(e), "\n"); NULL})
  if (!is.null(df)) {
    items <- sort(unique(df$item))
    resps <- sort(unique(df$resp))
    cat("N items:", length(items), "\n")
    cat("Items:", paste(items, collapse=" | "), "\n")
    cat("N resp:", length(resps), "\n")
    cat("Resp values:", paste(resps, collapse=", "), "\n")
    saveRDS(df, file=gt_file)
  }
  cat("\n")
}
