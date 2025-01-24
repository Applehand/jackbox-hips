from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random
import string
from app.models import *

origins = [
    "http://localhost",
    "http://localhost:5173",
    "https://itch.io",
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sessions = {}

# Utility Functions

def get_session(key: int | str) -> Session:
    """Retrieve a session by session_id or access_code, raise an HTTPException if not found."""
    if isinstance(key, int):
        session = sessions.get(key)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
        return session
    elif isinstance(key, str):
        for session in sessions.values():
            if session.access_code == key:
                return session
        raise HTTPException(status_code=404, detail="Session not found.")
    else:
        raise HTTPException(status_code=400, detail="Invalid key type. Expected int or str.")


def generate_access_code(length: int = 4) -> str:
    """Generate a random access code of the specified length."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Session Routes

@app.post("/sessions", response_model=CreateSessionResponse)
def create_session(request: CreateSessionRequest):
    """Create a new game session."""
    session_id = len(sessions) + 1
    access_code = generate_access_code()
    host_player = HostPlayer(name=request.host_name, role="in_lobby", id=0, host_password=request.host_password)
    new_session = Session(
        session_id=session_id,
        access_code=access_code,
        host=host_player,
    )
    sessions[session_id] = new_session
    return CreateSessionResponse(
        session_id=new_session.session_id,
        access_code=new_session.access_code,
        host_player=host_player
    )

@app.get("/sessions/{session_id}", response_model=GetSessionDataResponse)
def get_session_data(session_id: int):
    """Retrieve session data by session ID."""
    session: Session = get_session(session_id)
    
    current_game = session.current_game if session.current_game else None

    return GetSessionDataResponse(
        session_id=session.session_id,
        access_code=session.access_code,
        current_game=current_game,
        session_players=session.session_players,
    )

@app.delete("/sessions/{session_id}")
def delete_session(session_id: int):
    """Delete a session by session ID."""
    session: Session = sessions.pop(session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    return {"message": f"Session {session_id} deleted successfully"}

# Game Routes

@app.post("/sessions/{session_id}/start")
def start_session_game(session_id: int):
    """Start a game within a session."""
    session: Session = get_session(session_id)
    
    if session.current_game:
        raise HTTPException(status_code=400, detail="Game already in progress.")

    session.game_type = GameType.werewolf # Temporary placeholder for game type.
    
    if not session.game_type:
        raise HTTPException(status_code=400, detail="Game type not set. Please set the game type before starting the game.")
    
    session.current_game = Game(game_type=session.game_type, game_players=session.session_players)
    initial_game_state = session.current_game.start_game()

    return {
        "message": f"Session {session.session_id} game started successfully.",
        "game_state": initial_game_state
    }

@app.post("/sessions/{session_id}/end")
def end_session_game(session_id: int):
    """End a game within a session."""
    session: Session = get_session(session_id)
    
    session.game_type = None

    if not session.current_game:
        raise HTTPException(status_code=400, detail="There is no game to end.")
    
    session.current_game.end_game()
    session.current_game = None

    return {
        "message": f"Session {session_id} game ended successfully."
    }

@app.get("/sessions/{session_id}/game")
def get_game_data(session_id: int):
    """Retrieve game data from a session."""
    session: Session = get_session(session_id)
    
    if not session.current_game:
        raise HTTPException(status_code=400, detail="No game currently in progress in this session.")
    
    return {
        "game_state": session.current_game.game_state,
        "player_states": [player.model_dump() for player in session.session_players],
    }

@app.post("/sessions/{session_id}/game")
def update_game_state(session_id: int, update: dict):
    """Update the game state within a session."""
    session: Session = get_session(session_id)
    
    if not session.current_game:
        raise HTTPException(status_code=400, detail="No game currently in progress in this session.")
    
    session.current_game.game_state.update(update)
    
    return {
        "message": "Game state updated successfully.",
        "game_state": session.current_game.game_state
    }

# Player Routes

@app.post("/sessions/{access_code}/players", response_model=List[Player])
def create_player(access_code: str, request: CreatePlayerRequest):
    """Create a new player and add to a session."""
    session: Session = get_session(access_code)

    player_id = session.player_id_counter
    session.player_id_counter += 1

    player = Player(name=request.name, role="in_lobby", id=player_id)
    session.session_players.append(player)

    return session.session_players

@app.get("/sessions/{session_id}/players", response_model=List[Player])
def get_players_data(session_id: int):
    """Retrieve all players in a session."""
    session: Session = get_session(session_id)

    return session.session_players

@app.delete("/sessions/{session_id}/players/{player_id}")
def remove_player_from_session(session_id: int, player_id: int):
    """Remove a player from a session."""
    session: Session = get_session(session_id)
    
    player: Player = next((player for player in session.session_players if player.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")
    
    session.session_players.remove(player)

    return {"message": f"{player.name} removed from session."}

@app.post("/sessions/{session_id}/players/{player_id}/action")
def handle_player_action(session_id: int, player_id: int, request: PlayerActionRequest):
    """Process an action for a specific player in a session."""
    session: Session = get_session(session_id)
    
    player: Player = next((player for player in session.session_players if player.id == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found.")

    if not session.current_game:
        raise HTTPException(status_code=400, detail="There is not a currently ongoing game.")

    if request.action == "test":
        player.current_action = request.action
        new_game_state = session.current_game.process_action(player)
        return new_game_state
    else:
        raise HTTPException(status_code=400, detail="Player action is not accepted.")
