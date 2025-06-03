import './app.css'
import Chat from './components/chat';

function App() {
  return (
    // Use Tailwind theme-aware classes instead of hardcoded background color
    <div className="h-screen w-full flex flex-col bg-app-bg dark:bg-app-bg-dark">
      {/* The Chat component now handles its own header/title and layout */}
      <Chat />
    </div>
  );
}

export default App
