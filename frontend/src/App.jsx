import { useState, useEffect } from 'react';
import axios from 'axios';
// import * as microsoftTeams from "@microsoft/teams-js"; // DESCOMENTAR tras instalar: npm install @microsoft/teams-js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';


////////////////// EJEMPLO HECHO POR GEMINI PARA PROBAR QUE FUNCIONE NGROK /////////////////////////

// npm run dev
// http://localhost:5173/

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {

  const [burnoutData, setBurnoutData] = useState(null);
  const [currentTeam, setCurrentTeam] = useState('Team-Alpha');
  const [searchInput, setSearchInput] = useState('');
  const [inTeams, setInTeams] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');


  useEffect(() => {
    console.log("Modo Navegador (Teams SDK desactivado temporalmente)");
  }, []);


  const fetchTeamData = async (teamName) => {
    if (!teamName) return;
    setErrorMsg('');

    try {

      const response = await axios.get(
        `http://localhost:8000/burnout/team?team=${teamName}&period=1m`
      );

      console.log("Datos recibidos:", response.data);
      setBurnoutData(response.data.burnout);
      setCurrentTeam(teamName);

    } catch (error) {
      console.error("Error conectando:", error);
      setBurnoutData(null);
      setErrorMsg(`No se encontraron datos para el equipo "${teamName}".`);
    }
  };


  useEffect(() => {
    fetchTeamData('Team-Alpha');
  }, []);


  const handleSearch = (e) => {
    e.preventDefault();
    fetchTeamData(searchInput);
  };


  const chartData = {
    labels: ['Amabilidad (Media)', 'Sarcasmo (Media)', 'Toxicidad (Media)'],
    datasets: [
      {
        label: `Métricas del Equipo: ${currentTeam}`,
        data: burnoutData
          ? [burnoutData.politeness, burnoutData.sarcasm, burnoutData.toxicity]
          : [0, 0, 0],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(255, 99, 132, 0.6)'
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(255, 99, 132, 1)'
        ],
        borderWidth: 1,
      },
    ],
  };


  return (
    <div style={{ fontFamily: 'Segoe UI, sans-serif', padding: '20px', maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ textAlign: 'center', color: '#444' }}>Team Well-being Dashboard</h1>

      {/* Search Bar */}
      <div style={{ background: '#f0f2f5', padding: '20px', borderRadius: '8px', marginBottom: '20px', textAlign: 'center', border: '1px solid #ddd' }}>
        <p style={{ margin: '0 0 10px 0', fontWeight: '600', color: '#555' }}>🏢 Select Department/Team:</p>
        <form onSubmit={handleSearch} style={{ display: 'flex', justifyContent: 'center', gap: '10px' }}>
          <input
            type="text"
            placeholder="Ex: Team-Alpha, Team-Beta..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            style={{ padding: '10px', width: '250px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
          <button type="submit" style={{ padding: '10px 20px', background: '#0078d4', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
            Analyze
          </button>
        </form>
        <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
          Intenta buscar: <strong>Team-Alpha</strong>, <strong>Team-Beta</strong> o <strong>Team-Gamma</strong>
        </div>
      </div>

      {/* Error Messages */}
      {errorMsg && (
        <div style={{ padding: '15px', background: '#fde7e9', color: '#a80000', borderRadius: '4px', marginBottom: '20px', textAlign: 'center' }}>
          {errorMsg}
        </div>
      )}

      {/* Chart Container */}
      <div style={{ background: 'white', padding: '30px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        {burnoutData ? <Bar data={chartData} /> : <p style={{ textAlign: 'center', color: '#666' }}>Loading metrics...</p>}
      </div>

      {/* Footer */}
      <div style={{ marginTop: '30px', borderTop: '1px solid #eee', paddingTop: '10px', fontSize: '12px', color: '#888', textAlign: 'center' }}>
        <p>Status: {inTeams ? "Connected to Teams SDK" : " Browser Mode (Localhost)"}</p>
        <p>Backend: Connected to http://localhost:8000</p>
      </div>
    </div>
  );
}

export default App;
