import {sleep} from 'k6';
import http from 'k6/http';
import { Trend, Rate } from 'k6/metrics';

const hostRoot = "http://localhost";

const response_times = new Trend('response_times');
const percentile = (pct, arr) => {
    const sortedArr = arr.sort((a, b) => a - b);
    const index = Math.ceil(pct / 100 * sortedArr.length) - 1;
    return sortedArr[index];
};

const readMult = 0.7;
const executor = 'constant-arrival-rate';
const duration = "2m";
// Div by 3 to get per scenario-group execution rate
const executionRate = 733;
const preAllocatedVUs = 400;


export const options = {
    discardResponseBodies: true,
    scenarios: {
        getBattery: {
            executor: executor,
            exec: 'getBattery',
            duration: duration,
	    rate: Math.floor(executionRate * readMult),
	    timeUnit: "1s",
	    preAllocatedVUs: preAllocatedVUs
        },
        addBattery: {
            executor: executor,
            exec: 'addBattery',
            duration: duration,
	    rate: executionRate - Math.floor(executionRate*(readMult)),
	    timeUnit: "1s",
	    preAllocatedVUs: preAllocatedVUs
        },
        getUser: {
            executor: executor,
            exec: 'getUser',
            duration: duration,
	    rate: Math.floor(executionRate * readMult),
	    timeUnit: "1s",
	    preAllocatedVUs: preAllocatedVUs
        },
       addUser: {
            executor: executor,
            exec: 'addUser',
            duration: duration,
	    rate: executionRate - Math.floor(executionRate*(readMult)),
	    timeUnit: "1s",
	    preAllocatedVUs: preAllocatedVUs,
        },
         getStatus: {
             executor: executor,
             exec: 'getStatus',
             duration: duration,
             rate: executionRate,
             timeUnit: "1s",
             preAllocatedVUs: preAllocatedVUs
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
