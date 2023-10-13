export default function Battery(props) {
    return (<div>
        <h1>{props.nickname}</h1>
        <span><b>Capacity:</b> {{props?.capacity}} kw/h</span>
        <span><b>Charge:</b> {{props?.charge}} kw/h</span>
    </div>);
}