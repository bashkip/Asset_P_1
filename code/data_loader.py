"""Data loading shared by all questions: sample period, French CSV parsing, returns, factors and characteristics."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent  # project root (this file lives in code/)
DATA = ROOT / "data"
OUTPUT = ROOT / "output"

# Team members -> student number (the digits in the eur.nl email prefix)
STUDENT_IDS = {
    "Francesco": 646407,
    "Sebastiaan": 652524,
    "Saranya": 648636,
    "Thomas": 706550,
}

PORTFOLIO_FILE = DATA / "25_Portfolios_ME_Prior_1_0.csv"
FF5_FILE = DATA / "F-F_Research_Data_5_Factors_2x3.csv"
SORT_FACTOR_FILE = DATA / "F-F_ST_Reversal_Factor.csv"
SORT_FACTOR = "ST_Rev"


def sample_period(student_ids: dict, path: Path = DATA / "start_end_fem21003.xlsx"):
    """Start and end month of the sample, taken from the student with the lowest student number."""
    df = pd.read_excel(path)
    df["student_number"] = df["Unnamed: 3"].astype(str).str.extract(r"^(\d+)")[0].astype(int)
    lowest = min(student_ids.values())
    row = df.loc[df["student_number"] == lowest]
    if row.empty:
        raise ValueError(f"Student number {lowest} not found in {path.name}")
    start, end = row["Start"].iloc[0], row["End"].iloc[0]
    return start.to_period("M"), end.to_period("M")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def read_french_section(path: Path, title: str | None = None) -> pd.DataFrame:
    """Read one monthly block from a Kenneth French CSV.

    The block starts at the first line containing `title` (or at the top of the file if None),
    its column header is the next line starting with ',', and it ends at the first line whose
    first field is not a yyyymm date. Missing values (-99.99, -999) become NaN.
    """
    lines = path.read_text().splitlines()
    i = 0
    if title is not None:
        i = next(k for k, line in enumerate(lines) if title in line)
    while not lines[i].startswith(","):
        i += 1
    columns = [c.strip() for c in lines[i].split(",")[1:]]

    rows, dates = [], []
    for line in lines[i + 1:]:
        fields = [f.strip() for f in line.split(",")]
        if len(fields[0]) != 6 or not fields[0].isdigit():
            break
        dates.append(pd.Period(f"{fields[0][:4]}-{fields[0][4:]}", freq="M"))
        rows.append([float(f) for f in fields[1:len(columns) + 1]])

    df = pd.DataFrame(rows, index=pd.PeriodIndex(dates, name="month"), columns=columns)
    return df.mask(df.isin([-99.99, -999.0]))


def build_characteristics(returns: pd.DataFrame, size: pd.DataFrame,
                          prior_ew: pd.DataFrame, prior_vw: pd.DataFrame) -> dict:
    """Raw characteristics per portfolio (T x N each), dated so that row t is known at the start of month t.

    From the French file: average firm size and the EW/VW average prior (t-1) return.
    Constructed from the portfolio's own return history (row t-1 is the latest return known at the start of t):
      mom   : sum of returns t-12..t-2 (skips the most recent month)
      ltrev : sum of returns t-60..t-13
      vol   : std of returns t-12..t-1
    """
    return {
        "size": size,
        "prior_ew": prior_ew,
        "prior_vw": prior_vw,
        "mom": returns.shift(2).rolling(11).sum(),
        "ltrev": returns.shift(13).rolling(48).sum(),
        "vol": returns.shift(1).rolling(12).std(),
    }


def load_data(start: pd.Period, end: pd.Period) -> dict:
    """Portfolio returns, risk-free rate, factors and characteristics over [start, end], all in % per month.

    Characteristics are built on the full history first, so look-back windows are filled at `start`.
    """
    returns = read_french_section(PORTFOLIO_FILE, "Average Value Weighted Returns -- Monthly")
    chars = build_characteristics(
        returns,
        size=read_french_section(PORTFOLIO_FILE, "Average Firm Size"),
        prior_ew=read_french_section(PORTFOLIO_FILE, "Equally-Weighted Average of Prior Returns"),
        prior_vw=read_french_section(PORTFOLIO_FILE, "Value-Weighted Average of Prior Returns"),
    )
    ff5 = read_french_section(FF5_FILE)
    sort_factor = read_french_section(SORT_FACTOR_FILE)

    window = slice(start, end)
    data = {
        "returns": returns.loc[window],
        "rf": ff5.loc[window, "RF"],
        "factors": pd.concat([ff5[["Mkt-RF", "SMB"]], sort_factor[[SORT_FACTOR]]], axis=1).loc[window],
        "chars": {name: c.loc[window] for name, c in chars.items()},
    }
    data["excess"] = data["returns"].sub(data["rf"], axis=0)

    n_months = end.ordinal - start.ordinal + 1
    for name, df in [("returns", data["returns"]), ("rf", data["rf"]), ("factors", data["factors"]),
                     *data["chars"].items()]:
        if len(df) != n_months or df.isna().any(axis=None):
            raise ValueError(f"{name}: incomplete data in {start}..{end}")
    return data


def load() -> dict:
    """Data for the team's prescribed sample period; also stores the period under 'start' and 'end'."""
    start, end = sample_period(STUDENT_IDS)
    return {"start": start, "end": end, **load_data(start, end)}


if __name__ == "__main__":
    data = load()
    print(f"Sample period: {data['start']} to {data['end']} ({len(data['returns'])} months)")
    print(f"Test assets: {data['returns'].shape[1]} portfolios; factors: {list(data['factors'].columns)}")
    print("\nFactor means / std (% per month):")
    print(data["factors"].agg(["mean", "std"]).round(2))
    print("\nCharacteristics (pooled mean / std):")
    print(pd.DataFrame({n: [c.stack().mean(), c.stack().std()] for n, c in data["chars"].items()},
                       index=["mean", "std"]).round(2))
    print("\nPooled correlation of characteristics:")
    print(pd.DataFrame({n: c.stack() for n, c in data["chars"].items()}).corr().round(2))
