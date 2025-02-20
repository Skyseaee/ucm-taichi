import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { login } from '../../Services/auth';
import './Login.css';

const Login = () => {
  const { setUser } = useAuth();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = await login(credentials);
      setUser(userData);
      setError('');
    } catch (error) {
      setError(error.response?.data?.error || 'Login failed');
    }
  };

  return (
    <div className="login-container">
      <h2 className="login-title">Welcome Back</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="text"
            className="form-input"
            placeholder="Username"
            value={credentials.username}
            onChange={(e) => setCredentials({...credentials, username: e.target.value})}
          />
        </div>
        
        <div className="input-group">
          <input
            type="password"
            className="form-input"
            placeholder="Password"
            value={credentials.password}
            onChange={(e) => setCredentials({...credentials, password: e.target.value})}
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" className="submit-btn">
          Sign In
        </button>
      </form>
    </div>
  );
};

export default Login;