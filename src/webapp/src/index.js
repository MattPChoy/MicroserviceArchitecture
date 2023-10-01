import React from 'react';
import {createRoot} from "react-dom/client";
import {
    createBrowserRouter,
    RouterProvider,
    Route,
    Link,
} from "react-router-dom";

import Home from "./pages/Home"
import Status from "./pages/Status"

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
    <RouterProvider router={router}/>
);
