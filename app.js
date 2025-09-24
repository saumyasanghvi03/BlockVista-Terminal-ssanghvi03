import React from 'react';
import MarketDashboard from './components/MarketDashboard';
import NewsFeed from './components/NewsFeed';
import ChartView from './components/ChartView';
import Alerts from './components/Alerts';
import './styles/main.css';

function App() {
  return (
    <div className="container">
      <h1>BlockVista Terminal</h1>
      <div className="dashboard">
        <MarketDashboard />
        <NewsFeed />
      </div>
      <div className="dashboard">
        <ChartView />
        <Alerts />
      </div>
    </div>
  );
}

export default App;
