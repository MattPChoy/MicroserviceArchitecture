import {useEffect, useState} from "react";

export default function Status() {
    const [services, setServices] = useState([]);
    useEffect(() => {
        const data = fetch(
            "http://localhost:5000/api/v1/status/",
            {
                    mode: 'cors',
                    headers: {
                        'Access-Control-Allow-Origin': "*",
                    }
                }
        ).then((r) => {
            return r.json()
        }).then((r) => {
            setServices(r);
            console.log(r);
            document.getElementById("fuckyou").innerHTML = r;
        });
    });

    return (
        <div>
            <p>waawa</p>
            <div id="fuckyou"/>
        </div>
    );
}