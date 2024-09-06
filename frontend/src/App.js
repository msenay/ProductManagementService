import axios from 'axios';
import './styles/App.css';

// Axios token setup
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/signin';
    }
    return Promise.reject(error);
  }
);

function App() {
  return (
    <div>
      <h1>Learn React</h1>
      <p>Welcome to the App</p>
    </div>
  );
}

export default App;
