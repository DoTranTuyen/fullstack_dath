import classNames from 'classnames/bind'
import styles from './Mobile.module.scss'
import Header from './components/Header'
import Footer from './components/Footer'
import { useContext, useEffect } from 'react'
import { ThemeContext } from '../DarkMode/ThemeContext'
import { useParams } from 'react-router-dom'
import { CartProvider } from '../../context/CartContext'
import { AuthProvider } from '../../context/AuthContext'
import CallStaffButton from '../../components/CallStaffButton/CallStaffButton'

const cx = classNames.bind(styles)

const MobileLayout = ({ children }) => {
    const { theme } = useContext(ThemeContext);
    const { lang } = useParams()

    useEffect(() => {
        document.body.setAttribute("data-theme", theme);
    }, [theme]);

    return (
        <AuthProvider>
            <CartProvider>
                <div className={cx("cs-container")} data-theme={theme}>
                    <Header lang={lang} />
                    <div className={cx("cs-container-content")}>
                        {children}
                    </div>
                    <Footer />
                    <CallStaffButton />
                </div>
            </CartProvider>
        </AuthProvider>
    )
}

export default MobileLayout