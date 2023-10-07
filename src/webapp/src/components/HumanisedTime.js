export default function HumanisedTime(time) {
    const date = new Date(parseFloat(time) * 1000);
    return date.toLocaleString();
}