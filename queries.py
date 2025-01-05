ROA2_ID = "53945"


def tournaments_by_game_id(id: str, online: bool, upcoming: bool) -> str:
    return f"""
        query QueryTournamentsByGameId {{
          tournaments(query: {{
            filter: {{
              videogameIds: [{id}],
              hasOnlineEvents: {str(online).lower()}, 
              upcoming: {str(upcoming).lower()}
            }}
            perPage: 250,
          }}) {{
            nodes {{
              id
              name
              numAttendees
              venueAddress
              url
              startAt
              timezone
              events(filter: {{videogameId: {id}}}) {{
                name
                numEntrants
              }}
            }}
          }}
        }}
    """
