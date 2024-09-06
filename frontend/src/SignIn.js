import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {Link} from 'react-router-dom';
import axios from 'axios';
import Layout from './Layout';

const SignIn = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/login/`, {
                username,
                password,
            });
            localStorage.setItem('token', response.data.token);
            navigate('/');
        } catch (err) {
            if (err.response) {
                setError(err.response.data.error || 'Login failed !');
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
            console.log(err);
        }
    };

    return (
        <Layout>
            <div className="auth-container">
                <h2>Sign In</h2>
                <form onSubmit={handleLogin} className="auth-form">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Login</button>
                </form>
                {error && <p className="error-message">{error}</p>}
                <p>Don't have an account? <Link to="/signup">Register</Link></p>
            </div>
        </Layout>
    );
};

export default SignIn;