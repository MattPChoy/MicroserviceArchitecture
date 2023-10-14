import AddBatteryForm from "../components/Battery/AddBatteryForm.tsx";
import "../Common.css"

import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent'
import Typography from '@mui/material/Typography';
import {useEffect, useState} from "react";

// eslint-disable-next-line react/prop-types
function Battery({name, capacity}) {
    return (
        <Card sx={{maxWidth: 345}} style={{backgroundColor: "#1D2129", margin: "20px 0 0 0"}}>
            <CardContent>
                <Typography sx={{fontSize: 14}} gutterBottom>
                    Battery • {name}
                </Typography>

                <Typography variant="body2">
                    <b>Capacity:</b> {capacity}
                </Typography>
            </CardContent>
        </Card>
    );
}

async function getBatteries() {
    let batteries = await fetch('http://localhost:5000/api/v1/battery/?owner_id=0', {
        method: "GET",
    });

    batteries = {loaded: true, data: (await batteries.json()).battery_data};
    return batteries;
}

function BatteryList() {
    const [batteries, setBatteries] = useState({loaded: false});
    useEffect(() => {
        getBatteries().then((r) => setBatteries(r));

        setInterval(() => {
            getBatteries().then((r) => setBatteries(r));
        }, 1000);
    }, [])

    console.log(batteries);
    if (batteries.loaded) {
        if (batteries.data.length === undefined || batteries.data.length === 0) {
            return <div>no batteries</div>;
        }

        return batteries.data.map((battery) => {
            return <Battery name={battery.name} capacity={battery.capacity} key={battery.id}/>;
        })
    } else {
        return <div>loading...</div>;
    }
}

export default function Home() {
    return (
        <main>
            <h1>Home</h1>
            <AddBatteryForm/>
            <BatteryList/>
        </main>);
}