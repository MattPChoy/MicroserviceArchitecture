import logo from './logo.svg';
import './App.css';
import {useEffect, useState} from "react";


function updateServiceList(setServices) {
    fetch("/services", {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json"
        }
    }).then((r) => {
        try {
            return r.json();
        } catch (e) {
            return {};
        }
    }).then((services) => {
        setServices(services);
    }).then(
        setTimeout(() => {
            updateServiceList(setServices)
        }, 5000)
    );
}

function ServiceCard(props) {
    const lastResponseDate = new Date(props.last_resp * 1000);
    const now = Date.now();
    const err = "🔴";
    const warn = "🟠"
    const ok = "🟢";

    let status;

    if (now - lastResponseDate < 60 * 1000) {
        status = ok;
    } else if (now - lastResponseDate < 5 * 60 * 1000) {
        status = warn;
    } else {
        status = err;
    }

    return (
        <div className="serviceCard">
            <h2>{props.service_name}</h2>
            <p><strong>IP</strong>: {props.ip}</p>
            <p><strong>Last Response</strong>:{status} {lastResponseDate.toLocaleString()} </p>
        </div>
    );
}

function App() {
    const [services, setServices] = useState([]);

    useEffect(() => {
        updateServiceList(setServices);
    }, [])

    return (
        <div className="App">
            <h1>System Status</h1>
            <div className="servicesContainer">
                {Object.keys(services).map((s) => {
                    return <ServiceCard key={s.ip} {...services[s]} />
                })}
            </div>
        </div>
    );
}

export default App;
