<div align="center">

# Gemini response usage accounting

Design note

</div>

Updated 17 November 2026. Earlier study records may undercount provider usage: the client previously discarded token metadata when a response was rejected before completion, and the goal compiler also discarded metadata for invalid returned weights. The earlier reports retain that limitation; the missing values cannot be reconstructed from their logs.

The client now extracts nonnegative integer input, candidate-output, thinking and total token counts from a parsed response before checking the candidate's finish reason. Rejected parsed responses carry available counts with the sanitized error; both the repair advisor and goal compiler record them when retrying or falling back. Invalid returned goal weights also retain available counts. Unexpected metadata fields, negative values and booleans are excluded. The status string and existing retry and fallback rules remain unchanged, and response bodies and credentials are not recorded as usage.

Google's [response reference](https://ai.google.dev/api/generate-content) distinguishes normal completion from reasons such as reaching the output-token limit. Its [token guidance](https://ai.google.dev/gemini-api/docs/generate-content/tokens) describes separately reported thinking and candidate-output tokens. Counts are included only when supplied in a parseable response. Network errors, HTTP errors, oversized or malformed responses, and omitted metadata can still leave usage unknown; recorded counts are not a verified bill. Actual account charges require the provider's billing records.

Mocked tests cover incomplete responses with usage, rejected weights, retry behavior and transport failures. The full backend suite passed 114 tests. No live provider call was made to test this change.
