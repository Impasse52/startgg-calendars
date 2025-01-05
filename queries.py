ROA2_ID = "53945"


def tournaments_by_game_id(id: str) -> str:
    return f"""
        query QueryTournamentsByGameId {{
          tournaments(query: {{
            filter: {{
              videogameIds: [{id}]
            }}
          }}) {{
            nodes {{
              id
              name
              numAttendees
              venueAddress
              url
              startAt
              events(filter: {{videogameId: {id}}}) {{
                name
                numEntrants
              }}
            }}
          }}
        }}
    """
