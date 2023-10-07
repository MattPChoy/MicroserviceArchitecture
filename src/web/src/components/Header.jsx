import "./Header.css";
import battery from "../battery.png"
import {useNavigate} from "react-router-dom";

export default function Header() {
    const navigate = useNavigate();

    return (
        <div className='header'>
            <img className='headerImg' src={battery} onClick={() => {navigate("/")}}/>
        </div>
    );
}