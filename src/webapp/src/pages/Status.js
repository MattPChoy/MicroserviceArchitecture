import {useEffect} from "react";

export default function Status() {
    useEffect(() => {
        fetch("/api/v1/status", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            mode: 'no-cors'
        }).then((r) => {
            console.log(r);
            document.getElementById("fuckyou").innerHTML = r;
            //return r.json()
        })//.then((r) => {
        //     console.log(r);
        //
        // });
    });

    return (
        <div id="fuckyou"></div>
    );
}