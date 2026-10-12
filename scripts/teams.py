"""Team lookup: ESPN abbreviation -> StatRankings name, nflverse code, colors.

ESPN abbreviations are the canonical team key everywhere in this repo.
"""

TEAMS = {
    # abbr: (StatRankings / full name, nflverse code, primary, secondary)
    "ARI": ("Arizona Cardinals", "ARI", "#97233F", "#FFB612"),
    "ATL": ("Atlanta Falcons", "ATL", "#A71930", "#000000"),
    "BAL": ("Baltimore Ravens", "BAL", "#241773", "#9E7C0C"),
    "BUF": ("Buffalo Bills", "BUF", "#00338D", "#C60C30"),
    "CAR": ("Carolina Panthers", "CAR", "#0085CA", "#101820"),
    "CHI": ("Chicago Bears", "CHI", "#0B162A", "#C83803"),
    "CIN": ("Cincinnati Bengals", "CIN", "#FB4F14", "#000000"),
    "CLE": ("Cleveland Browns", "CLE", "#311D00", "#FF3C00"),
    "DAL": ("Dallas Cowboys", "DAL", "#003594", "#869397"),
    "DEN": ("Denver Broncos", "DEN", "#FB4F14", "#002244"),
    "DET": ("Detroit Lions", "DET", "#0076B6", "#B0B7BC"),
    "GB": ("Green Bay Packers", "GB", "#203731", "#FFB612"),
    "HOU": ("Houston Texans", "HOU", "#03202F", "#A71930"),
    "IND": ("Indianapolis Colts", "IND", "#002C5F", "#A2AAAD"),
    "JAX": ("Jacksonville Jaguars", "JAX", "#006778", "#D7A22A"),
    "KC": ("Kansas City Chiefs", "KC", "#E31837", "#FFB81C"),
    "LV": ("Las Vegas Raiders", "LV", "#000000", "#A5ACAF"),
    "LAC": ("Los Angeles Chargers", "LAC", "#0080C6", "#FFC20E"),
    "LAR": ("Los Angeles Rams", "LA", "#003594", "#FFA300"),
    "MIA": ("Miami Dolphins", "MIA", "#008E97", "#FC4C02"),
    "MIN": ("Minnesota Vikings", "MIN", "#4F2683", "#FFC62F"),
    "NE": ("New England Patriots", "NE", "#002244", "#C60C30"),
    "NO": ("New Orleans Saints", "NO", "#D3BC8D", "#101820"),
    "NYG": ("New York Giants", "NYG", "#0B2265", "#A71930"),
    "NYJ": ("New York Jets", "NYJ", "#125740", "#FFFFFF"),
    "PHI": ("Philadelphia Eagles", "PHI", "#004C54", "#A5ACAF"),
    "PIT": ("Pittsburgh Steelers", "PIT", "#FFB612", "#101820"),
    "SF": ("San Francisco 49ers", "SF", "#AA0000", "#B3995D"),
    "SEA": ("Seattle Seahawks", "SEA", "#002244", "#69BE28"),
    "TB": ("Tampa Bay Buccaneers", "TB", "#D50A0A", "#34302B"),
    "TEN": ("Tennessee Titans", "TEN", "#0C2340", "#4B92DB"),
    "WSH": ("Washington Commanders", "WAS", "#5A1414", "#FFB612"),
}


def name(abbr):
    return TEAMS[abbr][0]


def nflverse(abbr):
    return TEAMS[abbr][1]


def colors(abbr):
    return TEAMS[abbr][2], TEAMS[abbr][3]
