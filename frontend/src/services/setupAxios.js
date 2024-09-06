import axios from 'axios';

const setupAxios = (navigate) => {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('token');
        navigate('/signin');
      }
      return Promise.reject(error);
    }
  );
};

export default setupAxios;
