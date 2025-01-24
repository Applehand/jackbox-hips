import "./App.css";
import { useState } from "react";

function Header() {
  return (
    <header>
      <h1>JAKEBOX</h1>
    </header>
  );
}

function Footer() {
  return <footer></footer>;
}

type LoginViewProps = {
  setJoin: (hasJoined: boolean) => void;
  setPlayers: (players: Array<Object>) => void;
};

function LoginView({ setJoin, setPlayers }: LoginViewProps) {
  const [name, setName] = useState("");
  const [accessCode, setAccessCode] = useState("");

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setName(event.currentTarget.value);
  };

  const handleAccessCodeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setAccessCode(event.currentTarget.value);
  };

  const handleJoin = async () => {
    try {
      const url = `http://localhost:8000/sessions/${accessCode}/players`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: name }),
      });

      if (!response.ok) {
        throw new Error("Failed to join game.");
      }

      const data = await response.json();
      console.log("Response from API:", data);

      setPlayers(data);
      setJoin(true);
    } catch (error) {
      console.error("Error during API call:", error);
    }
  };

  return (
    <div>
      <p>Enter the lobby code:</p>
      <input
        value={accessCode}
        onChange={handleAccessCodeChange}
        placeholder="Lobby Code"
      />
      <p>Pick a name:</p>
      <input value={name} onChange={handleNameChange} placeholder="Your Name" />
      <button onClick={handleJoin}>Join Lobby</button>
    </div>
  );
}

type LobbyViewProps = {
  players: Array<Object>;
};

function LobbyView({ players }: LobbyViewProps) {
  return (
    <div>
      <h2>Welcome to the Lobby!</h2>
      <ul>
        {players.map((player, index) => (
          <li key={index}>{JSON.stringify(player)}</li>
        ))}
      </ul>
    </div>
  );
}

function Main() {
  const [hasJoinedSession, setHasJoinedSession] = useState(false);
  const [players, setPlayers] = useState<Array<Object>>([]);

  return hasJoinedSession ? (
    <LobbyView players={players} /> 
  ) : (
    <LoginView setJoin={setHasJoinedSession} setPlayers={setPlayers} />
  );
}

export default function App() {
  return (
    <>
      <Header />
      <Main />
      <Footer />
    </>
  );
}
