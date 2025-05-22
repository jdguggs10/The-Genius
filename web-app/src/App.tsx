import { useState } from 'react'
import './App.css'
import Chat from './components/chat';

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>The Genius</h1>
      </header>
      <main>
        <Chat />
      </main>
    </div>
  );
}

export default App
