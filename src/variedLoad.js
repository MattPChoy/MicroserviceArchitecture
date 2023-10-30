import {sleep} from 'k6';
import http from 'k6/http';
import { Trend, Rate } from 'k6/metrics';

const hostRoot = "http://10.0.0.10";

const response_times = new Trend('response_times');
const percentile = (pct, arr) => {
    const sortedArr = arr.sort((a, b) => a - b);
    const index = Math.ceil(pct / 100 * sortedArr.length) - 1;
    return sortedArr[index];
};

const readMult = 0.85;
const executor = 'constant-vus';
const battery = 400;
const user = 200;
const status = 100;
const duration = "2m";

export const options = {
    discardResponseBodies: true,
    scenarios: {
        getBattery: {
            executor: 'constant-vus',
            exec: 'getBattery',
            vus: Math.floor(battery * readMult),
            duration: duration,
        },
        addBattery: {
            executor: 'constant-vus',
            exec: 'addBattery',
            vus: battery - Math.floor(battery * readMult),
            duration: duration
        },
        getUser: {
            executor: 'constant-vus',
            exec: 'getUser',
            vus: Math.floor(user * readMult),
            duration: duration
        },
        addUser: {
            executor: 'constant-vus',
            exec: 'addUser',
            vus: user - Math.floor(user * readMult),
            duration: duration
        },
         getStatus: {
             executor: 'constant-vus',
             exec: 'getStatus',
             vus: status,
             duration: duration
         }
    },
};




function getRandInt(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

export function getStatus() {
    let resp = http.get(`${hostRoot}:5000/api/v1/status/`);
    response_times.add(resp.timings.duration);
}

export function getBattery() {
    const uid = getRandInt(1, 1);
    http.get(`${hostRoot}:5000/api/v1/battery/?id=${uid}`)
}

export function addBattery() {
    const payload = JSON.stringify({
        "name": "Joe",
        "capacity": 1,
        "charge": 12,
        "owner": 69
    })
    const headers = {'Content-Type': 'application/json'};
    http.post(
        `${hostRoot}:5000/api/v1/battery/`,
        payload,
        {
            headers: {'Content-Type': 'application/json'},
        }
    )
}

export function getUser() {
    const uid = getRandInt(1, 1);
    http.get(`${hostRoot}:5000/api/v1/user/?id=${uid}`)
}

export function addUser() {
    const payload = JSON.stringify({
        firstname: "k",
        lastname: "j",
        password: "p",
        email: "0",
        region: 0,
    })
    const headers = {'Content-Type': 'application/json'};
    http.post(
        `${hostRoot}:5000/api/v1/user/`,
        payload,
        {
            headers: {'Content-Type': 'application/json', Accept: "*/*"},
        }
    )
}
