import TextField from '@mui/material/TextField';
import "./AddBatteryForm.css";
import {useState} from "react";

export default function AddBatteryForm() {
    const [isInvalid, setIsInvalid] = useState({});
    const formIsInvalid = Object.keys(isInvalid).map(
        (value: string) => isInvalid[value]).some((value: boolean) => {
        return value === undefined || value === false
    }) || Object.keys(isInvalid).length === 0;

    console.log(isInvalid);
    console.log(formIsInvalid);

    function handleFormSubmit(e : any) {
        e.preventDefault();
        const formData = {
            nickname: document.getElementById("batteryNickname").value,
            capacity: document.getElementById("batteryCapacity").value,
            charge: 0,
            owner_id: 0,
        }

        fetch('http://localhost:3001/battery', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        }).then((response) => {
            console.log(response);
            if (response.status === 200) {
                alert('Battery added successfully!');
            }
        });
    }

    return (
        <form className="form addBatteryForm">
            <h2>Add Battery</h2>
            <TextField id='batteryNickname' label='Battery Short Name' style={{"paddingBottom": '30px'}}
                       variant='outlined'/>
            <TextField id='batteryCapacity' label='Battery Capacity' style={{"paddingBottom": '30px'}}
                       variant='outlined'/>
            <button onClick={handleFormSubmit} style={{"width": "300px"}} className="formSubmit">Add Battery</button>
        </form>
    );
}