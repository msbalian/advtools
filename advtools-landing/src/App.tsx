import Hero from './components/Hero';
import Features from './components/Features';
import Comparison from './components/Comparison';
import FinalCTA from './components/FinalCTA';

function App() {
  return (
    <main className="min-h-screen font-sans selection:bg-brand-light selection:text-white">
      <Hero />
      <Features />
      <Comparison />
      <FinalCTA />
    </main>
  );
}

export default App;
