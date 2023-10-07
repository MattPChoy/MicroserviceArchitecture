import HumanisedTime from "./HumanisedTime";

export default function ServiceCard({name, time, ip}) {
    const now = new Date();
    const lastSeen = new Date(parseFloat(time) * 1000);
    const diff = now - lastSeen;

    const r = "🔴";
    const g = "🟢";
    const y = "🟠";

    let indicator = g
    if (diff > 60000) {
        // If within 1 minute then is ok
        indicator = g
    } else if (diff > 1000 * 5 * 60) {
        // If within 5 min starting to get a bit concerned
        indicator = y;
    } else {
        indicator = r;
    }

    return (
        <div className='card'>
            <h2>{name}</h2>
            <p>{indicator} {HumanisedTime(time)}</p>
        </div>
    );
}