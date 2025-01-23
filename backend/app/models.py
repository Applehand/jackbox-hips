from pydantic import BaseModel
from typing import Literal, List, Optional
from enum import Enum

class GameType(str, Enum):
    """Enumeration of possible game types."""
    hiders_and_seekers = "hiders_and_seekers"
    werewolf = "werewolf"

class Player(BaseModel):
    """Represents a player in a session."""
    name: str
    role: Literal["werewolf", "civilian", "in_lobby"] = "in_lobby"
    id: int
    current_action: Optional[Literal["test"]] = "test"

class CreatePlayerRequest(BaseModel):
    """Request model for creating a new player."""
    name: str

class PlayerActionRequest(BaseModel):
    """Request model for a player action."""
    action: Literal["test"]

class Session(BaseModel):
    """Represents a game session."""
    session_id: int
    access_code: str
    host: Player
    session_players: List[Player] = []
    player_id_counter: int = 1
    game_type: Optional[GameType] = None
    current_game: Optional['Game'] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_players = [self.host]

    def to_dict(self):
        """Converts the session data to a dictionary."""
        return {
            "session_id": self.session_id,
            "access_code": self.access_code,
            "host": self.host.model_dump(),
            "players": [player.model_dump() for player in self.session_players],
            "game_type": self.current_game.game_type if self.current_game else None,
            "current_game": self.current_game.model_dump() if self.current_game else None
        }

class CreateSessionRequest(BaseModel):
    """Request model for creating a new session."""
    host_name: str

class CreateSessionResponse(BaseModel):
    """Response model for creating a new session."""
    session_id: int
    access_code: str
    host_player: Player

class GetSessionDataResponse(BaseModel):
    """Response model for retrieving session data."""
    session_id: int
    access_code: str
    current_game: Optional['Game']
    session_players: List[Player]

class Game(BaseModel):
    """Represents a game within a session."""
    game_type: GameType
    game_players: List[Player]
    game_state: dict = {}

    def start_game(self):
        """Starts the game and assigns roles to players."""
        for player in self.game_players:
            player.role = "civilian"
        return self.game_state
    
    def end_game(self):
        """Ends the game and resets player roles."""
        self.game_type = None
        for player in self.game_players:
            player.role = "in_lobby"
        self.game_state = {}

    def process_action(self, player: Player):
        """
        Processes an action performed by a player.

        Args:
            player (Player): The player performing the action.
        
        Returns:
            dict: The updated game state.
        """
        target_player = next((p for p in self.game_players if p.id == player.id), None)
        
        if not target_player:
            raise ValueError(f"Player with ID {player.id} not found in the session.")
        
        target_player.current_action = player.current_action

        # update the game state here

        return { "game_state": self.game_state }
