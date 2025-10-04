# Data for Determining US Food Regions

The `data` folder has the raw data from several source types for states, which are compared against each other for determining availability in the states. Furthermore, those intermediate results will be compared against each other within the same regions to determine if the food regions outlined by the US Department of Health and Human Services make sense. If the do, food availability will be compared among those regions and assigned. If they do not align, new food region boundaries will be drawn and detailed.

## Data Flow Process:

1) Source data is converted to CSV, JSON, or XLSX. This can be done manually or with scripts in `tools` if the sources allow. Source data vegetables names should be mapped to Fork Ranger Ingredients.

2) In `data\truth_states` several sources are overlayed for each state and ingredient. Monthly availability for Fork Ranger will be determined for each state/vegetable/month instance here.

3) Once state availabilities are determined, Regions will be confirmed or modified in `data/truth_regions`. (The process for this is TBD).