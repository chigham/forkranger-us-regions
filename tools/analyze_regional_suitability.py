import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def pairwise_hamming_distance(matrix: np.ndarray) -> np.ndarray:
    '''
    Performs a 3D Pairwise Hamming Distance calculation on a boolean matrix 
    representing month seasonality for each vegetable/state combination. 
    Returns the average distance for each row representing as vegetable/state combination.
    '''

    n = matrix.shape[0]
    diff = matrix[:, None, :] != matrix[None, :, :]
    pairwise_dist = diff.mean(axis=2)

    return pairwise_dist.sum(axis=1) / (n - 1)


class SeasonalityAnalyzer:

    def __init__(self, file_path: str, sheet_name: str, ignore_label: str, sentinel_values: list[str] = None) -> None:
        '''
        Constructor for SeasonalityAnalyzer. 
        
        Expects: 
         - an excel file path, 
         - a sheet name with region data, 
         - a label to ignore in the state column (Fork Ranger, region name, etc.), and
         - a list of sentinel data values that should map to false in the boolean matrix (e.g. "0", "", "-").
        
        It opens the file, recognizes the vegetable, state, and month columns, 
        and initializes data structures for analysis and reporting.
        '''

        self.file_path = file_path
        self.sheet_name = sheet_name
        self.ignore_label = ignore_label
        self.sentinel_values = sentinel_values or ["0"]

        self.df = pd.read_excel(file_path, sheet_name=sheet_name)

        self.veg_col = self.df.columns[0]
        self.state_col = self.df.columns[1]
        self.month_cols = self.df.columns[2:14]

        self.state_scores = {}
        self.state_counts = {}

        self.report = {"vegetables_excluded": [], "state_rows_excluded": []}

    def _boolean_matrix(self, group: pd.DataFrame) -> np.ndarray:
        '''
        Converts the dataframe subset for one vegetable into a boolean matrix. 
        Sentinel values (e.g. "0", "", "-") are treated as False, 
        and all other values are treated as True.
        '''

        values = group[self.month_cols].astype(str)
        bool_df = ~values.isin(self.sentinel_values)
        return bool_df.to_numpy()

    def analyze(self, exclude_ignore_label: bool = False) -> pd.DataFrame:
        '''
        Cleans and filters the data, 
        transforms into boolean matrices for each vegetable,
        analyzes using pairwise Hamming distance, 
        summarizes averages for each state, 
        and tracks excluded data.
        '''

        for veg, group in self.df.groupby(self.veg_col):

            if exclude_ignore_label:
                if self.ignore_label not in group[self.state_col].values:  # Skip this vegetable altogether and move on
                    self.report["vegetables_excluded"].append((veg, "missing_ignore_label"))
                    continue

                group = group[group[self.state_col] != self.ignore_label]

            if len(group) == 0:  # Skip this vegetable altogether and move on
                self.report["vegetables_excluded"].append((veg, "no_states_after_ignore_removed"))
                continue

            month_data = group[self.month_cols]

            # Vectorized invalid detection
            contains_nan = month_data.isna().any(axis=1)

            contains_gfs = (month_data.astype(str).apply(lambda col: col.str.contains("GFS", case=False)).any(axis=1))

            invalid_mask = contains_nan | contains_gfs

            if invalid_mask.any():
                excluded_states = group.loc[invalid_mask, self.state_col].tolist()

                for state in excluded_states:
                    self.report["state_rows_excluded"].append((veg, state))

                group = group[~invalid_mask]

            # Need at least 2 states for comparison
            if len(group) < 2:
                self.report["vegetables_excluded"].append((veg, "fewer_than_two_valid_states"))
                continue

            #! --- The real analysis begins here. Everything before this was data cleaning and validation ---

            matrix = self._boolean_matrix(group)

            state_avg = pairwise_hamming_distance(matrix)

            states = group[self.state_col].values

            for state, score in zip(states, state_avg):
                self.state_scores[state] = (
                    self.state_scores.get(state, 0) + score
                )
                self.state_counts[state] = (
                    self.state_counts.get(state, 0) + 1
                )

        return self._finalize()

    def _finalize(self) -> pd.DataFrame:
        '''Averages pairwise Hamming distance scores across all vegetables for each state.'''

        final_scores = {state: self.state_scores[state] / self.state_counts[state] for state in self.state_scores}

        self.results_df = pd.DataFrame.from_dict(final_scores, orient="index", columns=["Distinctness Score"]).sort_values("Distinctness Score", ascending=False)

        return self.results_df

    def get_report(self) -> dict[str, pd.DataFrame]:
        '''
        Report includes results and info about vegetables and 
        state/veggie combinations that were excluded from analysis.
        '''

        vegetables_excluded = pd.DataFrame(self.report["vegetables_excluded"], columns=["Vegetable", "Reason"])
        state_rows_excluded = pd.DataFrame(self.report["state_rows_excluded"], columns=["Vegetable", "State"])

        return {"results": self.results_df, "vegetables_excluded": vegetables_excluded, "state_rows_excluded": state_rows_excluded}


if __name__ == "__main__":

    file_path = r"data\truth_states\State-Truths-v3.xlsx"

    ne_analyzer = SeasonalityAnalyzer(file_path=file_path, sheet_name="North-East", ignore_label="Fork Ranger", sentinel_values=["0", "", "-"])
    ne_results = ne_analyzer.analyze(exclude_ignore_label=True)
    ne_report = ne_analyzer.get_report()
    print(ne_analyzer.sheet_name)
    print(ne_results)
    #print(ne_report["vegetables_excluded"])
    #print(ne_report["state_rows_excluded"])
    print()

    ma_analyzer = SeasonalityAnalyzer(file_path=file_path, sheet_name="Mid-Atlantic", ignore_label="Fork Ranger", sentinel_values=["0", "", "-"])
    ma_results = ma_analyzer.analyze(exclude_ignore_label=True)
    ma_report = ma_analyzer.get_report()
    print(ma_analyzer.sheet_name)
    print(ma_results)
    print()

    se_analyzer = SeasonalityAnalyzer(file_path=file_path, sheet_name="South-East", ignore_label="South-East", sentinel_values=["0", "", "-"])
    se_results = se_analyzer.analyze(exclude_ignore_label=False)
    se_report = se_analyzer.get_report()
    print(se_analyzer.sheet_name)
    print(se_results)
    print()
