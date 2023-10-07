import React from 'react';
import {createRoot} from "react-dom/client";
import {
    createBrowserRouter,
    RouterProvider,
    Route,
    Link, BrowserRouter, Routes,
} from "react-router-dom";

import Home from "./pages/Home"
import Status from "./pages/Status"
import Header from "./components/Header";

const router = createBrowserRouter([
    {
        path: "/",
        element: (
            <Home/>
        ),
    },
    {
        path: "/status",
        element: <Status/>
    }
]);

createRoot(document.getElementById("root")).render(
    <BrowserRouter>
        <Header/>
        <main>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/status" element={<Status/>}/>
            </Routes>
        </main>
    </BrowserRouter>
);
