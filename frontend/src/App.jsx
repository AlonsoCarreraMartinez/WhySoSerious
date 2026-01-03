import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

  // Backend URL (Adjust port if necessary)
  const API_URL = "http://localhost:8000/teams/dashboard";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(API_URL);
        setTeams(response.data);
        setLoading(false);
      } catch (error) {
        console.error("Error connecting to backend:", error);
        setLoading(false);
      }
    };

    fetchData();
    
    // Optional: Auto-refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div style={styles.container}><h1>Loading data...</h1></div>;

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>WhySoSerious Dashboard</h1>
        <p>Real-time monitoring of team status</p>
      </header>

      <div style={styles.grid}>
        {teams.map((team) => (
          <div key={team._id} style={styles.card}>
            <h2 style={styles.teamName}>{team._id}</h2>
            
            <div style={styles.metricsContainer}>
              {/* POLITENESS */}
              <MetricBar 
                label="Politeness" 
                value={team.burnout_mean?.politeness || 0} 
                color="#4CAF50" // Green
              />
              
              {/* SARCASM */}
              <MetricBar 
                label="Sarcasm" 
                value={team.burnout_mean?.sarcasm || 0} 
                color="#FF9800" // Orange
              />

              {/* TOXICITY */}
              <MetricBar 
                label="Toxicity" 
                value={team.burnout_mean?.toxicity || 0} 
                color="#F44336" // Red
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Sub-component for progress bars
const MetricBar = ({ label, value, color }) => {
  // We calculate percentage based on a scale of 0 to 5.
  // If your scores go up to 10, change '5' to '10' below.
  const percentage = Math.min((value / 5) * 100, 100); 

  return (
    <div style={{ marginBottom: '15px' }}>
      <div style={styles.labelRow}>
        <span>{label}</span>
        <span style={{ fontWeight: 'bold' }}>{value.toFixed(2)}</span>
      </div>
      <div style={styles.progressBarBg}>
        <div 
          style={{ 
            ...styles.progressBarFill, 
            width: `${percentage}%`, 
            backgroundColor: color 
          }} 
        />
      </div>
    </div>
  );
};

// Basic CSS-in-JS styles
const styles = {
  container: {
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    padding: '40px',
    backgroundColor: '#f4f4f9',
    minHeight: '100vh',
  },
  header: {
    textAlign: 'center',
    marginBottom: '50px',
  },
  title: {
    color: '#333',
    fontSize: '2.5rem',
    marginBottom: '10px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '30px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '15px',
    padding: '25px',
    boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
    transition: 'transform 0.2s',
  },
  teamName: {
    marginTop: 0,
    color: '#2c3e50',
    borderBottom: '2px solid #eee',
    paddingBottom: '15px',
    marginBottom: '20px',
  },
  metricsContainer: {
    display: 'flex',
    flexDirection: 'column',
  },
  labelRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '5px',
    fontSize: '0.9rem',
    color: '#555',
  },
  progressBarBg: {
    height: '10px',
    backgroundColor: '#e0e0e0',
    borderRadius: '5px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: '5px',
    transition: 'width 0.5s ease-in-out',
  },
};

export default App;