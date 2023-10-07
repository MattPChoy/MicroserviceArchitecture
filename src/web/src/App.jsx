import './App.css'
import {BrowserRouter, createBrowserRouter, Route, Routes} from "react-router-dom";
import Header from "./components/Header.jsx";
import Home from "./pages/Home.jsx";
import Status from "./pages/Status.jsx";

function App() {
    return (
        <BrowserRouter>
        <Header/>
        <main>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/status" element={<Status/>}/>
            </Routes>
        </main>
    </BrowserRouter>
    )
}

export default App
