import {sleep} from 'k6';
import http from 'k6/http';

const readMult = 1;
const battery = 30;
const user = 30;
const status = 15;

const duration = '2m';
const executor = 'constant-vus';

export const options = {
    discardResponseBodies: true,
    scenarios: {
        getBattery: {
            executor: 'constant-vus',
            exec: 'getBattery',
            vus: Math.floor(battery * readMult),
            duration: duration,
        },
//        addBattery: {
//            executor: 'constant-vus',
//            exec: 'addBattery',
//            vus: battery - Math.floor(battery * readMult),
//            duration: duration
//        },
        getUser: {
            executor: 'constant-vus',
            exec: 'getUser',
            vus: Math.floor(user * readMult),
            duration: duration
        },
        //addUser: {
        //    executor: 'constant-vus',
        //    exec: 'addUser',
        //    vus: user - Math.floor(battery * readMult),
        //    duration: duration
        //},
        // getStatus: {
        //     executor: 'constant-vus',
        //     exec: 'getStatus',
        //     vus: status,
        //     duration: duration
        // }
    },
};




function getRandInt(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

export function getStatus() {
    http.get(`http://localhost:5000/api/v1/status/`)
}

export function getBattery() {
    const uid = getRandInt(1, battery);
    http.get(`http://localhost:5000/api/v1/battery/?id=${uid}`)
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
        `http://localhost:5000/api/v1/battery/`,
        payload,
        {
            headers: {'Content-Type': 'application/json'},
        }
    )
}

export function getUser() {
    const uid = getRandInt(1, user);
    http.get(`http://localhost:5000/api/v1/user/?id=${uid}`)
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
        `http://localhost:5000/api/v1/user/`,
        payload,
        {
            headers: {'Content-Type': 'application/json', Accept: "*/*"},
        }
    )
}
