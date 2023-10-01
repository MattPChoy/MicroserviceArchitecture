import { sleep } from 'k6';
import http from 'k6/http';

export const options = {
    discardResponseBodies: true,
    scenarios: {
        getBattery: {
            executor: 'constant-vus',
            exec: 'getBattery',
            vus: 500,
            duration: '2m',
        },
        getUser: {
            executor: 'constant-vus',
            exec: 'getUser',
            vus: 500,
            duration: '2m'
        },
	    getStatus: {
            executor: 'constant-vus',
            exec: 'getStatus',
            vus: 1000,
	        duration: '2m'
	    }
    },
};

function getRandInt(min, max){
	return Math.floor(Math.random() * (max-min) + min);
}

export function getStatus() {
    http.get(`http://localhost:5000/api/v1/status/`, {
	    tags: {my_custom_tag: 'getStatus'},
    })
    sleep(0.5)
}

export function getBattery() {
    const uid=getRandInt(1,1000);
    //const uid=3;
    http.get(`http://localhost:5000/api/v1/battery/?id=${uid}`, {
        tags: {my_custom_tag: 'getBattery'},
    })
    sleep(0.5)
}

export function getUser() {
    const uid=getRandInt(1,1000);
    //const uid=3;
    http.get(`http://localhost:5000/api/v1/user/?id=${uid}`, {
        tags: {my_custom_tag: 'getUser'},
    })
    sleep(0.5)
}
