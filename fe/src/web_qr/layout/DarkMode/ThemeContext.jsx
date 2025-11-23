import React, { createContext, useState, useEffect } from "react";

const ThemeContext = createContext();

const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState(localStorage.getItem("theme") || "dark");

    useEffect(() => {
        const container = document.querySelector(".cs-container");

        if (container) {
            container.setAttribute("data-theme", theme);
        }

        localStorage.setItem("theme", theme);

    }, [theme]);

    const toggleTheme = (newTheme) => {
        if (theme !== newTheme) {
            setTheme(newTheme);
            localStorage.setItem("theme", newTheme);
        }
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};

export { ThemeProvider, ThemeContext };
