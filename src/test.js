import http from 'k6/http';
import { check, group, sleep, Trend } from 'k6';

let responseTimes = new Trend('response_times');

export let options = {
    vus: 10,
    duration: '30s',
};

export default function () {
    const randomAction = Math.random();

    if (randomAction < 0.7) {
        // Send a POST request 70% of the time
        group('POST Request', function () {
            let payload = {
                name: '',
                capacity: 0,
                charge: 0,
                owner: 0
            };

            let postRes = http.post('http://localhost:5000/api/v1/batteries', JSON.stringify(payload));

            check(postRes, {
                'POST Request is successful': (res) => res.status === 200,
            });

            responseTimes.add(postRes.timings.duration);
        });
    } else {
        // Send a GET request 30% of the time
        group('GET Request', function () {
            let getRes = http.get('http://localhost:5000/api/v1/batteries');

            check(getRes, {
                'GET Request is successful': (res) => res.status === 200,
            });

            responseTimes.add(getRes.timings.duration);
        });
    }

    // Introduce some delay between iterations
    sleep(1);
}

import http from 'k6/http';
import { check, group, sleep, Trend } from 'k6';

let responseTimes = new Trend('response_times');

export let options = {
    vus: 10,
    duration: '30s',
};

export default function () {
    const randomAction = Math.random();

    if (randomAction < 0.7) {
        // Send a POST request 70% of the time
        group('POST Request', function () {
            let payload = {
                name: '',
                capacity: 0,
                charge: 0,
                owner: 0
            };

            let postRes = http.post('http://localhost:5000/api/v1/batteries', JSON.stringify(payload));

            check(postRes, {
                'POST Request is successful': (res) => res.status === 200,
            });

            responseTimes.add(postRes.timings.duration);
        });
    } else {
        // Send a GET request 30% of the time
        group('GET Request', function () {
            let getRes = http.get('http://localhost:5000/api/v1/batteries');

            check(getRes, {
                'GET Request is successful': (res) => res.status === 200,
            });

            responseTimes.add(getRes.timings.duration);
        });
    }

    // Introduce some delay between iterations
    sleep(1);
}

export function handleSummary(data) {
    const percentiles = responseTimes.percentiles([25, 50, 75, 100]);

    console.log('25th percentile: ', percentiles[25]);
    console.log('Median: ', percentiles[50]);
    console.log('75th percentile: ', percentiles[75]);
    console.log('Fastest response time: ', percentiles[0]);
    console.log('Slowest response time: ', percentiles[100]);
}

