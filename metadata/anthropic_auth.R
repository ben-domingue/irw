## Anthropic credentials for 02_biblio.R's BibTeX fallback.
##
## Two paths, resolved in this order:
##
##   1. `ANTHROPIC_API_KEY` -- a static key, sent as `x-api-key`. The local
##      path; Ben's laptop keeps it in ~/.config/irw/anthropic.env.
##   2. Workload Identity Federation -- no static secret anywhere. The GitHub
##      Actions job presents the run's own OIDC token and exchanges it for a
##      short-lived Anthropic token (`sk-ant-oat01-...`), sent as
##      `Authorization: Bearer`. See .github/workflows/metadata-pipeline.yml.
##
## The key is checked first because that is the order every Anthropic SDK
## resolves credentials in, and matching it keeps this file unsurprising. The
## consequence is that CI must NOT set `ANTHROPIC_API_KEY`: a key in the
## environment silently shadows federation, so the federation variables would
## be dead configuration and the static secret would still be the thing in use.
##
## Why any of this is written out by hand: every Anthropic SDK does the
## exchange and the refresh loop for you, and there is no R SDK. Two properties
## of the exchange shape the code below.
##
##   - A minted token lives the LESSER of the federation rule's
##     `token_lifetime_seconds` and twice the remaining life of the presented
##     JWT. GitHub's JWTs expire in ~5 minutes, so a minted token is good for
##     ~10 whatever the rule says. 02_biblio.R is 8th of 17 stages in a run
##     that has taken 117 minutes, so a single exchange at job start cannot
##     carry the stage -- the token is minted on first use and re-minted
##     mid-loop when it ages out.
##   - GitHub JWTs carry a `jti` and are single-use. Every exchange therefore
##     fetches a FRESH JWT from `ACTIONS_ID_TOKEN_REQUEST_URL` (which stays
##     valid for the whole job) rather than re-reading one file written at job
##     start, which would be rejected as `jti_reused` on the second exchange.

library(httr)
library(jsonlite)

## Minted token + its expiry, cached across calls within one stage.
.anthropic_token_cache <- new.env(parent = emptyenv())

anthropic_federation_configured <- function() {
  all(nzchar(Sys.getenv(c(
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
    "ANTHROPIC_SERVICE_ACCOUNT_ID"
  ))))
}

## A JWT for this workload, fresh on every call (see the jti note above).
.anthropic_identity_token <- function() {
  req_url <- Sys.getenv("ACTIONS_ID_TOKEN_REQUEST_URL")
  req_token <- Sys.getenv("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
  if (nzchar(req_url) && nzchar(req_token)) {
    ## `audience` must equal the federation rule's configured audience.
    response <- GET(
      paste0(req_url, "&audience=https%3A%2F%2Fapi.anthropic.com"),
      add_headers(Authorization = paste("Bearer", req_token))
    )
    if (status_code(response) != 200) {
      stop("GitHub OIDC token request failed (HTTP ", status_code(response), "): ",
           content(response, as = "text", encoding = "UTF-8"))
    }
    jwt <- content(response, as = "parsed")$value
    if (is.null(jwt) || !nzchar(jwt)) stop("GitHub OIDC token request returned no token.")
    return(jwt)
  }
  ## Outside Actions, or in a job that wrote the JWT to a file instead. One
  ## exchange only: a file read twice presents the same jti the second time.
  token_file <- Sys.getenv("ANTHROPIC_IDENTITY_TOKEN_FILE")
  if (nzchar(token_file) && file.exists(token_file)) {
    return(trimws(paste(readLines(token_file, warn = FALSE), collapse = "")))
  }
  stop("Federation is configured but no identity token is available: neither ",
       "ACTIONS_ID_TOKEN_REQUEST_URL (is `id-token: write` granted to the job?) ",
       "nor a readable ANTHROPIC_IDENTITY_TOKEN_FILE.")
}

## Exchange the JWT for an Anthropic access token (RFC 7523 jwt-bearer grant).
.anthropic_exchange_token <- function() {
  body <- list(
    grant_type = "urn:ietf:params:oauth:grant-type:jwt-bearer",
    assertion = .anthropic_identity_token(),
    federation_rule_id = Sys.getenv("ANTHROPIC_FEDERATION_RULE_ID"),
    organization_id = Sys.getenv("ANTHROPIC_ORGANIZATION_ID"),
    service_account_id = Sys.getenv("ANTHROPIC_SERVICE_ACCOUNT_ID")
  )
  ## Required only when the rule covers more than one workspace; sending an
  ## empty string is not the same as omitting the field.
  workspace_id <- Sys.getenv("ANTHROPIC_WORKSPACE_ID")
  if (nzchar(workspace_id)) body$workspace_id <- workspace_id

  response <- POST(
    url = "https://api.anthropic.com/v1/oauth/token",
    content_type_json(),
    encode = "json",
    body = body
  )
  if (status_code(response) != 200) {
    ## A denied exchange is an opaque 401 "Authentication failed" whichever
    ## check failed. The deny reason is on the authentication history tab of
    ## the Console's Workload identity page -- `match_subject_prefix` means the
    ## rule's subject_prefix does not match this run's `sub`.
    stop("Anthropic token exchange failed (HTTP ", status_code(response), "): ",
         content(response, as = "text", encoding = "UTF-8"),
         ". Deny reasons are listed at ",
         "https://platform.claude.com/settings/workload-identity-federation?tab=history")
  }
  parsed <- content(response, as = "parsed")
  if (is.null(parsed$access_token)) stop("Anthropic token exchange returned no access_token.")
  .anthropic_token_cache$token <- parsed$access_token
  ## Refresh 120s before expiry, as the SDKs do: a failed exchange at that
  ## point still leaves a usable token to retry with.
  expires_in <- if (is.null(parsed$expires_in)) 600 else as.numeric(parsed$expires_in)
  .anthropic_token_cache$refresh_at <- Sys.time() + max(expires_in - 120, 30)
  invisible(.anthropic_token_cache$token)
}

## The authorization header for a Messages API request, as a named character
## vector for `add_headers(.headers = ...)`. `force_refresh` re-mints even if
## the cached token looks current -- for retrying a 401.
anthropic_auth_header <- function(force_refresh = FALSE) {
  api_key <- Sys.getenv("ANTHROPIC_API_KEY")
  if (nzchar(api_key)) return(c("x-api-key" = api_key))

  if (anthropic_federation_configured()) {
    stale <- is.null(.anthropic_token_cache$token) ||
      Sys.time() >= .anthropic_token_cache$refresh_at
    if (force_refresh || stale) .anthropic_exchange_token()
    return(c(Authorization = paste("Bearer", .anthropic_token_cache$token)))
  }

  ## Interactive use with neither configured: ask, as this script always has.
  ## Non-interactively `readline()` returns "" and the request 401s, which is
  ## the clearer failure of the two available.
  api_key <- readline("Enter your Anthropic API key: ")
  Sys.setenv(ANTHROPIC_API_KEY = api_key)
  c("x-api-key" = api_key)
}
