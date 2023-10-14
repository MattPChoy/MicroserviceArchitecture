import TextField from '@mui/material/TextField';
import "./AddBatteryForm.css";
import {useState} from "react";

export default function AddBatteryForm() {
    const [formData, setFormData] = useState({
        capacity: "", name: ""
    })
    function handleFormSubmit(event) {
        event.preventDefault();
        const data = {
            name: formData.name,
            capacity: formData.capacity,
            charge: 0,
            owner: 0,
        }

        fetch('http://localhost:5000/api/v1/battery/', {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "Access-Control-Allow-Origin": "*"
            }
        }).then((data) => {
            console.log(data);
        });
    }

    const formIsInvalid = formData.capacity.length === 0 || formData.name.length === 0;

    function handleChange(e) {
        setFormData({
            ...formData,
            [e.target.id]: e.target.value
        });
    }

    return (
        <form className="form addBatteryForm">
            <h2>Add Battery</h2>
            <TextField id='name' label='Battery Short Name' style={{"paddingBottom": '30px', color: 'white'}}
                       variant='outlined' sx={{input: {color: 'white'}}} InputLabelProps={{style: {color: 'white'}}} required={true}
                        value={formData.name} onChange={handleChange}/>
            <TextField id='capacity' label='Battery Capacity' style={{"paddingBottom": '30px'}}
                       variant='outlined' sx={{input: {color: 'white'}}} InputLabelProps={{style: {color: 'white'}}} required={true}
                        value={formData.capacity} onChange={handleChange} type='number'/>
            <button onClick={handleFormSubmit} style={{"width": "300px"}} className="formSubmit" disabled={formIsInvalid}>Add Battery</button>
        </form>
    );
}