import './App.css'
import Chat from './components/chat';

function App() {
  return (
    // Use Tailwind classes for basic structure, ensuring it can go full height with the custom background
    <div className="h-screen w-full flex flex-col" style={{ backgroundColor: '#f3ebdf' }}>
      {/* The Chat component now handles its own header/title and layout */}
      <Chat />
    </div>
  );
}

export default App
