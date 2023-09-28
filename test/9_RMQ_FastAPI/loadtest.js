import http from 'k6/http';

export const options = {
  vus: 1000,
  duration: '1m',
};

export default function () {
  const payload = JSON.stringify({
    "capacity": 100,
    "charge": 69,
    "name"  : "Steven"
});
  const headers = { 'Content-Type': 'application/json' };
  http.get('http://192.168.1.43:8000/process');
}
