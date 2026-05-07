import { useState } from "react";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👨‍🍳 Chef IA prêt ! Écris une recette ou tes ingrédients."
    }
  ]);

  const [level, setLevel] = useState("debutant");
  const [gourmet, setGourmet] = useState(false);

  // 🧠 IA SIMPLE
  const generateResponse = (text) => {
    const t = text.toLowerCase();

    // 🌟 MODE ÉTOILÉ
    if (gourmet) {
      return `🌟 Chef étoilé : création gastronomique autour de "${text}" avec dressage élégant et équilibre des saveurs.`;
    }

    // 🍫 CHOCOLAT EXEMPLE
    if (t.includes("chocolat")) {
      if (level === "debutant") {
        return "🍪 Mélange chocolat + œufs + sucre. Cuisson 180°C 20 min.";
      }
      if (level === "pro") {
        return "🍰 Fondant chocolat avec texture maîtrisée et cuisson précise.";
      }
      return "👨‍🍳 Création avancée : ganache, cœur coulant, finition cacao.";
    }

    return `👨‍🍳 Recette générée pour niveau ${level} : ${text}`;
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    const botMsg = { role: "assistant", content: generateResponse(input) };

    setMessages([...messages, userMsg, botMsg]);
    setInput("");
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>

      <h1>👨‍🍳 Chef IA</h1>

      {/* LEVEL */}
      <div style={{ marginBottom: 10 }}>
        <button onClick={() => setLevel("debutant")}>Débutant</button>
        <button onClick={() => setLevel("pro")}>Pro</button>
        <button onClick={() => setLevel("expert")}>Expert</button>
      </div>

      {/* MODE ÉTOILÉ */}
      <button
        onClick={() => setGourmet(!gourmet)}
        style={{ marginBottom: 10 }}
      >
        🌟 Mode étoilé
      </button>

      {/* CHAT */}
      <div
        style={{
          border: "1px solid #ccc",
          height: 300,
          overflowY: "auto",
          padding: 10,
          marginBottom: 10
        }}
      >
        {messages.map((m, i) => (
          <p
            key={i}
            style={{
              textAlign: m.role === "user" ? "right" : "left",
              color: m.role === "user" ? "red" : "green"
            }}
          >
            {m.content}
          </p>
        ))}
      </div>

      {/* INPUT */}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Écris une recette..."
        style={{ width: "70%" }}
      />

      <button onClick={sendMessage}>Envoyer</button>

    </div>
  );
}