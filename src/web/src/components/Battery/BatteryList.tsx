import {useEffect, useState} from "react";
import Battery from "./Battery";

function retrieveBatteries() {
    let batteries = undefined;
    fetch('http://localhost:3001/battery', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    }).then((response) => {
        console.log(response);
        if (response.status === 200) {
            return response.json();
        }
    }).then((data) => {
        console.log(data);
        batteries = data;
    });

    return batteries;
}

export default function BatteryList() {
    const [batteries, setBatteries] = useState([]);

    useEffect(() => {
        setBatteries(retrieveBatteries());
    }, []);


    const batteryElems = batteries.map((battery) => {
        return <Battery {...battery} key={battery.id}/>
    });


    return (
        <div>
            {batteryElems}
        </div>
    )
}