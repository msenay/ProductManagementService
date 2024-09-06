// src/Layout.js
import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const Layout = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  const handleLogout = async () => {
    try {
      await axios.post(`${process.env.REACT_APP_API_URL}/logout/`, {}, {
        headers: { Authorization: `Token ${localStorage.getItem('token')}` },
      });
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      navigate('/signin');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <div>
      {/* Header */}
      <header className="header">
        <div className="logo">
          <Link to="/">
            <img src="/ounass.png" alt="Ounass" />
          </Link>
        </div>

        {/* Logout is visible only if user has token */}
        {isAuthenticated && (
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        )}
      </header>

      {/* Main content */}
      <main>
        {children}
      </main>

      {/* Footer */}
      <footer>
        <p>© 2024 Ounass. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout;