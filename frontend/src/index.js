import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import './index.css';
import Products from './Products';
import SingIn from './SignIn';
import SignUp from './SignUp';
import setupAxios from './setupAxios';



const MainApp = () => {
  const navigate = useNavigate();
  setupAxios(navigate);

  return (
    <Routes>
        <Route path="/" element={<Products />} />
        <Route path="/signin" element={<SingIn />} />
        <Route path="/signup" element={<SignUp />} />
    </Routes>
  );
};

ReactDOM.render(
  <React.StrictMode>
    <Router>
      <MainApp />
    </Router>
  </React.StrictMode>,
  document.getElementById('root')
);