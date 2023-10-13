import {useEffect, useState} from "react";
import ServiceCard from "../components/ServiceCard.jsx";
import "../Common.css"

function updateServices(setServices) {
    console.log("Updating alive services")
    fetch(
        "http://localhost:5000/api/v1/status/",
    ).then((r) => {
        return r.json()
    }).then((r) => {
        setServices(r);
    });

    setTimeout(() => {
        updateServices(setServices)
    }, 3000);
}

export default function Status() {
    const [services, setServices] = useState([]);
    console.log("HI")

    useEffect(() => {
        updateServices(setServices)
    }, []);

    const serviceCards = Object.keys(services).map((service_ip) => {
        return (
            <ServiceCard key={service_ip} {...services[service_ip]}/>
        );
    });

    return (
        <div className='serviceCardContainer'>
            {serviceCards}
        </div>
    );
}