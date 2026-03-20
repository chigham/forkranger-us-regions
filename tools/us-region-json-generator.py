import json
import pandas as pd
from pprint import pprint
import requests

def validate_truths(df: pd.DataFrame) -> bool:
    """Makes sure the only values in the month columns are the expected data values or the sentinel "-", which indicate seasonality status for each month."""

    expected_values = {"-", "SN", "LC", "GFS", "PT"}

    month_cols = data.columns[2:14]
    month_values = data[month_cols].to_numpy().ravel()
    unique_values_combined = pd.unique(month_values[pd.notna(month_values)])

    return set(unique_values_combined) == expected_values

def fr_id_from_en_name_mapper(df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from English Vegetable Name to Fork Ranger ID."""

    return dict(zip(df["nameEN"], df["id"]))

new_us_veggies = {
    "Collard greens": "", 
    "Green onion": "", 
    "Okra": "", 
    "Bok choy": "", 
    "Celeriac": "", 
    "Chard": "", 
    "Gooseberry": "", 
    "Radicchio": "", 
    "Radish": "", 
    "Boysenberry": "", 
    "Cardoons": "", 
    "Purslane": "", 
    "Quince": "", 
    "Rapini": "", 
    "Salsify": "", 
    "Sugar snaps": "", 
    "Snow peas": "", 
    "Jerusalem artichoke": "", 
    "Asian pears": "", 
    "Horseradish": "", 
    "Rhubarb": "", 
    "Swede": "", 
    "Pawpaw": "", 
    "Cantaloupe": ""
}


if __name__ == "__main__":

    fr_json_path = "https://github.com/jordibruin/forkrangerRecipes/blob/main/seasonal/seasonal-products.json?raw=true"
    seasonal_products_df = pd.read_json(fr_json_path)
    seasonal_products = json.loads(requests.get(fr_json_path).content)
    pprint(seasonal_products)

    name_to_id = fr_id_from_en_name_mapper(seasonal_products_df)

    sheet_name = "North-East"
    data = pd.read_excel(r"data\truth_states\State-Truths-v3.xlsx", sheet_name=sheet_name)
    data = data[["name", "truth", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
    data = data[data["truth"] == "Fork Ranger"]
    data = data.drop(columns=["truth"])
    data = data.rename(columns={"name": "nameEN"})
    
    # Convert data to a list of dictionaries for each row where the keys are "GFS", "LC", "PT", "SN", and "nameEN", and the values of the first four keys are lists containing the ordered integer column names that contain that key as a value, and the value of "nameEN" is that value in the "nameEN" column for that row.
    data_dicts = []
    for _, row in data.iterrows():
        row_dict = {"nameEN": row["nameEN"], "id": name_to_id.get(row["nameEN"], ""), "GFS": [], "LC": [], "PT": [], "SN": []}
        for month in range(1, 13):
            value = row[month]
            if value in ["GFS", "LC", "PT", "SN"]:
                row_dict[value].append(month)
        data_dicts.append(row_dict)
    
    print()
    print("     ==================================     ")
    print("     ==================================     ")
    print("     ==================================     ")
    print()
    
    pprint(data_dicts)
