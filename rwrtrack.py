import collections
import csv
import logging
import logging.config
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger.debug("Logging configured from logging.conf")


Stats = collections.namedtuple("Stats",
                               "username xp time_played "
                               "kills deaths longest_kill_streak "
                               "targets_destroyed vehicles_destroyed "
                               "soldiers_healed distance_moved "
                               "shots_fired throwables_thrown")

playerstats_url = "http://rwr.runningwithrifles.com/rwr_stats/view_players.php"


def request_stats(start=0):
    logger.debug(f"Requesting stats ({start}-{start+100}) from server")
    url = f"{playerstats_url}?sort=rank_progression&start={start}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        # Path("stats.html").write_text(r.text)
    except Exception as e:
        logger.critical(f"Requesting stats failed due to {type(e).__name__}",
                        exc_info=1)
        raise
    else:
        return r.text


def extract_rows(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[1::]
    return rows if rows else []


def convert_tp_to_mins(time_played):
    try:
        h, m = time_played.split(" ")
        hours = int(h[0:-1])
        mins = int(m[0:-3])
    except IndexError as e:
        logger.error(f"Converting {time_played} failed because of IndexError",
                     exc_info=1)
        raise
    except ValueError as e:
        logger.error(f"Converting {time_played} failed because of ValueError",
                     exc_info=1)
        raise
    else:
        return hours*60 + mins


def convert_dm_to_metres(distance_moved):
    # TODO: EXCEPTION HANDLING!
    dm_km = float(distance_moved[0:-2])
    dm_m = int(dm_km*1000)
    return dm_m


def extract_stats(row):
    cols = row.find_all("td")
    try:
        username = cols[1].get_text()
        kills = int(cols[2].get_text())
        deaths = int(cols[3].get_text())
        time_played = convert_tp_to_mins(cols[6].get_text())
        longest_kill_streak = int(cols[7].get_text())
        targets_destroyed = int(cols[8].get_text())
        vehicles_destroyed = int(cols[9].get_text())
        soldiers_healed = int(cols[10].get_text())
        teamkills = int(cols[11].get_text())
        distance_moved = convert_dm_to_metres(cols[12].get_text())
        shots_fired = int(cols[13].get_text())
        throwables_thrown = int(cols[14].get_text())
        xp = int(cols[15].get_text())
    except IndexError as e:
        logger.error(f"Skipping row\n'{row}'\ndue to IndexError", exc_info=1)
        return None
    except ValueError as e:
        logger.error(f"Skipping row\n'{row}'\ndue to ValueError", exc_info=1)
        return None
    else:
        return Stats(username, xp, time_played,
                     kills, deaths, longest_kill_streak,
                     targets_destroyed, vehicles_destroyed,
                     soldiers_healed, distance_moved,
                     shots_fired, throwables_thrown)


def get_stats(num_pages):
    logger.debug(f"Retrieving {num_pages} pages of stats from server")
    stats = []
    for x in range(0, num_pages*100, 100):
        html = request_stats(x)
        if html:
            rows = extract_rows(html)
            for row in rows:
                s = extract_stats(row)
                if s:
                    stats.append(s)
    return stats


def get_stats_test():
    # Hack function for developing new functionality without
    # hammering the RWR servers with requests
    logger.debug("Loading stats from stats.html example for testing")
    html = Path("stats.html").read_text(encoding="utf-8")
    stats = []
    if html:
        rows = extract_rows(html)
        for row in rows:
            s = extract_stats(row)
            stats.append(s)
    return stats


def write_stats_to_csv(stats):
    date_today = date.today()
    logger.debug(f"Writing stats to {date_today}.csv")
    field_headers = ["username", "xp", "time_played",
                     "kills", "deaths", "longest_kill_streak",
                     "targets_destroyed", "vehicles_destroyed",
                     "soldiers_healed", "distance_moved",
                     "shots_fired", "throwables_thrown"]
    csv_path = Path(__file__).parent / Path(f"csv_historical/{date_today}.csv")
    # TODO: Consider checking if a csv file for date_today already exists
    if not csv_path.parent.exists():
        csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(field_headers)
        for s in stats:
            writer.writerow([s.username, s.xp, s.time_played,
                             s.kills, s.deaths, s.longest_kill_streak,
                             s.targets_destroyed, s.vehicles_destroyed,
                             s.soldiers_healed, s.distance_moved,
                             s.shots_fired, s.throwables_thrown])


if __name__ == '__main__':
    logger.debug("Running rwrtrack.py as main program")
    # stats = get_stats_test()
    stats = get_stats(5)
    # print(stats)
    write_stats_to_csv(stats)

    # TODO: Consider one-script with arguments using docopt or whatever, or
    #       multiple scripts like the offline version
