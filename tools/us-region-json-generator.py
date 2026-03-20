import json
import re
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

def fr_image_from_en_name_mapper(df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from English Vegetable Name to Fork Ranger image name."""

    return dict(zip(df["nameEN"], df["image"]))

def fr_nameNL_from_en_name_mapper(df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from English Vegetable Name to Fork Ranger Dutch name."""

    return dict(zip(df["nameEN"], df["nameNL"]))

def fr_nameDE_from_en_name_mapper(df: pd.DataFrame) -> dict[str, str]:
    """Creates a mapping from English Vegetable Name to Fork Ranger German name."""

    return dict(zip(df["nameEN"], df["nameDE"]))

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
    name_to_image = fr_image_from_en_name_mapper(seasonal_products_df)
    name_to_nameNL = fr_nameNL_from_en_name_mapper(seasonal_products_df)
    name_to_nameDE = fr_nameDE_from_en_name_mapper(seasonal_products_df)

    sheet_name = "North-East"
    data = pd.read_excel(r"data\truth_states\State-Truths-v3.xlsx", sheet_name=sheet_name)
    data = data[["name", "truth", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
    data = data[data["truth"] == "Fork Ranger"]
    data = data.drop(columns=["truth"])
    data = data.rename(columns={"name": "nameEN"})
    
    # Convert data to a list of dictionaries for each row where the keys are "GFS", "LC", "PT", "SN", and "nameEN", and the values of the first four keys are lists containing the ordered integer column names that contain that key as a value, and the value of "nameEN" is that value in the "nameEN" column for that row.
    data_dicts = []
    for _, row in data.iterrows():
        row_dict = {"nameEN": row["nameEN"], "id": name_to_id.get(row["nameEN"], ""), "nameNL": name_to_nameNL.get(row["nameEN"], ""), "nameDE": name_to_nameDE.get(row["nameEN"], ""), "image": name_to_image.get(row["nameEN"], ""), "GFS": [], "LC": [], "PT": [], "SN": []}
        for month in range(1, 13):
            value = row[month]
            if value in ["GFS", "LC", "PT", "SN"]:
                row_dict[value].append(month)
        data_dicts.append(row_dict)
    
    data_dicts.sort(key=lambda x: (int(x["id"]) if x["id"] else float("inf"), x["nameEN"]))

    # Reorder keys matching seasonal-products.json: id, nameNL, nameEN, nameDE, image, LC, GFS, PT, SN
    ordered_keys = ["id", "nameNL", "nameEN", "nameDE", "image", "LC", "GFS", "PT", "SN"]
    data_dicts = [{k: d[k] for k in ordered_keys} for d in data_dicts]

    print()
    print("     ==================================     ")
    print("     ==================================     ")
    print("     ==================================     ")
    print()
    
    pprint(data_dicts)

    # Format JSON matching seasonal-products.json style (2-space indent, empty lists inline)
    raw_json = json.dumps(data_dicts, indent=2)
    raw_json = re.sub(r'\[\s*\]', '[]', raw_json)

    output_path = r"examples\seasonal-products-USNE.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(raw_json)
    print(f"\nSaved to {output_path}")
