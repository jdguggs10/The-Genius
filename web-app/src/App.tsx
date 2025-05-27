import './App.css'
import Chat from './components/chat';

function App() {
  return (
    // Use Tailwind classes for basic structure, ensuring it can go full height
    <div className="h-screen flex flex-col">
      {/* The Chat component now handles its own header/title and layout */}
      <Chat />
    </div>
  );
}

export default App
