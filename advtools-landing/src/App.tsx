import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Roadmap from './pages/Roadmap';

function App() {
  return (
    <Router>
      <main className="min-h-screen font-sans selection:bg-brand-light selection:text-white">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/roadmap" element={<Roadmap />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
