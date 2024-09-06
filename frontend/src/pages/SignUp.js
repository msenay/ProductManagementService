import React, {useState} from 'react';
import axios from 'axios';
import {Link} from 'react-router-dom';
import {useNavigate} from 'react-router-dom';
import Layout from '../components/Layout';

function SignUp() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            await axios.post(`${process.env.REACT_APP_API_URL}/signup/`, {
                username,
                email,
                password,
                first_name: firstName,
                last_name: lastName,
            });
            navigate('/signin');
        } catch (err) {
            if (err.response && err.response.data) {
                const responseErrors = err.response.data;
                if (responseErrors.username) {
                    setError(responseErrors.username[0]);
                } else if (responseErrors.email) {
                    setError(responseErrors.email[0]);
                } else if (responseErrors.password) {
                    setError(responseErrors.password[0]);
                } else {
                    setError('Registration failed.');
                }
            } else {
                setError('An unexpected error occurred. Please try again.');
            }
        }
    };

    return (
        <Layout>
            <div className="auth-container">
                <h2>Register</h2>
                <form onSubmit={handleSubmit} className="auth-form">
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <input
                        type="text"
                        placeholder="First Name"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        required
                    />
                    <input
                        type="text"
                        placeholder="Last Name"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        required
                    />
                    <button type="submit">Register</button>
                </form>
                {error && <p className="error-message">{error}</p>}
                <p>Already have an account? <Link to="/signin">Login</Link></p>
            </div>
        </Layout>
    );
}

export default SignUp;
