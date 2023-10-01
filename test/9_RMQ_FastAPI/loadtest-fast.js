import http from 'k6/http';

export const options = {
  vus: 1000,
  duration: '1m',
};

export default function () {
  http.get('http://192.168.1.43:8000/');
}
