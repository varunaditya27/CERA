<div align="center">

# Screen-reader listening review

A task sheet for a person who uses a screen reader

</div>

Automated checks (axe-core, a keyboard Tab walk, the AT-SPI accessibility tree and Orca page titles) pass. They cannot say whether the pages make sense when read aloud. This review needs a person using NVDA, JAWS, Orca or VoiceOver with their usual settings.

## Setup

Follow the [demo walkthrough](demo.md) to start both servers. Use a current Chrome, Firefox or Safari with your own screen reader. Note the screen reader, its version, the browser and the operating system.

## Tasks

For each task, record whether it could be done without sighted help, how long it took, and anything confusing, missing or read twice.

1. Reach the main content from the top of any page, using the skip link.
2. On Datasets, find the dataset with the most variants, and open its details.
3. On Results, read the primary-study chart and its table. Say whether the chart adds anything beyond the table when heard, and whether the table can be navigated by row and column.
4. On Predict, enter an Amylase sequence (the demo guide gives one), submit, and find the predicted score and its range.
5. On Experiments, choose a dataset, set a seed, choose a search method and run it. Say whether the progress and the finished result were announced.
6. Open the run review, open the first batch, and read its table of measurements.
7. Run the decision check and say whether the outcome was clear.
8. On Goals, read the warning about sending text to Google before submitting.

## What to report

Findings as a list, each with the page, what you heard, what you expected and how severe it was (blocks a task, slows it, or minor). Also say what worked well. File them as issues or send them to the authors; the authors will fix and re-run the automated checks.
