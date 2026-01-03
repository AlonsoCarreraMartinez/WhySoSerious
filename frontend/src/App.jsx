import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);

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
              <MetricBar 
                label="Politeness" 
                value={team.burnout_mean?.politeness || 0} 
                color="#4CAF50" 
              />
              <MetricBar 
                label="Sarcasm" 
                value={team.burnout_mean?.sarcasm || 0} 
                color="#FF9800" 
              />
              <MetricBar 
                label="Toxicity" 
                value={team.burnout_mean?.toxicity || 0} 
                color="#F44336" 
              />
            </div>

            <div style={styles.channelsSection}>
                <h3 style={styles.channelsTitle}>Active Channels</h3>
                <div style={styles.channelsList}>
                    {team.channel_details && team.channel_details.length > 0 ? (
                        team.channel_details.map((channel) => (
                            <div key={channel._id} style={styles.channelBox}>
                                <div style={styles.channelNameRow}>
                                    <strong># {channel.name}</strong>
                                </div>
                                <MetricBar 
                                    label="Politeness" 
                                    value={channel.burnout_mean?.politeness || 0} 
                                    color="#4CAF50" 
                                    isSmall
                                />
                                <MetricBar 
                                    label="Sarcasm" 
                                    value={channel.burnout_mean?.sarcasm || 0} 
                                    color="#FF9800" 
                                    isSmall
                                />
                                <MetricBar 
                                    label="Toxicity" 
                                    value={channel.burnout_mean?.toxicity || 0} 
                                    color="#F44336" 
                                    isSmall
                                />
                            </div>
                        ))
                    ) : (
                        <span style={styles.noChannels}>No channels linked</span>
                    )}
                </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}

const MetricBar = ({ label, value, color, isSmall }) => {
  const percentage = Math.min((value / 5) * 100, 100);
  
  const height = isSmall ? '6px' : '10px';
  const fontSize = isSmall ? '0.75rem' : '0.9rem';
  const marginBottom = isSmall ? '6px' : '15px';

  return (
    <div style={{ marginBottom: marginBottom }}>
      <div style={{ ...styles.labelRow, fontSize: fontSize }}>
        <span>{label}</span>
        <span style={{ fontWeight: 'bold' }}>{value.toFixed(2)}</span>
      </div>
      <div style={{ ...styles.progressBarBg, height: height }}>
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
    gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
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
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
  },
  teamName: {
    marginTop: 0,
    color: '#2c3e50',
    borderBottom: '2px solid #eee',
    paddingBottom: '15px',
    marginBottom: '20px',
  },
  metricsContainer: {
    marginBottom: '20px',
  },
  labelRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '5px',
    color: '#555',
  },
  progressBarBg: {
    backgroundColor: '#e0e0e0',
    borderRadius: '5px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: '5px',
    transition: 'width 0.5s ease-in-out',
  },
  
  channelsSection: {
    borderTop: '1px solid #eee',
    paddingTop: '15px',
    marginTop: '10px',
  },
  channelsTitle: {
    fontSize: '0.85rem',
    textTransform: 'uppercase',
    color: '#888',
    marginBottom: '15px',
    letterSpacing: '1px',
  },
  channelsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  channelBox: {
    backgroundColor: '#f8f9fa',
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #e9ecef',
  },
  channelNameRow: {
    marginBottom: '10px',
    fontSize: '0.9rem',
    color: '#333',
  },
  noChannels: {
    fontStyle: 'italic',
    color: '#aaa',
    fontSize: '0.9rem',
  }
};

export default App;