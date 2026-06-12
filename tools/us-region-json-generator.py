import json
import os
import re
import pandas as pd
from pprint import pprint
import requests
from typing import Dict, Any, List


def normalize_name(s: str) -> str:
    if s is None:
        return ""
    ns = str(s).strip().lower()
    ns = re.sub(r"\s*\(.*?\)\s*", "", ns)
    ns = ns.replace("'", "").replace("’", "")
    ns = re.sub(r"[^a-z0-9 ]+", "", ns)
    ns = re.sub(r"\s+", " ", ns).strip()
    return ns


def fr_id_from_en_name_mapper(df: pd.DataFrame) -> Dict[str, Any]:
    return dict(zip(df["nameEN"], df["id"]))


def fr_image_from_en_name_mapper(df: pd.DataFrame) -> Dict[str, str]:
    return dict(zip(df["nameEN"], df["image"]))


def fr_nameNL_from_en_name_mapper(df: pd.DataFrame) -> Dict[str, str]:
    return dict(zip(df["nameEN"], df["nameNL"]))


def fr_nameDE_from_en_name_mapper(df: pd.DataFrame) -> Dict[str, str]:
    return dict(zip(df["nameEN"], df["nameDE"]))


en_to_us_mapper = {
    'Abricot': 'Apricot',
    'Apple': 'Apple',
    'Asparagus': 'Asparagus',
    'Aubergine': 'Eggplant',
    'Beetroot': 'Beet',
    'Bell pepper': 'Bell pepper',
    'Blackberry': 'Blackberry',
    'Blueberry': 'Blueberry',
    'Pak choi': 'Bok choy',
    'Broccoli': 'Broccoli',
    'Brussels sprouts': 'Brussels sprouts',
    'Cantaloupe': 'Cantaloupe',
    'Carrot': 'Carrot',
    'Cauliflower': 'Cauliflower',
    'Celeriac': 'Celery Root',
    'Celery': 'Celery',
    'Chard': 'Chard',
    'Cherry': 'Cherry',
    'Chicory': 'Belgian endive',
    'Chinese cabbage': 'Chinese cabbage',
    'Collard greens': 'Collard greens',
    'Corn': 'Corn',
    'Cucumber': 'Cucumber',
    'Endive': 'Curly endive',
    'Fennel': 'Fennel',
    'Gooseberry': 'Gooseberry',
    'Grapes': 'Grapes',
    'Green bean': 'Green bean',
    'Spring onion': 'Green onion',
    'Horseradish': 'Horseradish',
    'Jerusalem artichoke': 'Jerusalem artichoke',
    'Kale': 'Kale',
    'Kohlrabi': 'Kohlrabi',
    'Leek': 'Leek',
    'Lettuce': 'Lettuce',
    'Nectarine': 'Nectarine',
    'Okra': 'Okra',
    'Parsnip': 'Parsnip',
    'Pawpaw': 'Pawpaw',
    'Peach': 'Peach',
    'Pear': 'Pear',
    'Peas': 'Peas',
    'Plum': 'Plum',
    'Potato': 'Potato',
    'Pumpkin': 'Pumpkin',
    'Purslane': 'Purslane',
    'Quince': 'Quince',
    'Radicchio': 'Radicchio',
    'Radish': 'Radish',
    'Raspberry': 'Raspberry',
    'Rhubarb': 'Rhubarb',
    'Rocket': 'Rocket',
    'Black salsify': 'Salsify',
    'Snow peas': 'Snow peas',
    'Spinach': 'Spinach',
    'Strawberry': 'Strawberry',
    'Sugar snaps': 'Sugar snap peas',
    'Swede': 'Rutabaga',
    'Tomato': 'Tomato',
    'Turnip': 'Turnip',
    'Watermelon': 'Watermelon',
    'White cabbage': 'White cabbage',
    'Zucchini': 'Zucchini'
}


us_to_en_mapper = {v: k for k, v in en_to_us_mapper.items()}


def load_seasonal_products(local_path: str, remote_url: str) -> List[Dict[str, Any]]:
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return json.loads(requests.get(remote_url).text)


if __name__ == "__main__":
    fr_remote_url = "https://github.com/jordibruin/forkrangerRecipes/blob/main/seasonal/seasonal-products.json?raw=true"
    local_canonical = os.path.join(os.getcwd(), 'examples', 'seasonal-products.json')

    seasonal_products = load_seasonal_products(local_canonical, fr_remote_url)
    seasonal_products_df = pd.DataFrame(seasonal_products)
    pprint(seasonal_products[:10])

    # canonical maps
    name_to_id_raw = fr_id_from_en_name_mapper(seasonal_products_df)
    name_to_id = {k: (str(v) if pd.notna(v) else '') for k, v in name_to_id_raw.items()}
    name_to_image = fr_image_from_en_name_mapper(seasonal_products_df)
    name_to_nameNL = fr_nameNL_from_en_name_mapper(seasonal_products_df)
    name_to_nameDE = fr_nameDE_from_en_name_mapper(seasonal_products_df)

    # normalized canonical lookup
    season_norm = {normalize_name(n): n for n in seasonal_products_df['nameEN'].astype(str)}
    name_to_id_norm = {normalize_name(k): v for k, v in name_to_id.items()}
    name_to_image_norm = {normalize_name(k): v for k, v in name_to_image.items()}
    name_to_nameNL_norm = {normalize_name(k): v for k, v in name_to_nameNL.items()}
    name_to_nameDE_norm = {normalize_name(k): v for k, v in name_to_nameDE.items()}

    # gather fallbacks from regional example files
    examples_dir = os.path.join(os.getcwd(), 'examples')
    fallback_id: Dict[str, str] = {}
    fallback_image: Dict[str, str] = {}
    fallback_nameNL: Dict[str, str] = {}
    fallback_nameDE: Dict[str, str] = {}
    fallback_nameEN: Dict[str, str] = {}
    if os.path.isdir(examples_dir):
        for fname in os.listdir(examples_dir):
            if not fname.startswith('seasonal-products-') or not fname.endswith('.json'):
                continue
            if fname == 'seasonal-products.json':
                continue
            try:
                with open(os.path.join(examples_dir, fname), 'r', encoding='utf-8') as f:
                    arr = json.load(f)
            except Exception:
                continue
            for p in arr:
                n = p.get('nameEN')
                if not n:
                    continue
                key = normalize_name(n)
                if p.get('id') is not None and str(p.get('id')).strip() != '':
                    fallback_id.setdefault(key, str(p.get('id')))
                if p.get('image'):
                    fallback_image.setdefault(key, p.get('image'))
                if p.get('nameNL'):
                    fallback_nameNL.setdefault(key, p.get('nameNL'))
                if p.get('nameDE'):
                    fallback_nameDE.setdefault(key, p.get('nameDE'))
                fallback_nameEN.setdefault(key, n)
                season_norm.setdefault(key, n)

    en_to_us_norm = {normalize_name(k): v for k, v in en_to_us_mapper.items()}
    us_to_en_norm = {normalize_name(v): k for k, v in en_to_us_mapper.items()}

    sheet_name = "Great-Lakes-Ohio-Valley-Midwest"  # TODO: Update every time
    data = pd.read_excel(r"data\truth_states\State-Truths-v3.xlsx", sheet_name=sheet_name)  # TODO: Update every time
    data = data[["name", "truth", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
    data = data[data["truth"] == "Fork Ranger"]
    data = data.drop(columns=["truth"]).rename(columns={"name": "nameEN"})

    data_dicts: List[Dict[str, Any]] = []
    for _, row in data.iterrows():
        raw_name = str(row["nameEN"]).strip()
        key = normalize_name(raw_name)

        # Resolve nameEN with fallbacks and simple pluralization heuristics
        name_en = None
        candidates = [key]
        if key.endswith('s'):
            candidates.insert(0, key[:-1])
        else:
            candidates.append(key + 's')

        for c in candidates:
            if c in season_norm:
                name_en = season_norm[c]
                break
            if c in fallback_nameEN:
                name_en = fallback_nameEN[c]
                break

        if not name_en:
            if key in us_to_en_norm:
                name_en = us_to_en_norm[key]
            elif key in en_to_us_norm:
                name_en = next((orig for orig in en_to_us_mapper.keys() if normalize_name(orig) == key), None)
            elif key in fallback_nameEN:
                name_en = fallback_nameEN[key]
            else:
                name_en = raw_name

        name_us = en_to_us_mapper.get(name_en, name_en)
        nkey = normalize_name(name_en)

        id_val = name_to_id.get(name_en) or name_to_id_norm.get(nkey) or fallback_id.get(key, '')
        image_val = name_to_image.get(name_en) or name_to_image_norm.get(nkey) or fallback_image.get(key, '')
        nameNL_val = name_to_nameNL.get(name_en) or name_to_nameNL_norm.get(nkey) or fallback_nameNL.get(key, '')
        nameDE_val = name_to_nameDE.get(name_en) or name_to_nameDE_norm.get(nkey) or fallback_nameDE.get(key, '')

        row_dict = {
            "nameEN": name_en,
            "id": id_val or "",
            "nameNL": nameNL_val or "",
            "nameDE": nameDE_val or "",
            "nameUS": name_us,
            "image": image_val or "",
            "GFS": [],
            "LC": [],
            "PT": [],
            "SN": []
        }

        for month in range(1, 13):
            value = row[month]
            if value in ["GFS", "LC", "PT", "SN"]:
                row_dict[value].append(month)
        data_dicts.append(row_dict)

    # Merge or append additional US-only veggies from CSV (no id/image expected)
    csv_path = os.path.join('examples', 'new_us_veggies_MB.csv')  # TODO: Update every time
    if os.path.exists(csv_path):
        try:
            new_df = pd.read_csv(csv_path, dtype=str).fillna('')
            for _, crow in new_df.iterrows():
                csv_name_en = str(crow.get('nameEN', '')).strip()
                if not csv_name_en:
                    continue
                ck = normalize_name(csv_name_en)

                # try to find an existing product in data_dicts and update names
                updated = False
                for d in data_dicts:
                    if normalize_name(d.get('nameEN', '')) == ck:
                        if not str(d.get('nameNL', '')).strip():
                            d['nameNL'] = str(crow.get('nameNL', '')).strip()
                        if not str(d.get('nameDE', '')).strip():
                            d['nameDE'] = str(crow.get('nameDE', '')).strip()
                        # prefer CSV nameUS when present
                        if str(crow.get('nameUS', '')).strip():
                            d['nameUS'] = str(crow.get('nameUS', '')).strip()
                        updated = True
                        break
        except Exception as e:
            print(f"Warning: failed to read or parse {csv_path}: {e}")

    data_dicts.sort(key=lambda x: (int(x["id"]) if str(x["id"]).strip() else float("inf"), x["nameEN"]))

    ordered_keys = ["id", "nameNL", "nameEN", "nameDE", "nameUS", "image", "LC", "GFS", "PT", "SN"]
    data_dicts = [{k: d.get(k, "") for k in ordered_keys} for d in data_dicts]

    missing_id = [d for d in data_dicts if not str(d.get('id')).strip()]
    missing_image = [d for d in data_dicts if not str(d.get('image')).strip()]
    print(f"Total items: {len(data_dicts)}")
    print(f"Missing id count: {len(missing_id)}")
    print(f"Missing image count: {len(missing_image)}")

    raw_json = json.dumps(data_dicts, indent=2, ensure_ascii=False)
    raw_json = re.sub(r'\[\s*\]', '[]', raw_json)

    output_path = os.path.join('examples', 'seasonal-products-USGL.json')  # TODO: Update every time
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(raw_json)
    print(f"\nSaved to {output_path}")