import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import GlobalStyles from './main/GlobalStyles'
import { ThemeProvider } from './web_qr/layout/DarkMode/ThemeContext.jsx'
import "./language/i18n.js";
import { SocketProvider } from './main/context/SocketContext.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  // <React.StrictMode>
  <SocketProvider>
    <ThemeProvider>
      <GlobalStyles>
        <App />
      </GlobalStyles>
    </ThemeProvider>
    </SocketProvider>
  // </React.StrictMode>
)
