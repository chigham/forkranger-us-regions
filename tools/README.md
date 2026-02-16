# Fork Ranger data processing tools

This folder `tools` contains scripts for speeding the most laborious processes that don't have to be done manually.

`tools\seasonal_food_guide_seasonality.py` does web scraping and creates a csv output of data from the Seasonal Food Guide website `https://www.seasonalfoodguide.org/about`. It does not define storage months, so it assigns every value as Prime Time, Starting Now, Last Chance, or not available "".

`tools\analyze_regional_suitability.py` measures how different states' seasonality patterns are from each other within a region. It utilizes the Pairwise Hamming Distance model per vegetable and then averages the scores for each state across all vegetables. An analyzer object tracks entire vegetables that are not local to the region and vegetable/state combinations that and rows that are excluded from analysis for one reason or another.
