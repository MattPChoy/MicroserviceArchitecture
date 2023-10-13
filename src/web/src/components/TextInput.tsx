// @ts-ignore
import React, {ChangeEventHandler, useEffect, useState} from "react";
import "./Input.css";
import {transformWithEsbuild} from "vite";

export default function TextInput(props: any) {
    useEffect(() => {
        // Use undefined here to indicate that the text field hasn't been edited yet,
        // but populate it, so we know what text fields exist.
        props.isInvalid[props.label] = undefined;
    }, []);

    function customValidation(e: any) {
        if (props.customValidation === undefined) {
            return true;
        }

        return props.customValidation(e);
    }

    function inputValidation(e: any) {
        const propIsInvalid = e.target.value.length === 0 || customValidation(e);
        props.setIsInvalid({...props.isInvalid, [props.label]: propIsInvalid});
    }

    const showWarningMessage = props.isInvalid[props.label] || props.isInvalid[props.label] !== undefined;

    return (
        <div className="formElementContainer">
            <label>{props.label}</label>
            <input type="text" onChange={inputValidation}/>
            <span className="formValidation">{showWarningMessage ? props.validationMessage : ''}</span>
        </div>
    )
}