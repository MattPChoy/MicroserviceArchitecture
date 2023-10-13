import TextInput from "../TextInput";
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

    return (
        <form className="form addBatteryForm">
            <h2>Add Battery</h2>
            <TextInput label="Battery Nickname" validationMessage="Battery name is required and cannot be empty."
                       isInvalid={isInvalid} setIsInvalid={setIsInvalid}/>
            <TextInput label="Battery Capacity" validationMessage="Battery capacity is required and cannot be empty."
                       isInvalid={isInvalid} setIsInvalid={setIsInvalid} />
            <TextInput label="Battery Voltage" validationMessage="Battery voltage is required and cannot be empty."
                       isInvalid={isInvalid} setIsInvalid={setIsInvalid}/>

            <button disabled={formIsInvalid} style={{"width": "300px"}} className="formSubmit">Add Battery</button>
        </form>
    );
}