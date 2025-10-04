# Fork Ranger data processing tools

This folder `tools` contains scripts for speeding the most laborious processes that don't have to be done manually.

`tools\seasonal_food_guide_seasonality.py` does web scraping and creates a csv output of data from the Seasonal Food Guide website `https://www.seasonalfoodguide.org/about`. It does not define storage months, so it assigns every value as Prime Time, Starting Now, Last Chance, or not available "".

