import os
import random
import json
from pathlib import Path
from time import monotonic, sleep

from dotenv import load_dotenv
import musicbrainzngs

import networkx as nx
from pyvis.network import Network


# =========================
# Konfiguration
# =========================

load_dotenv()

musicbrainzngs.set_useragent(
    os.getenv("MB_APP_NAME", "MusicGraph"),
    os.getenv("MB_VERSION", "1.0"),
    os.getenv("MB_CONTACT", "unknown")
)


# MusicBrainz IDs!
# Hier nur echte eindeutige IDs eintragen

ARTISTS = {
    "a40ea317-e531-428a-909b-da1e68700573": "Freddie Dredd",
    "ef326b3d-61f0-4379-aca0-21237d696d63": "$uicideboy$",
    "ade4c525-9c89-4977-8cf6-dedd53c54573": "Cursed",
    "e0b50375-d3b1-4fbd-960b-67ce8950f737": "1nonly",
    "162b4965-1664-45d9-9c4d-91a948da1736": "870glizzy",
    "bc4cf08a-4ffe-454e-93b2-30a0be5cef8c": "BLCKK",
    "cad93cfa-f023-4f42-9919-0d73567575b4": "Bumboi",
    "31a0ab8f-c879-4cbc-95e6-3101b08c7ffc": "Santos Santana",
    "7932a977-460b-46c7-bbfb-a4db3ebca16f": "Sinizter",
    "215294d9-e121-4458-ba5b-44a3320c9cd3": "Sect Unit aka. Cardeairè Jack",
    "9b3efa33-033b-4612-8d7d-e3bac072a770": "Lord Gasp",
    "84b74b71-d9fc-4e1e-b77b-34c697df5666": "GODHANDUSA",
    "63e1d5bf-f968-4487-a449-5786fa6b4454": "Grim Salvo",
    "4ce34d0f-0d21-4521-92c6-09b47db6f5e8": "ISSBROKIE",
    "6ad4e523-2d44-4151-a32a-fc39cb50d689": "Lil Kaine",
    "99e0983f-6183-463e-a61e-2041ca8931ba": "Lil Darkie",
    "3cd4ffd4-d934-4007-9ad4-829f86eefd3d": "Lu",
    "cae09884-f473-460a-a04a-4dd3fc69cf6e": "Pouya",
    "1989dd59-7f11-4c90-9450-4d728ed07fb0": "Ghostemane",
    "d231ec46-7c77-473f-ae50-71f774461abf": "Ramirez",
    "c25963ac-b289-4d99-a8dc-06c0ce757f0c": "Night Lovell",
    "e5935f40-48a6-4bab-8ace-4ad7f7148e15": "Savage Ga$p",
    "32477cb6-1132-49ac-837f-0a88260b80a8": "shteppi",
    "d04743e0-7b28-437a-9d06-3e3e6232d880": "Faceless 1-7",
    "a9fc7c6e-cd47-46d3-b0d0-07b512ca8ded": "Prompto",
    "e11fda7b-15fd-453a-ac9b-0704cbba7529": "Sadfriendd",
    "b99ea5a6-84a0-4fd3-8976-f73252853f05": "Towa ",
    "d49766d4-bb65-47a2-9056-d1dc02cc2575": "TWENTYTHREE",
    "806c25d3-7724-4da0-8c5e-08797f1efe5b": "Witchouse 40k",
    "1757ec32-7b59-403d-bbe5-5e85a0207baf": "Istasha",
    "c9e99426-b852-4509-97d5-e7546e8c6b2d": "KAMAARA",
    "8b87a68b-5d06-4ac1-a88f-752d3cfbd989": "Salvia Grey",
    "6d3b73ab-fd28-457a-a68c-dbe359f19b56": "MOSSBACK",
    "e11bf872-101b-44e0-99e2-58bc4f5e5f8d": "99zed",
    "b7d60457-cf60-4d53-90e7-c457f657487b": "cr1tter",
    "ce512113-aab1-49a8-b4f0-d8400fa33c8e": "Letoa",
    "1e24e6b0-5dd3-4c6d-850b-c477824cfe1d": "lilbubblegum",
    "419d19c3-de05-4ba3-a2c8-5c3fd5ec06cf": "SXMPRA",
    "cbf010c3-db28-41dc-accf-b58a547a6ba7": "NetuH",
    "1f23ac38-b652-4dc7-9684-a4a3f6a211f2": "Warlord Colossus",
    "20b034b2-35a1-40be-908f-22d1b5681572": "Yung Gravy",
    "bb7959ac-84cc-45c4-8138-d80ee5f2bd9a": "Lucy Bedroque",
    "968847c6-2150-419d-b14b-68c672dcde99": "fakemink",
    "6e878f15-50aa-4087-966a-f3cc1f06dce3": "egobreak"
}


CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

OUTPUT = "musicbrainz_graph.html"


# =========================
# Rate Limit
# 10 Requests / Sekunde
# =========================

INTERVAL = 1 / 10
last_request = 0


def api_wait():

    global last_request

    elapsed = monotonic() - last_request

    if elapsed < INTERVAL:
        sleep(INTERVAL - elapsed)

    last_request = monotonic()



# =========================
# Cache
# =========================

def cache_path(name):
    return CACHE_DIR / f"{name}.json"



def save_cache(name, data):

    with open(
        cache_path(name),
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False
        )



def load_cache(name):

    path = cache_path(name)

    if path.exists():

        with open(
            path,
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return None



# =========================
# MusicBrainz
# =========================

def get_releases(artist_id):

    key = "releases_" + artist_id


    cached = load_cache(key)

    if cached:
        return cached


    print(
        "Lade Releases:",
        artist_id
    )


    releases = []

    offset = 0


    while True:

        result = musicbrainzngs.browse_releases(
            artist=artist_id,
            limit=100,
            offset=offset
        )

        api_wait()


        batch = result.get(
            "release-list",
            []
        )


        releases.extend(batch)


        if len(batch) < 100:
            break


        offset += 100



    save_cache(
        key,
        releases
    )


    return releases



def get_release_tracks(release_id):

    key = "tracks_" + release_id


    cached = load_cache(key)

    if cached:
        return cached



    result = musicbrainzngs.get_release_by_id(
        release_id,
        includes=[
            "recordings",
            "artist-credits"
        ]
    )

    api_wait()


    release = result["release"]


    tracks = []


    for medium in release.get(
        "medium-list",
        []
    ):

        for track in medium.get(
            "track-list",
            []
        ):

            recording = track.get(
                "recording"
            )


            if recording:
                tracks.append(
                    recording
                )


    save_cache(
        key,
        tracks
    )


    return tracks



# =========================
# Graph
# =========================

G = nx.Graph()



def add_artist(
    artist_id,
    artist_name
):

    print(
        "\nAnalysiere:",
        artist_name
    )


    G.add_node(
        artist_id,
        name=artist_name
    )


    releases = get_releases(
        artist_id
    )


    print(
        artist_name,
        "-",
        len(releases),
        "Releases"
    )


    seen_tracks = set()


    for index, release in enumerate(releases):

        if index % 25 == 0:
            print(
                f"{index}/{len(releases)} Releases"
            )


        tracks = get_release_tracks(
            release["id"]
        )


        for recording in tracks:


            recording_id = recording["id"]


            if recording_id in seen_tracks:
                continue


            seen_tracks.add(
                recording_id
            )


            credits = recording.get(
                "artist-credit",
                []
            )


            track_artists = []


            for credit in credits:

                if not isinstance(credit, dict):
                    continue

                artist = credit.get(
                    "artist"
                )


                if not artist:
                    continue


                mbid = artist["id"]


                # Nur Zielkünstler
                if mbid in ARTISTS:

                    track_artists.append(
                        {
                            "id": mbid,
                            "name": ARTISTS[mbid]
                        }
                    )



            # Kanten erstellen

            for i in range(len(track_artists)):

                for j in range(
                    i + 1,
                    len(track_artists)
                ):


                    a = track_artists[i]
                    b = track_artists[j]


                    if G.has_edge(
                        a["id"],
                        b["id"]
                    ):

                        G[a["id"]][b["id"]]["weight"] += 1


                    else:

                        G.add_edge(
                            a["id"],
                            b["id"],
                            weight=1
                        )



# =========================
# Start
# =========================

for artist_id, name in ARTISTS.items():

    add_artist(
        artist_id,
        name
    )



print("\nErgebnis:")
print(
    "Nodes:",
    G.number_of_nodes()
)

print(
    "Edges:",
    G.number_of_edges()
)



# =========================
# PyVis
# =========================

net = Network(
    height="900px",
    width="100%",
    bgcolor="#111111",
    font_color="white"
)

net.barnes_hut(
    gravity=-8000,       # more negative = nodes push apart harder
    central_gravity=0.2, # lower = less pull toward center
    spring_length=250,   # longer = more space along edges
    spring_strength=0.02,
    damping=0.09,
    overlap=0
)

def random_color():
    r = random.randint(80, 255)
    g = random.randint(80, 255)
    b = random.randint(80, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

for node, data in G.nodes(data=True):

    net.add_node(
        node,
        label=data["name"],
        color=random_color()
    )



for a, b, data in G.edges(data=True):

    net.add_edge(
        a,
        b,
        value=data["weight"],
        title=f"Gemeinsame Tracks: {data['weight']}"
    )



net.write_html(
    OUTPUT
)


print(
    "\nFertig:",
    OUTPUT
)