import React from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

import './GlobalStyles.module.scss'

const GlobalStyles = ({ children }) => {
  return React.Children.only(children)
}

export default GlobalStyles
